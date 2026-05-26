from __future__ import annotations

from typing import Any, Optional

from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex

from vpn_speed_selector.core.scraper import ServerInfo


_COLUMNS = [
    ("rank", "#", 30, Qt.AlignmentFlag.AlignCenter),
    ("country", "Country", 120, Qt.AlignmentFlag.AlignLeft),
    ("ip", "IP", 130, Qt.AlignmentFlag.AlignLeft),
    ("ping_ms", "Ping ms", 70, Qt.AlignmentFlag.AlignRight),
    ("uptime_days", "Uptime", 70, Qt.AlignmentFlag.AlignRight),
    ("score", "Score", 60, Qt.AlignmentFlag.AlignRight),
    ("status", "Status", 90, Qt.AlignmentFlag.AlignCenter),
]

_FIELD_MAP = {
    "rank": lambda s, i: str(i + 1),
    "country": lambda s, i: s.country,
    "ip": lambda s, i: s.ip,
    "ping_ms": lambda s, i: str(s.actual_ping_ms or s.site_ping_ms),
    "uptime_days": lambda s, i: "{}d".format(s.uptime_days),
    "score": lambda s, i: str(s.score),
    "status": lambda s, i: s.status,
}


class ServerTableModel(QAbstractTableModel):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._servers: list[ServerInfo] = []
        self._top_n = 5

    def set_servers(self, servers: list[ServerInfo]) -> None:
        self.beginResetModel()
        self._servers = list(servers)
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._servers)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(_COLUMNS)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None
        row = index.row()
        col = index.column()
        if row >= len(self._servers):
            return None
        key = _COLUMNS[col][0]
        getter = _FIELD_MAP.get(key)
        if getter is None:
            return None
        return getter(self._servers[row], row)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return _COLUMNS[section][1]
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def column_width(self, col: int) -> int:
        if 0 <= col < len(_COLUMNS):
            return _COLUMNS[col][2]
        return 80

    def column_alignment(self, col: int) -> Qt.AlignmentFlag:
        if 0 <= col < len(_COLUMNS):
            return _COLUMNS[col][3]
        return Qt.AlignmentFlag.AlignLeft

    def is_top_row(self, row: int) -> bool:
        return 0 <= row < self._top_n

    def server_at(self, row: int) -> Optional[ServerInfo]:
        if 0 <= row < len(self._servers):
            return self._servers[row]
        return None
