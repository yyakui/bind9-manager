from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session, joinedload

from core.security import get_current_user, require_admin
from database import get_db
from models.user import User
from models.zone import Record, Zone
from schemas import Message, RecordCreate, ZoneCreate, ZoneRead, ZoneUpdate
from services.bind_config import write_named_conf
from services.zone_file import bump_serial, export_zone_file, parse_zone_text, write_zone_file

router = APIRouter(prefix="/zones", tags=["zones"])


def get_zone_or_404(db: Session, zone_id: int) -> Zone:
    zone = db.query(Zone).options(joinedload(Zone.records)).filter(Zone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")
    return zone


def persist_generated_files(db: Session, zone: Zone | None = None) -> None:
    if zone and zone.zone_type in {"master", "hint"}:
        write_zone_file(zone)
    write_named_conf(db)


@router.get("", response_model=list[ZoneRead])
def list_zones(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> list[Zone]:
    return db.query(Zone).options(joinedload(Zone.records)).order_by(Zone.name).all()


@router.post("", response_model=ZoneRead, status_code=status.HTTP_201_CREATED)
def create_zone(
    payload: ZoneCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
) -> Zone:
    existing = db.query(Zone).filter(Zone.name == payload.name, Zone.view_id == payload.view_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Zone already exists in this view")
    data = payload.model_dump(exclude={"records"})
    zone = Zone(**data)
    zone.records = [Record(**record.model_dump()) for record in payload.records]
    db.add(zone)
    db.commit()
    db.refresh(zone)
    persist_generated_files(db, zone)
    return get_zone_or_404(db, zone.id)


@router.get("/{zone_id}", response_model=ZoneRead)
def get_zone(
    zone_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> Zone:
    return get_zone_or_404(db, zone_id)


@router.put("/{zone_id}", response_model=ZoneRead)
def update_zone(
    zone_id: int,
    payload: ZoneUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
) -> Zone:
    zone = get_zone_or_404(db, zone_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(zone, field, value)
    db.commit()
    db.refresh(zone)
    persist_generated_files(db, zone)
    return get_zone_or_404(db, zone.id)


@router.delete("/{zone_id}", response_model=Message)
def delete_zone(
    zone_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
) -> Message:
    zone = get_zone_or_404(db, zone_id)
    db.delete(zone)
    db.commit()
    write_named_conf(db)
    return Message(message="Zone deleted")


@router.get("/{zone_id}/export")
def export_zone(
    zone_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> Response:
    zone = get_zone_or_404(db, zone_id)
    return Response(
        content=export_zone_file(zone),
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="{zone.name}.db"'},
    )


@router.post("/{zone_id}/import", response_model=ZoneRead)
def import_records(
    zone_id: int,
    body: Annotated[str, Body(media_type="text/plain")],
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
) -> Zone:
    zone = get_zone_or_404(db, zone_id)
    records = parse_zone_text(zone.name, body)
    zone.records.clear()
    zone.records.extend(Record(**RecordCreate(**record).model_dump()) for record in records)
    bump_serial(zone)
    db.commit()
    db.refresh(zone)
    persist_generated_files(db, zone)
    return get_zone_or_404(db, zone.id)


@router.post("/{zone_id}/write-files", response_model=Message)
def write_files(
    zone_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
) -> Message:
    zone = get_zone_or_404(db, zone_id)
    persist_generated_files(db, zone)
    return Message(message="BIND configuration files generated")
