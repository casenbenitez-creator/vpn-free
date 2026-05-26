from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class ServerInfo:
    country: str
    ip: str
    ovpn_url: str
    uptime_days: int
    site_ping_ms: int
    actual_ping_ms: Optional[int] = None
    score: float = 0.0
    status: str = ""


DUMMY_SERVERS: list[ServerInfo] = [
    ServerInfo("Japan", "124.32.30.64", "https://ipspeed.info/ovpn/124.32.30.64.ovpn", 6, 4, 4, 98.2),
    ServerInfo("Japan", "126.221.31.122", "https://ipspeed.info/ovpn/126.221.31.122.ovpn", 53, 7, 7, 95.1),
    ServerInfo("Japan", "110.163.147.10", "https://ipspeed.info/ovpn/110.163.147.10.ovpn", 11, 9, 9, 91.4),
    ServerInfo("Japan", "219.100.37.117", "https://ipspeed.info/ovpn/219.100.37.117.ovpn", 0, 8, 8, 88.7),
    ServerInfo("Japan", "219.100.37.98", "https://ipspeed.info/ovpn/219.100.37.98.ovpn", 0, 8, 8, 88.7),
    ServerInfo("South Korea", "211.216.167.19", "https://ipspeed.info/ovpn/211.216.167.19.ovpn", 9, 31, 31, 79.3),
    ServerInfo("South Korea", "1.244.119.231", "https://ipspeed.info/ovpn/1.244.119.231.ovpn", 33, 37, 37, 76.1),
    ServerInfo("South Korea", "121.165.121.91", "https://ipspeed.info/ovpn/121.165.121.91.ovpn", 27, 31, 31, 75.8),
    ServerInfo("Germany", "217.144.174.117", "https://ipspeed.info/ovpn/217.144.174.117.ovpn", 8, 69, 69, 62.5),
    ServerInfo("Russian Federation", "212.107.222.59", "https://ipspeed.info/ovpn/212.107.222.59.ovpn", 1, 150, 150, 41.2),
    ServerInfo("Thailand", "184.22.106.160", "https://ipspeed.info/ovpn/184.22.106.160.ovpn", 1, 7, 7, 87.1),
    ServerInfo("Vietnam", "42.118.212.228", "https://ipspeed.info/ovpn/42.118.212.228.ovpn", 10, 23, 23, 82.4),
    ServerInfo("USA", "216.67.58.152", "https://ipspeed.info/ovpn/216.67.58.152.ovpn", 6, 135, 135, 48.9),
    ServerInfo("Grenada", "74.122.88.200", "https://ipspeed.info/ovpn/74.122.88.200.ovpn", 7, 62, 62, 64.1),
    ServerInfo("Japan", "219.100.37.31", "https://ipspeed.info/ovpn/219.100.37.31.ovpn", 0, 11, 11, 85.2),
    ServerInfo("Japan", "219.100.37.172", "https://ipspeed.info/ovpn/219.100.37.172.ovpn", 0, 8, 8, 88.7),
    ServerInfo("Japan", "115.39.47.101", "https://ipspeed.info/ovpn/115.39.47.101.ovpn", 3, 6, 6, 90.3),
    ServerInfo("Japan", "219.28.132.31", "https://ipspeed.info/ovpn/219.28.132.31.ovpn", 3, 5, 5, 92.1),
    ServerInfo("South Korea", "14.43.226.230", "https://ipspeed.info/ovpn/14.43.226.230.ovpn", 3, 24, 24, 80.6),
    ServerInfo("South Korea", "175.206.178.132", "https://ipspeed.info/ovpn/175.206.178.132.ovpn", 4, 35, 35, 74.9),
]
