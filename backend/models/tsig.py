from datetime import datetime

from sqlalchemy import DateTime, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class TSIGKey(Base):
    __tablename__ = "tsig_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    algorithm: Mapped[str] = mapped_column(String(64), default="hmac-sha256", nullable=False)
    secret: Mapped[str] = mapped_column(String(512), nullable=False)
    zones: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    allow_update_zones: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
