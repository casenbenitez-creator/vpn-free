from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QWidget

from vpn_speed_selector.app import ThemeManager


class StatusWidget(QWidget):
    def __init__(self, theme: ThemeManager, parent=None) -> None:
        super().__init__(parent)
        self._theme = theme
        self._label = QLabel(self)
        self._apply_theme()
        self.set_disconnected()

    def set_connected(self, ip: str, country: str, ping_ms: int) -> None:
        status_color = self._theme.get("status", "connected")
        self._label.setText(
            '<span style="color:{}">[CONNECTED]</span> {} ({}) {}ms'.format(
                status_color, ip, country, ping_ms
            )
        )

    def set_disconnected(self) -> None:
        status_color = self._theme.get("status", "disconnected")
        self._label.setText(
            '<span style="color:{}">[DISCONNECTED]</span>'.format(status_color)
        )

    def set_connecting(self, ip: str) -> None:
        status_color = self._theme.get("status", "connecting")
        self._label.setText(
            '<span style="color:{}">[CONNECTING]</span> {}...'.format(status_color, ip)
        )

    def set_failed(self, reason: str) -> None:
        status_color = self._theme.get("status", "failed")
        self._label.setText(
            '<span style="color:{}">[FAILED]</span> {}'.format(status_color, reason)
        )

    def set_next_check(self, time_str: str) -> None:
        current = self._label.text()
        self._label.setText('{}  |  Next check: {}'.format(current, time_str))

    def _apply_theme(self) -> None:
        bg = self._theme.get("status", "background")
        fg = self._theme.get("status", "foreground")
        font_fam = self._theme.get("font", "family")
        font_size = self._theme.get("font", "size_base")
        self.setStyleSheet(
            "background-color: {}; color: {}; font-family: '{}'; font-size: {}pt; padding: 4px 8px;".format(
                bg, fg, font_fam, font_size
            )
        )
