from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import QTextEdit

from vpn_speed_selector.app import ThemeManager


_MAX_LINES = 500


class LogWidget(QTextEdit):
    def __init__(self, theme: ThemeManager, parent=None) -> None:
        super().__init__(parent)
        self._theme = theme
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self._apply_theme()

    def append_line(self, text: str) -> None:
        self.append(text)
        if self.document().blockCount() > _MAX_LINES:
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            cursor.movePosition(
                QTextCursor.MoveOperation.Down,
                QTextCursor.MoveMode.KeepAnchor,
                self.document().blockCount() - _MAX_LINES,
            )
            cursor.removeSelectedText()
            cursor.deleteChar()
        self.ensureCursorVisible()

    def _apply_theme(self) -> None:
        bg = self._theme.get("log", "background")
        fg = self._theme.get("log", "foreground")
        font_fam = self._theme.get("font", "family")
        font_size = self._theme.get("font", "size_log")
        self.setStyleSheet(
            "background-color: {}; color: {}; font-family: Consolas, '{}'; font-size: {}pt; border: none; padding: 4px;".format(
                bg, fg, font_fam, font_size
            )
        )
