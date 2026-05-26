from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication


_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_THEMES_DIR = _PROJECT_ROOT / "themes"


class ThemeManager(QObject):
    theme_changed = pyqtSignal()

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._data: dict[str, Any] = {}
        self._theme_name: str = ""

    def load(self, name: str) -> None:
        path = _THEMES_DIR / f"{name}.json"
        if not path.exists():
            path = _THEMES_DIR / "catppuccin-mocha.json"
        with open(path, encoding="utf-8") as fh:
            self._data = json.load(fh)
        self._theme_name = self._data.get("name", name)
        self.theme_changed.emit()

    @property
    def theme_name(self) -> str:
        return self._theme_name

    def get(self, group: str, key: str) -> str:
        section = self._data.get(group, {})
        value = section.get(key, "")
        if not value:
            palette = QApplication.palette()
            if palette is not None and key == "foreground":
                return palette.windowText().color().name()
            if palette is not None and key == "background":
                return palette.window().color().name()
        return str(value)

    def group(self, name: str) -> dict[str, Any]:
        return dict(self._data.get(name, {}))


def create_app(argv: list[str]) -> QApplication:
    app = QApplication(argv)
    app.setApplicationName("VPN Speed Selector")
    app.setOrganizationName("vpn-speed-selector")

    theme = ThemeManager(parent=app)
    theme.load("catppuccin-mocha")
    app.setProperty("theme_manager", theme)

    from vpn_speed_selector.ui.main_window import MainWindow

    window = MainWindow(theme=theme)
    window.show()

    return app
