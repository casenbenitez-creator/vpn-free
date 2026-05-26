from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from vpn_speed_selector.core.scraper import ServerInfo


_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_RANKING_PATH = _PROJECT_ROOT / "data" / "ranking.json"


def _load_weights() -> dict[str, float]:
    if _RANKING_PATH.exists():
        with open(_RANKING_PATH, encoding="utf-8") as fh:
            data = json.load(fh)
        return data.get("weights", {})
    return {"ping": 0.60, "uptime": 0.25, "site_ping": 0.15}


def rank_servers(servers: list[ServerInfo]) -> list[ServerInfo]:
    weights = _load_weights()

    ping_vals = [s.actual_ping_ms or 9999 for s in servers if s.actual_ping_ms is not None]
    uptime_vals = [s.uptime_days for s in servers]
    site_vals = [s.site_ping_ms for s in servers]

    ping_max = max(ping_vals) if ping_vals else 1
    uptime_max = max(uptime_vals) if uptime_vals else 1
    site_max = max(site_vals) if site_vals else 1

    if ping_max == 0:
        ping_max = 1
    if uptime_max == 0:
        uptime_max = 1
    if site_max == 0:
        site_max = 1

    for s in servers:
        ping_score = 1.0 - ((s.actual_ping_ms or 9999) / ping_max)
        uptime_score = s.uptime_days / uptime_max
        site_score = 1.0 - (s.site_ping_ms / site_max)

        s.score = round(
            ping_score * weights.get("ping", 0.60)
            + uptime_score * weights.get("uptime", 0.25)
            + site_score * weights.get("site_ping", 0.15),
            1,
        )

    servers.sort(key=lambda s: s.score, reverse=True)
    return servers
