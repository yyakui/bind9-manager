from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="BIND9_MANAGER_",
        env_file=".env",
        extra="ignore",
    )

    app_name: str = "BIND9 Manager"
    database_url: str = "sqlite:///./bind9_manager.db"
    secret_key: str = "change-this-secret-before-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    default_admin_username: str = "admin"
    default_admin_password: str = "change-me-now"

    bind_conf_path: Path = Path("/etc/bind/named.conf")
    bind_zones_dir: Path = Path("/etc/bind/zones")
    generated_conf_path: Path = Path("/var/lib/bind9-manager/generated/named.conf")
    backup_dir: Path = Path("/var/lib/bind9-manager/backups")
    audit_append_only: bool = True

    rndc_command: str = "rndc"
    dig_command: str = "dig"
    named_process_name: str = "named"
    monitor_interval_seconds: int = 60
    auto_backup_before_writes: bool = True

    alert_webhook_url: str | None = None
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None
    smtp_to: str | None = None

    cors_origins: list[str] = Field(default_factory=lambda: ["*"])


@lru_cache
def get_settings() -> Settings:
    return Settings()
