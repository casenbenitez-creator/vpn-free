from __future__ import annotations

import socket
from typing import Optional


def get_default_gateway() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return "0.0.0.0"


def get_adapter_name() -> str:
    return ""
