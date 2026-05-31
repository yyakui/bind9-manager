from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class GlobalOptions(Base):
    __tablename__ = "global_options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    listen_on: Mapped[list[str]] = mapped_column(JSON, default=lambda: ["any"], nullable=False)
    listen_on_v6: Mapped[list[str]] = mapped_column(JSON, default=lambda: ["any"], nullable=False)
    forwarders: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    forward_mode: Mapped[str] = mapped_column(String(32), default="first", nullable=False)
    recursion: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    allow_query: Mapped[list[str]] = mapped_column(JSON, default=lambda: ["any"], nullable=False)
    allow_recursion: Mapped[list[str]] = mapped_column(JSON, default=lambda: ["localhost", "localnets"], nullable=False)
    dnssec_validation: Mapped[str] = mapped_column(String(16), default="auto", nullable=False)
    rate_limit: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    response_policy: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    logging_channels: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    logging_categories: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
