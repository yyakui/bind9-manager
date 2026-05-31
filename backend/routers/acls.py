from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.security import get_current_user, require_admin
from database import get_db
from models.acl import ACL
from models.options import GlobalOptions
from models.user import User
from models.view import DNSView
from models.zone import Zone
from schemas import ACLCreate, ACLRead, ACLUpdate, Message
from services.bind_config import write_named_conf

router = APIRouter(prefix="/acls", tags=["acls"])


def acl_references(db: Session, acl_name: str) -> int:
    count = 0
    zones = db.query(Zone).all()
    for zone in zones:
        count += int(acl_name in zone.allow_transfer)
        count += int(acl_name in zone.allow_update)
    views = db.query(DNSView).all()
    for view in views:
        count += int(acl_name in view.match_clients)
    options = db.query(GlobalOptions).first()
    if options:
        count += int(acl_name in options.allow_query)
        count += int(acl_name in options.allow_recursion)
    return count


def to_read(db: Session, acl: ACL) -> ACLRead:
    data = ACLRead.model_validate(acl)
    data.references = acl_references(db, acl.name)
    return data


def get_acl_or_404(db: Session, acl_id: int) -> ACL:
    acl = db.get(ACL, acl_id)
    if not acl:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ACL not found")
    return acl


@router.get("", response_model=list[ACLRead])
def list_acls(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> list[ACLRead]:
    return [to_read(db, acl) for acl in db.query(ACL).order_by(ACL.name).all()]


@router.post("", response_model=ACLRead, status_code=status.HTTP_201_CREATED)
def create_acl(
    payload: ACLCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
) -> ACLRead:
    acl = ACL(**payload.model_dump())
    db.add(acl)
    db.commit()
    db.refresh(acl)
    write_named_conf(db)
    return to_read(db, acl)


@router.put("/{acl_id}", response_model=ACLRead)
def update_acl(
    acl_id: int,
    payload: ACLUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
) -> ACLRead:
    acl = get_acl_or_404(db, acl_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(acl, field, value)
    db.commit()
    db.refresh(acl)
    write_named_conf(db)
    return to_read(db, acl)


@router.delete("/{acl_id}", response_model=Message)
def delete_acl(
    acl_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
) -> Message:
    acl = get_acl_or_404(db, acl_id)
    refs = acl_references(db, acl.name)
    if refs:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"ACL is referenced {refs} times")
    db.delete(acl)
    db.commit()
    write_named_conf(db)
    return Message(message="ACL deleted")
