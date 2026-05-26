from __future__ import annotations

from enum import Enum
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal

from vpn_speed_selector.core.scraper import ServerInfo


class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    FAILED = "failed"


class VPNConnector(QObject):
    state_changed = pyqtSignal(str)
    log_line = pyqtSignal(str)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._state = ConnectionState.DISCONNECTED
        self._current_server: Optional[ServerInfo] = None

    @property
    def state(self) -> ConnectionState:
        return self._state

    @property
    def current_server(self) -> Optional[ServerInfo]:
        return self._current_server

    def connect_to(self, server: ServerInfo) -> None:
        self._current_server = server
        self._set_state(ConnectionState.CONNECTING)
        self.log_line.emit("[CONNECT] Connecting to {} ({})...".format(server.ip, server.country))

    def disconnect(self) -> None:
        if self._state == ConnectionState.DISCONNECTED:
            return
        self._set_state(ConnectionState.DISCONNECTING)
        self.log_line.emit("[DISCONNECT] Disconnecting...")

    def _set_state(self, state: ConnectionState) -> None:
        self._state = state
        self.state_changed.emit(state.value)
