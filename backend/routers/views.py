from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.security import get_current_user, require_admin
from database import get_db
from models.user import User
from models.view import DNSView
from models.zone import Zone
from schemas import DNSViewCreate, DNSViewRead, DNSViewUpdate, Message
from services.bind_config import write_named_conf

router = APIRouter(prefix="/views", tags=["views"])


def get_view_or_404(db: Session, view_id: int) -> DNSView:
    view = db.get(DNSView, view_id)
    if not view:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="View not found")
    return view


def to_read(db: Session, view: DNSView) -> DNSViewRead:
    data = DNSViewRead.model_validate(view)
    data.zone_count = db.query(Zone).filter(Zone.view_id == view.id).count()
    return data


@router.get("", response_model=list[DNSViewRead])
def list_views(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> list[DNSViewRead]:
    views = db.query(DNSView).order_by(DNSView.sort_order, DNSView.name).all()
    return [to_read(db, view) for view in views]


@router.post("", response_model=DNSViewRead, status_code=status.HTTP_201_CREATED)
def create_view(
    payload: DNSViewCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
) -> DNSViewRead:
    view = DNSView(**payload.model_dump())
    db.add(view)
    db.commit()
    db.refresh(view)
    write_named_conf(db)
    return to_read(db, view)


@router.put("/{view_id}", response_model=DNSViewRead)
def update_view(
    view_id: int,
    payload: DNSViewUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
) -> DNSViewRead:
    view = get_view_or_404(db, view_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(view, field, value)
    db.commit()
    db.refresh(view)
    write_named_conf(db)
    return to_read(db, view)


@router.delete("/{view_id}", response_model=Message)
def delete_view(
    view_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
) -> Message:
    view = get_view_or_404(db, view_id)
    if db.query(Zone).filter(Zone.view_id == view.id).count():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="View still has zones")
    db.delete(view)
    db.commit()
    write_named_conf(db)
    return Message(message="View deleted")
