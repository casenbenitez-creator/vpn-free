from __future__ import annotations

from PyQt6.QtCore import QSettings


class ConfigStore:
    def __init__(self) -> None:
        self._settings = QSettings("vpn-speed-selector", "VPN Speed Selector")

    def get(self, key: str, default=None):
        return self._settings.value(key, default)

    def set(self, key: str, value) -> None:
        self._settings.setValue(key, value)

    def theme_name(self) -> str:
        return str(self.get("theme", "catppuccin-mocha"))

    def set_theme_name(self, name: str) -> None:
        self.set("theme", name)

    def region_filter(self) -> str:
        return str(self.get("region_filter", "All"))

    def set_region_filter(self, region: str) -> None:
        self.set("region_filter", region)
