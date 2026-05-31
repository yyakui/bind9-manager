from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.security import get_current_user, require_admin
from database import get_db
from models.user import User
from schemas import CommandResult, Message, MonitoringStatus
from services.bind_control import BindControl
from services.monitor_service import collect_status

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/status", response_model=MonitoringStatus)
def status(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    return collect_status(db)


@router.post("/reload", response_model=CommandResult)
def reload_bind(_: Annotated[User, Depends(require_admin)]):
    return BindControl().reload().to_dict()


@router.post("/reconfig", response_model=CommandResult)
def reconfig_bind(_: Annotated[User, Depends(require_admin)]):
    return BindControl().reconfig().to_dict()


@router.post("/zones/{zone}/refresh", response_model=CommandResult)
def refresh_zone(zone: str, _: Annotated[User, Depends(require_admin)]):
    return BindControl().refresh(zone).to_dict()


@router.get("/zones/{zone}/status", response_model=CommandResult)
def zone_status(
    zone: str,
    _: Annotated[User, Depends(get_current_user)],
):
    return BindControl().zonestatus(zone).to_dict()


@router.post("/ack-alerts", response_model=Message)
def ack_alerts(_: Annotated[User, Depends(require_admin)]) -> Message:
    return Message(message="Alerts acknowledged")
