import shutil
import tarfile
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from core.config import get_settings
from models.backup import BackupHistory


def _timestamp() -> str:
    return datetime.utcnow().strftime("%Y%m%d%H%M%S")


def create_backup(db: Session, operator: str, summary: str) -> BackupHistory:
    settings = get_settings()
    settings.backup_dir.mkdir(parents=True, exist_ok=True)
    archive_path = settings.backup_dir / f"backup-{_timestamp()}.tar.gz"

    with tarfile.open(archive_path, "w:gz") as archive:
        if settings.bind_conf_path.exists():
            archive.add(settings.bind_conf_path, arcname="named.conf")
        if settings.generated_conf_path.exists():
            archive.add(settings.generated_conf_path, arcname="generated/named.conf")
        if settings.bind_zones_dir.exists():
            archive.add(settings.bind_zones_dir, arcname="zones")

    backup = BackupHistory(operator=operator, summary=summary, archive_path=str(archive_path))
    db.add(backup)
    db.commit()
    db.refresh(backup)
    prune_backups(db)
    return backup


def list_backups(db: Session) -> list[BackupHistory]:
    return db.query(BackupHistory).order_by(BackupHistory.created_at.desc()).all()


def prune_backups(db: Session, keep: int = 50) -> None:
    backups = db.query(BackupHistory).order_by(BackupHistory.created_at.desc()).all()
    for backup in backups[keep:]:
        path = Path(backup.archive_path)
        if path.exists():
            path.unlink()
        db.delete(backup)
    db.commit()


def rollback_backup(db: Session, backup_id: int) -> BackupHistory:
    settings = get_settings()
    backup = db.get(BackupHistory, backup_id)
    if not backup:
        raise FileNotFoundError(f"Backup {backup_id} does not exist")

    archive_path = Path(backup.archive_path)
    if not archive_path.exists():
        raise FileNotFoundError(str(archive_path))

    restore_root = settings.backup_dir / f"restore-{backup_id}-{_timestamp()}"
    restore_root.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path, "r:gz") as archive:
        archive.extractall(restore_root)

    named_conf = restore_root / "named.conf"
    if named_conf.exists():
        settings.bind_conf_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(named_conf, settings.bind_conf_path)

    generated_conf = restore_root / "generated" / "named.conf"
    if generated_conf.exists():
        settings.generated_conf_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(generated_conf, settings.generated_conf_path)

    zones = restore_root / "zones"
    if zones.exists():
        settings.bind_zones_dir.mkdir(parents=True, exist_ok=True)
        for item in zones.iterdir():
            target = settings.bind_zones_dir / item.name
            if item.is_dir():
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(item, target)
            else:
                shutil.copy2(item, target)

    return backup
