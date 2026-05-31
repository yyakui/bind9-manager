from pathlib import Path

import dns.rdatatype
import dns.zone

from core.config import get_settings
from models.zone import Record, Zone


SUPPORTED_RECORD_TYPES = {"A", "AAAA", "CNAME", "MX", "TXT", "NS", "PTR", "SRV", "CAA", "NAPTR"}


def fqdn(value: str) -> str:
    if value == "@":
        return value
    return value if value.endswith(".") else f"{value}."


def zone_file_path(zone: Zone) -> Path:
    settings = get_settings()
    if zone.file_path:
        return Path(zone.file_path)
    safe_name = zone.name.rstrip(".").replace("/", "_")
    return settings.bind_zones_dir / f"{safe_name}.db"


def bump_serial(zone: Zone) -> None:
    zone.serial = int(zone.serial or 0) + 1


def render_record(record: Record, default_ttl: int) -> str:
    name = record.name or "@"
    ttl = record.ttl or default_ttl
    record_type = record.record_type.upper()
    value = record.value
    if record_type == "MX":
        value = f"{record.priority or 10} {fqdn(record.value)}"
    elif record_type == "SRV":
        value = f"{record.priority or 0} {record.weight or 0} {record.port or 0} {fqdn(record.value)}"
    elif record_type == "TXT" and not (value.startswith('"') and value.endswith('"')):
        value = '"' + value.replace('"', '\\"') + '"'
    elif record_type in {"CNAME", "NS", "PTR"}:
        value = fqdn(value)
    return f"{name:<28} {ttl:<8} IN {record_type:<8} {value}"


def render_zone_file(zone: Zone) -> str:
    lines = [
        f"$ORIGIN {fqdn(zone.name)}",
        f"$TTL {zone.ttl}",
        "@ IN SOA {primary} {admin} (".format(primary=fqdn(zone.primary_ns), admin=fqdn(zone.admin_email)),
        f"    {zone.serial} ; serial",
        f"    {zone.refresh} ; refresh",
        f"    {zone.retry} ; retry",
        f"    {zone.expire} ; expire",
        f"    {zone.minimum_ttl} ; minimum",
        ")",
        "",
    ]
    if not any(record.record_type.upper() == "NS" for record in zone.records):
        lines.append(f"@                            {zone.ttl:<8} IN NS       {fqdn(zone.primary_ns)}")
    lines.extend(render_record(record, zone.ttl) for record in zone.records)
    lines.append("")
    return "\n".join(lines)


def write_zone_file(zone: Zone) -> Path:
    path = zone_file_path(zone)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_zone_file(zone), encoding="utf-8")
    return path


def export_zone_file(zone: Zone) -> str:
    return render_zone_file(zone)


def parse_zone_text(zone_name: str, text: str) -> list[dict]:
    origin = fqdn(zone_name)
    parsed = dns.zone.from_text(text, origin=origin, relativize=False, check_origin=False)
    records: list[dict] = []
    for name, node in parsed.nodes.items():
        owner = "@" if str(name) == origin else str(name).removesuffix(f".{origin}").rstrip(".")
        for rdataset in node.rdatasets:
            record_type = dns.rdatatype.to_text(rdataset.rdtype)
            if record_type == "SOA" or record_type not in SUPPORTED_RECORD_TYPES:
                continue
            for item in rdataset.items:
                value = item.to_text()
                payload = {
                    "name": owner or "@",
                    "record_type": record_type,
                    "value": value,
                    "ttl": rdataset.ttl,
                }
                if record_type == "MX":
                    payload["priority"] = getattr(item, "preference", None)
                    payload["value"] = str(getattr(item, "exchange", value)).rstrip(".")
                elif record_type == "SRV":
                    payload["priority"] = getattr(item, "priority", None)
                    payload["weight"] = getattr(item, "weight", None)
                    payload["port"] = getattr(item, "port", None)
                    payload["value"] = str(getattr(item, "target", value)).rstrip(".")
                records.append(payload)
    return records
