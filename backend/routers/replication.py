from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.security import get_current_user, require_admin
from database import get_db
from models.user import User
from models.zone import Zone
from schemas import CommandResult
from services.bind_control import BindControl

router = APIRouter(prefix="/replication", tags=["replication"])


@router.get("/status")
def replication_status(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    control = BindControl()
    zones = db.query(Zone).filter(Zone.zone_type.in_(["master", "slave"])).order_by(Zone.name).all()
    return [
        {
            "zone": zone.name,
            "type": zone.zone_type,
            "masters": zone.masters,
            "allow_transfer": zone.allow_transfer,
            "status": control.zonestatus(zone.name).to_dict(),
        }
        for zone in zones
    ]


@router.post("/zones/{zone}/refresh", response_model=CommandResult)
def refresh_secondary(zone: str, _: Annotated[User, Depends(require_admin)]):
    return BindControl().refresh(zone).to_dict()
