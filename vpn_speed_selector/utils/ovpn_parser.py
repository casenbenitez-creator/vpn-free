from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class OvpnConfig:
    remote_ip: str
    remote_port: int
    protocol: str
    file_path: Path


def parse_ovpn(file_path: Path) -> Optional[OvpnConfig]:
    if not file_path.exists():
        return None
    try:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None

    remote_ip = ""
    remote_port = 1194
    protocol = "udp"

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("remote "):
            parts = stripped.split()
            if len(parts) >= 2:
                remote_ip = parts[1]
            if len(parts) >= 3:
                try:
                    remote_port = int(parts[2])
                except ValueError:
                    pass
        if stripped.lower().startswith("proto "):
            proto_val = stripped.split()[-1].lower()
            if proto_val in ("udp", "tcp"):
                protocol = proto_val

    if not remote_ip:
        return None

    return OvpnConfig(
        remote_ip=remote_ip,
        remote_port=remote_port,
        protocol=protocol,
        file_path=file_path,
    )
