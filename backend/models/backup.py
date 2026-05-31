from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class BackupHistory(Base):
    __tablename__ = "backup_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    operator: Mapped[str] = mapped_column(String(128), default="system", nullable=False)
    summary: Mapped[str] = mapped_column(String(512), nullable=False)
    archive_path: Mapped[str] = mapped_column(String(1024), nullable=False)
