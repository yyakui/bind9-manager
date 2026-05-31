from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Zone(Base):
    __tablename__ = "zones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    zone_type: Mapped[str] = mapped_column(String(32), default="master", nullable=False)
    view_id: Mapped[int | None] = mapped_column(ForeignKey("dns_views.id"), nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    ttl: Mapped[int] = mapped_column(Integer, default=3600, nullable=False)
    primary_ns: Mapped[str] = mapped_column(String(255), default="ns1.example.com.", nullable=False)
    admin_email: Mapped[str] = mapped_column(String(255), default="hostmaster.example.com.", nullable=False)
    serial: Mapped[int] = mapped_column(Integer, default=2025010101, nullable=False)
    refresh: Mapped[int] = mapped_column(Integer, default=3600, nullable=False)
    retry: Mapped[int] = mapped_column(Integer, default=900, nullable=False)
    expire: Mapped[int] = mapped_column(Integer, default=1209600, nullable=False)
    minimum_ttl: Mapped[int] = mapped_column(Integer, default=300, nullable=False)
    allow_transfer: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    allow_update: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    masters: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    forwarders: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    is_dnssec_signed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    records: Mapped[list["Record"]] = relationship(back_populates="zone", cascade="all, delete-orphan")
    view: Mapped["DNSView | None"] = relationship(back_populates="zones")


class Record(Base):
    __tablename__ = "records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    zone_id: Mapped[int] = mapped_column(ForeignKey("zones.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    record_type: Mapped[str] = mapped_column(String(16), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    ttl: Mapped[int | None] = mapped_column(Integer, nullable=True)
    priority: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weight: Mapped[int | None] = mapped_column(Integer, nullable=True)
    port: Mapped[int | None] = mapped_column(Integer, nullable=True)
    comment: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    zone: Mapped[Zone] = relationship(back_populates="records")
