import json
from contextlib import asynccontextmanager
from difflib import unified_diff
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt

from core.config import get_settings
from core.security import ensure_default_admin
from database import SessionLocal, init_db
from models.audit import AuditLog
from routers import acls, audit, auth, backup, dnssec, monitoring, options, records, replication, tsig, views, zones
from services.backup_service import create_backup
from services.bind_config import get_or_create_options
from services.monitor_service import MonitorService


settings = get_settings()
monitor_service = MonitorService()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    settings.backup_dir.mkdir(parents=True, exist_ok=True)
    settings.generated_conf_path.parent.mkdir(parents=True, exist_ok=True)
    db = SessionLocal()
    try:
        ensure_default_admin(db)
        get_or_create_options(db)
    finally:
        db.close()
    monitor_service.start()
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _decode_username(request: Request) -> str | None:
    auth_header = request.headers.get("authorization", "")
    if not auth_header.lower().startswith("bearer "):
        return None
    token = auth_header.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None
    return payload.get("sub")


def _infer_object_type(path: str) -> str | None:
    parts = [part for part in path.split("/") if part]
    if len(parts) >= 2 and parts[0] == "api":
        return parts[1]
    return parts[0] if parts else None


def _body_text(body: bytes) -> str | None:
    if not body:
        return None
    text = body.decode("utf-8", errors="replace")
    if len(text) > 8000:
        return text[:8000] + "... truncated"
    return text


def _diff(before: str | None, after: str | None) -> str | None:
    if not before and not after:
        return None
    left = (before or "").splitlines(keepends=True)
    right = (after or "").splitlines(keepends=True)
    return "".join(unified_diff(left, right, fromfile="before", tofile="after", lineterm=""))


@app.middleware("http")
async def audit_and_backup_middleware(request: Request, call_next):
    body = await request.body()

    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    request._receive = receive
    write_method = request.method in {"POST", "PUT", "PATCH", "DELETE"}
    skip_backup = request.url.path.startswith("/api/auth") or request.url.path.startswith("/docs")
    username = _decode_username(request) or "anonymous"

    if write_method and settings.auto_backup_before_writes and not skip_backup:
        db = SessionLocal()
        try:
            create_backup(db, username, f"before {request.method} {request.url.path}")
        finally:
            db.close()

    response = await call_next(request)

    if write_method:
        db = SessionLocal()
        try:
            payload = _body_text(body)
            audit = AuditLog(
                username=username,
                client_ip=request.client.host if request.client else None,
                method=request.method,
                path=request.url.path,
                action=request.method.lower(),
                object_type=_infer_object_type(request.url.path),
                object_id=request.path_params.get("zone_id") or request.path_params.get("record_id"),
                status_code=response.status_code,
                before=None,
                after=payload,
                diff=_diff(None, payload),
            )
            db.add(audit)
            db.commit()
        finally:
            db.close()
    return response


app.include_router(auth.router, prefix="/api")
app.include_router(zones.router, prefix="/api")
app.include_router(records.router, prefix="/api")
app.include_router(acls.router, prefix="/api")
app.include_router(views.router, prefix="/api")
app.include_router(options.router, prefix="/api")
app.include_router(backup.router, prefix="/api")
app.include_router(monitoring.router, prefix="/api")
app.include_router(replication.router, prefix="/api")
app.include_router(audit.router, prefix="/api")
app.include_router(tsig.router, prefix="/api")
app.include_router(dnssec.router, prefix="/api")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "app": settings.app_name}
