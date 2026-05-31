from pathlib import Path

from sqlalchemy.orm import Session, joinedload

from core.config import get_settings
from models.acl import ACL
from models.options import GlobalOptions
from models.tsig import TSIGKey
from models.view import DNSView
from models.zone import Zone
from services.zone_file import zone_file_path


def _block_values(values: list[str]) -> str:
    if not values:
        return "none;"
    return " ".join(f"{value};" for value in values)


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"


def _acl_block(acl: ACL) -> str:
    return f'acl "{acl.name}" {{ {_block_values(acl.entries)} }};'


def _option_list(name: str, values: list[str]) -> str:
    return f"    {name} {{ {_block_values(values)} }};"


def _render_rate_limit(rate_limit: dict) -> list[str]:
    if not rate_limit:
        return []
    lines = ["    rate-limit {"]
    for key, value in rate_limit.items():
        bind_key = key.replace("_", "-")
        lines.append(f"        {bind_key} {value};")
    lines.append("    };")
    return lines


def _render_logging(options: GlobalOptions) -> str:
    if not options.logging_channels and not options.logging_categories:
        return ""
    lines = ["logging {"]
    for name, value in options.logging_channels.items():
        destination = value.get("destination", "syslog") if isinstance(value, dict) else "syslog"
        severity = value.get("severity", "info") if isinstance(value, dict) else "info"
        lines.append(f'    channel "{name}" {{ {destination}; severity {severity}; }};')
    for category, channels in options.logging_categories.items():
        if isinstance(channels, str):
            channels = [channels]
        channel_list = " ".join(f'"{channel}";' for channel in channels)
        lines.append(f"    category {category} {{ {channel_list} }};")
    lines.append("};")
    return "\n".join(lines)


def get_or_create_options(db: Session) -> GlobalOptions:
    options = db.query(GlobalOptions).first()
    if options:
        return options
    options = GlobalOptions()
    db.add(options)
    db.commit()
    db.refresh(options)
    return options


def render_options(options: GlobalOptions) -> str:
    lines = [
        "options {",
        '    directory "/var/cache/bind";',
        _option_list("listen-on", options.listen_on),
        _option_list("listen-on-v6", options.listen_on_v6),
        f"    recursion {_yes_no(options.recursion)};",
        _option_list("allow-query", options.allow_query),
        _option_list("allow-recursion", options.allow_recursion),
        f"    dnssec-validation {options.dnssec_validation};",
    ]
    if options.forwarders:
        lines.append(_option_list("forwarders", options.forwarders))
        lines.append(f"    forward {options.forward_mode};")
    for rpz in options.response_policy:
        lines.append(f'    response-policy {{ zone "{rpz}"; }};')
    lines.extend(_render_rate_limit(options.rate_limit))
    lines.append("};")
    return "\n".join(lines)


def render_tsig_key(key: TSIGKey) -> str:
    return "\n".join(
        [
            f'key "{key.name}" {{',
            f"    algorithm {key.algorithm};",
            f'    secret "{key.secret}";',
            "};",
        ]
    )


def render_zone(zone: Zone, indent: str = "") -> str:
    zone_type = zone.zone_type.lower()
    lines = [
        f'{indent}zone "{zone.name}" {{',
        f"{indent}    type {zone_type};",
    ]
    if zone_type in {"master", "hint"}:
        lines.append(f'{indent}    file "{zone_file_path(zone)}";')
    if zone_type == "slave" and zone.masters:
        lines.append(f"{indent}    masters {{ {_block_values(zone.masters)} }};")
        lines.append(f'{indent}    file "{zone_file_path(zone)}";')
    if zone_type == "forward" and zone.forwarders:
        lines.append(f"{indent}    forwarders {{ {_block_values(zone.forwarders)} }};")
        lines.append(f"{indent}    forward first;")
    if zone.allow_transfer:
        lines.append(f"{indent}    allow-transfer {{ {_block_values(zone.allow_transfer)} }};")
    if zone.allow_update:
        lines.append(f"{indent}    allow-update {{ {_block_values(zone.allow_update)} }};")
    lines.append(f"{indent}}};")
    return "\n".join(lines)


def render_view(view: DNSView, zones: list[Zone]) -> str:
    lines = [
        f'view "{view.name}" {{',
        f"    match-clients {{ {_block_values(view.match_clients)} }};",
        f"    recursion {_yes_no(view.recursion)};",
    ]
    lines.extend(render_zone(zone, indent="    ") for zone in zones)
    lines.append("};")
    return "\n".join(lines)


def render_named_conf(db: Session) -> str:
    options = get_or_create_options(db)
    acls = db.query(ACL).order_by(ACL.name).all()
    keys = db.query(TSIGKey).order_by(TSIGKey.name).all()
    views = db.query(DNSView).order_by(DNSView.sort_order, DNSView.name).all()
    zones = db.query(Zone).options(joinedload(Zone.records)).order_by(Zone.name).all()

    parts = [
        "// Generated by bind9-manager. Edit through the Web UI.",
        render_options(options),
    ]
    parts.extend(_acl_block(acl) for acl in acls)
    parts.extend(render_tsig_key(key) for key in keys)
    logging = _render_logging(options)
    if logging:
        parts.append(logging)

    if views:
        for view in views:
            parts.append(render_view(view, [zone for zone in zones if zone.view_id == view.id]))
        unassigned = [zone for zone in zones if zone.view_id is None]
        if unassigned:
            default_view = DNSView(name="default", match_clients=["any"], recursion=options.recursion, sort_order=999)
            parts.append(render_view(default_view, unassigned))
    else:
        parts.extend(render_zone(zone) for zone in zones)

    return "\n\n".join(part for part in parts if part).strip() + "\n"


def write_named_conf(db: Session, path: Path | None = None) -> Path:
    settings = get_settings()
    target = path or settings.generated_conf_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_named_conf(db), encoding="utf-8")
    return target
