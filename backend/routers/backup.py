from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.security import get_current_user, require_admin
from database import get_db
from models.user import User
from schemas import BackupRead, Message
from services.backup_service import create_backup, list_backups, rollback_backup

router = APIRouter(prefix="/backups", tags=["backups"])


@router.get("", response_model=list[BackupRead])
def backups(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    return list_backups(db)


@router.post("", response_model=BackupRead, status_code=status.HTTP_201_CREATED)
def create_snapshot(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
):
    return create_backup(db, current_user.username, "manual snapshot")


@router.post("/{backup_id}/rollback", response_model=Message)
def rollback(
    backup_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
) -> Message:
    try:
        rollback_backup(db, backup_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Message(message="Backup restored")
