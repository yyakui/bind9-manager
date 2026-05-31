from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.security import get_current_user, require_admin
from database import get_db
from models.user import User
from schemas import OptionsRead, OptionsUpdate
from services.bind_config import get_or_create_options, write_named_conf

router = APIRouter(prefix="/options", tags=["options"])


@router.get("", response_model=OptionsRead)
def get_options(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    return get_or_create_options(db)


@router.put("", response_model=OptionsRead)
def update_options(
    payload: OptionsUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
):
    options = get_or_create_options(db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(options, field, value)
    db.commit()
    db.refresh(options)
    write_named_conf(db)
    return options
