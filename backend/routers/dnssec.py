from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.security import get_current_user, require_admin
from database import get_db
from models.dnssec import DNSSECKey
from models.user import User
from models.zone import Zone
from schemas import CommandResult, DNSSECKeyRead, Message, ZoneRead
from services.dnssec_service import generate_zone_key, sign_zone, unsign_zone

router = APIRouter(prefix="/dnssec", tags=["dnssec"])


def get_zone_or_404(db: Session, zone_id: int) -> Zone:
    zone = db.get(Zone, zone_id)
    if not zone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")
    return zone


@router.get("/keys", response_model=list[DNSSECKeyRead])
def list_keys(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    return db.query(DNSSECKey).order_by(DNSSECKey.created_at.desc()).all()


@router.post("/zones/{zone_id}/keys/{key_type}", response_model=DNSSECKeyRead, status_code=status.HTTP_201_CREATED)
def create_key(
    zone_id: int,
    key_type: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
):
    zone = get_zone_or_404(db, zone_id)
    key, _ = generate_zone_key(db, zone, key_type)
    return key


@router.post("/zones/{zone_id}/sign", response_model=CommandResult)
def sign(
    zone_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
):
    return sign_zone(db, get_zone_or_404(db, zone_id))


@router.post("/zones/{zone_id}/unsign", response_model=ZoneRead)
def unsign(
    zone_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
):
    return unsign_zone(db, get_zone_or_404(db, zone_id))


@router.get("/zones/{zone_id}/ds", response_model=Message)
def export_ds(
    zone_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> Message:
    zone = get_zone_or_404(db, zone_id)
    return Message(message=f"Run dnssec-dsfromkey for signed keys under zone path for {zone.name}")
