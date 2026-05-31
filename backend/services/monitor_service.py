import asyncio
import json
import subprocess
import time
import urllib.request
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from core.config import get_settings
from database import SessionLocal
from models.zone import Zone
from services.bind_control import BindControl


def _process_running(name: str) -> bool:
    try:
        completed = subprocess.run(["pgrep", "-x", name], capture_output=True, text=True, timeout=3, check=False)
        return completed.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _query_latency_ms() -> float | None:
    settings = get_settings()
    command = [settings.dig_command, "@127.0.0.1", ".", "SOA", "+time=2", "+tries=1", "+short"]
    start = time.monotonic()
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=4, check=False)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0:
        return None
    return round((time.monotonic() - start) * 1000, 2)


def collect_status(db: Session) -> dict[str, Any]:
    settings = get_settings()
    control = BindControl()
    rndc_status = control.status().to_dict()
    named_running = _process_running(settings.named_process_name) or rndc_status["ok"]
    zone_statuses = []
    alerts = []
    if not named_running:
        alerts.append("named process is not running or rndc status failed")
    for zone in db.query(Zone).order_by(Zone.name).all():
        status = control.zonestatus(zone.name).to_dict()
        if not status["ok"]:
            alerts.append(f"zone {zone.name} status check failed")
        zone_statuses.append({"zone": zone.name, "type": zone.zone_type, "status": status})
    status = {
        "generated_at": datetime.utcnow(),
        "named_running": named_running,
        "rndc_status": rndc_status,
        "zones": zone_statuses,
        "query_latency_ms": _query_latency_ms(),
        "alerts": alerts,
    }
    return status


def send_webhook_alert(alerts: list[str]) -> None:
    settings = get_settings()
    if not settings.alert_webhook_url or not alerts:
        return
    body = json.dumps({"title": "BIND9 Manager Alert", "alerts": alerts}).encode("utf-8")
    request = urllib.request.Request(
        settings.alert_webhook_url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(request, timeout=5).close()
    except OSError:
        pass


class MonitorService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.last_status: dict[str, Any] | None = None
        self._task: asyncio.Task | None = None

    def start(self) -> None:
        if self._task and not self._task.done():
            return
        self._task = asyncio.create_task(self._run())

    async def _run(self) -> None:
        while True:
            db = SessionLocal()
            try:
                self.last_status = collect_status(db)
                send_webhook_alert(self.last_status.get("alerts", []))
            finally:
                db.close()
            await asyncio.sleep(self.settings.monitor_interval_seconds)
