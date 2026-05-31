from pathlib import Path

from sqlalchemy.orm import Session

from models.dnssec import DNSSECKey
from models.zone import Zone
from services.bind_control import BindControl
from services.zone_file import write_zone_file


def generate_zone_key(db: Session, zone: Zone, key_type: str, algorithm: str = "ECDSAP256SHA256") -> tuple[DNSSECKey, dict]:
    flag = "257" if key_type.upper() == "KSK" else "256"
    zone_file = write_zone_file(zone)
    command = ["dnssec-keygen", "-a", algorithm, "-f", "KSK" if flag == "257" else "", "-n", "ZONE", zone.name]
    command = [item for item in command if item]
    result = BindControl().run(command, cwd=zone_file.parent, timeout=60).to_dict()
    key = DNSSECKey(zone_id=zone.id, key_type=key_type.upper(), algorithm=algorithm, path=str(zone_file.parent), active=result["ok"])
    db.add(key)
    db.commit()
    db.refresh(key)
    return key, result


def sign_zone(db: Session, zone: Zone) -> dict:
    zone_file = write_zone_file(zone)
    result = BindControl().run(["dnssec-signzone", "-o", zone.name, str(zone_file)], cwd=Path(zone_file).parent, timeout=120).to_dict()
    if result["ok"]:
        zone.is_dnssec_signed = True
        db.commit()
    return result


def unsign_zone(db: Session, zone: Zone) -> Zone:
    zone.is_dnssec_signed = False
    db.commit()
    db.refresh(zone)
    return zone
