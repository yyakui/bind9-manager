from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.security import get_current_user, require_admin
from database import get_db
from models.tsig import TSIGKey
from models.user import User
from schemas import Message, TSIGCreate, TSIGRead
from services.bind_config import write_named_conf
from services.tsig_service import generate_tsig_secret

router = APIRouter(prefix="/tsig", tags=["tsig"])


@router.get("", response_model=list[TSIGRead])
def list_keys(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    return db.query(TSIGKey).order_by(TSIGKey.name).all()


@router.post("", response_model=TSIGRead, status_code=status.HTTP_201_CREATED)
def create_key(
    payload: TSIGCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
):
    key = TSIGKey(**payload.model_dump(exclude={"secret"}), secret=payload.secret or generate_tsig_secret())
    db.add(key)
    db.commit()
    db.refresh(key)
    write_named_conf(db)
    return key


@router.delete("/{key_id}", response_model=Message)
def delete_key(
    key_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
) -> Message:
    key = db.get(TSIGKey, key_id)
    if not key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TSIG key not found")
    db.delete(key)
    db.commit()
    write_named_conf(db)
    return Message(message="TSIG key deleted")
