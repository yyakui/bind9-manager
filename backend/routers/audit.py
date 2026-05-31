from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.security import get_current_user
from database import get_db
from models.audit import AuditLog
from models.user import User
from schemas import AuditRead

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=list[AuditRead])
def list_audit_logs(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    username: str | None = None,
    object_type: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    limit: int = 200,
) -> list[AuditLog]:
    query = db.query(AuditLog)
    if username:
        query = query.filter(AuditLog.username == username)
    if object_type:
        query = query.filter(AuditLog.object_type == object_type)
    if since:
        query = query.filter(AuditLog.created_at >= since)
    if until:
        query = query.filter(AuditLog.created_at <= until)
    return query.order_by(AuditLog.created_at.desc()).limit(min(limit, 1000)).all()
