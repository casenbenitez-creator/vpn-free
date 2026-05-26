from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal


class Scheduler(QObject):
    next_check_changed = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._interval_minutes = 30

    def start(self) -> None:
        self.next_check_changed.emit("--:--")

    def stop(self) -> None:
        self.next_check_changed.emit("stopped")
