from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.security import get_current_user, require_admin
from database import get_db
from models.user import User
from models.zone import Record, Zone
from schemas import Message, RecordCreate, RecordRead, RecordUpdate
from services.bind_config import write_named_conf
from services.zone_file import bump_serial, write_zone_file

router = APIRouter(tags=["records"])


def get_record_or_404(db: Session, record_id: int) -> Record:
    record = db.get(Record, record_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return record


def get_zone_or_404(db: Session, zone_id: int) -> Zone:
    zone = db.get(Zone, zone_id)
    if not zone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")
    return zone


def persist_zone(db: Session, zone: Zone) -> None:
    bump_serial(zone)
    db.commit()
    db.refresh(zone)
    write_zone_file(zone)
    write_named_conf(db)


@router.get("/zones/{zone_id}/records", response_model=list[RecordRead])
def list_records(
    zone_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> list[Record]:
    return db.query(Record).filter(Record.zone_id == zone_id).order_by(Record.name, Record.record_type).all()


@router.post("/zones/{zone_id}/records", response_model=RecordRead, status_code=status.HTTP_201_CREATED)
def create_record(
    zone_id: int,
    payload: RecordCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
) -> Record:
    zone = get_zone_or_404(db, zone_id)
    record = Record(zone_id=zone_id, **payload.model_dump())
    record.record_type = record.record_type.upper()
    db.add(record)
    persist_zone(db, zone)
    db.refresh(record)
    return record


@router.put("/records/{record_id}", response_model=RecordRead)
def update_record(
    record_id: int,
    payload: RecordUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
) -> Record:
    record = get_record_or_404(db, record_id)
    zone = record.zone
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, field, value.upper() if field == "record_type" and value else value)
    persist_zone(db, zone)
    db.refresh(record)
    return record


@router.delete("/records/{record_id}", response_model=Message)
def delete_record(
    record_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
) -> Message:
    record = get_record_or_404(db, record_id)
    zone = record.zone
    db.delete(record)
    persist_zone(db, zone)
    return Message(message="Record deleted")
