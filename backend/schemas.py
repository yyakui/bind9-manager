from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: str
    created_at: datetime


class RecordBase(BaseModel):
    name: str
    record_type: str = Field(..., examples=["A", "AAAA", "CNAME", "MX", "TXT", "NS", "PTR", "SRV", "CAA", "NAPTR"])
    value: str
    ttl: int | None = None
    priority: int | None = None
    weight: int | None = None
    port: int | None = None
    comment: str | None = None


class RecordCreate(RecordBase):
    pass


class RecordUpdate(BaseModel):
    name: str | None = None
    record_type: str | None = None
    value: str | None = None
    ttl: int | None = None
    priority: int | None = None
    weight: int | None = None
    port: int | None = None
    comment: str | None = None


class RecordRead(RecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    zone_id: int
    created_at: datetime
    updated_at: datetime


class ZoneBase(BaseModel):
    name: str
    zone_type: str = Field("master", examples=["master", "slave", "forward", "hint"])
    view_id: int | None = None
    file_path: str | None = None
    ttl: int = 3600
    primary_ns: str = "ns1.example.com."
    admin_email: str = "hostmaster.example.com."
    serial: int = 2025010101
    refresh: int = 3600
    retry: int = 900
    expire: int = 1209600
    minimum_ttl: int = 300
    allow_transfer: list[str] = Field(default_factory=list)
    allow_update: list[str] = Field(default_factory=list)
    masters: list[str] = Field(default_factory=list)
    forwarders: list[str] = Field(default_factory=list)


class ZoneCreate(ZoneBase):
    records: list[RecordCreate] = Field(default_factory=list)


class ZoneUpdate(BaseModel):
    name: str | None = None
    zone_type: str | None = None
    view_id: int | None = None
    file_path: str | None = None
    ttl: int | None = None
    primary_ns: str | None = None
    admin_email: str | None = None
    serial: int | None = None
    refresh: int | None = None
    retry: int | None = None
    expire: int | None = None
    minimum_ttl: int | None = None
    allow_transfer: list[str] | None = None
    allow_update: list[str] | None = None
    masters: list[str] | None = None
    forwarders: list[str] | None = None
    is_dnssec_signed: bool | None = None


class ZoneRead(ZoneBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_dnssec_signed: bool
    created_at: datetime
    updated_at: datetime
    records: list[RecordRead] = Field(default_factory=list)


class ACLBase(BaseModel):
    name: str
    entries: list[str] = Field(default_factory=list)


class ACLCreate(ACLBase):
    pass


class ACLUpdate(BaseModel):
    name: str | None = None
    entries: list[str] | None = None


class ACLRead(ACLBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    references: int = 0


class DNSViewBase(BaseModel):
    name: str
    match_clients: list[str] = Field(default_factory=list)
    recursion: bool = True
    sort_order: int = 100


class DNSViewCreate(DNSViewBase):
    pass


class DNSViewUpdate(BaseModel):
    name: str | None = None
    match_clients: list[str] | None = None
    recursion: bool | None = None
    sort_order: int | None = None


class DNSViewRead(DNSViewBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    zone_count: int = 0


class OptionsUpdate(BaseModel):
    listen_on: list[str] | None = None
    listen_on_v6: list[str] | None = None
    forwarders: list[str] | None = None
    forward_mode: str | None = None
    recursion: bool | None = None
    allow_query: list[str] | None = None
    allow_recursion: list[str] | None = None
    dnssec_validation: str | None = None
    rate_limit: dict[str, Any] | None = None
    response_policy: list[str] | None = None
    logging_channels: dict[str, Any] | None = None
    logging_categories: dict[str, Any] | None = None


class OptionsRead(OptionsUpdate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    listen_on: list[str]
    listen_on_v6: list[str]
    forwarders: list[str]
    forward_mode: str
    recursion: bool
    allow_query: list[str]
    allow_recursion: list[str]
    dnssec_validation: str
    rate_limit: dict[str, Any]
    response_policy: list[str]
    logging_channels: dict[str, Any]
    logging_categories: dict[str, Any]
    updated_at: datetime


class BackupRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    operator: str
    summary: str
    archive_path: str


class AuditRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    username: str | None
    client_ip: str | None
    method: str
    path: str
    action: str
    object_type: str | None
    object_id: str | None
    status_code: int
    before: str | None
    after: str | None
    diff: str | None


class TSIGBase(BaseModel):
    name: str
    algorithm: str = "hmac-sha256"
    zones: list[str] = Field(default_factory=list)
    allow_update_zones: list[str] = Field(default_factory=list)


class TSIGCreate(TSIGBase):
    secret: str | None = None


class TSIGRead(TSIGBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    secret: str
    created_at: datetime


class DNSSECKeyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    zone_id: int
    key_type: str
    algorithm: str
    key_tag: str | None
    path: str | None
    active: bool
    created_at: datetime


class MonitoringStatus(BaseModel):
    generated_at: datetime
    named_running: bool
    rndc_status: dict[str, Any]
    zones: list[dict[str, Any]]
    query_latency_ms: float | None = None
    alerts: list[str] = Field(default_factory=list)


class CommandResult(BaseModel):
    command: list[str]
    returncode: int
    stdout: str
    stderr: str
    ok: bool


class Message(BaseModel):
    message: str
