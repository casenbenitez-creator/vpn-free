from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal

from vpn_speed_selector.core.scraper import ServerInfo


class PingWorker(QObject):
    ping_finished = pyqtSignal(list)

    def ping_all(self, servers: list[ServerInfo]) -> None:
        for s in servers:
            if s.actual_ping_ms is None:
                s.actual_ping_ms = s.site_ping_ms
        self.ping_finished.emit(servers)
