import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

from core.config import get_settings


@dataclass
class CommandResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    def to_dict(self) -> dict:
        data = asdict(self)
        data["ok"] = self.ok
        return data


class BindControl:
    def __init__(self) -> None:
        self.settings = get_settings()

    def run(self, command: list[str], timeout: int = 20, cwd: Path | None = None) -> CommandResult:
        try:
            completed = subprocess.run(
                command,
                cwd=str(cwd) if cwd else None,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            return CommandResult(command, completed.returncode, completed.stdout.strip(), completed.stderr.strip())
        except FileNotFoundError as exc:
            return CommandResult(command, 127, "", str(exc))
        except subprocess.TimeoutExpired as exc:
            return CommandResult(command, 124, exc.stdout or "", exc.stderr or "Command timed out")

    def rndc(self, *args: str, timeout: int = 20) -> CommandResult:
        return self.run([self.settings.rndc_command, *args], timeout=timeout)

    def status(self) -> CommandResult:
        return self.rndc("status")

    def reload(self, zone: str | None = None) -> CommandResult:
        return self.rndc("reload", zone) if zone else self.rndc("reload")

    def reconfig(self) -> CommandResult:
        return self.rndc("reconfig")

    def refresh(self, zone: str) -> CommandResult:
        return self.rndc("refresh", zone)

    def zonestatus(self, zone: str) -> CommandResult:
        return self.rndc("zonestatus", zone)

    def checkconf(self, config_path: Path | None = None) -> CommandResult:
        path = config_path or self.settings.generated_conf_path
        return self.run(["named-checkconf", str(path)])

    def checkzone(self, zone: str, zone_file: Path) -> CommandResult:
        return self.run(["named-checkzone", zone, str(zone_file)])
