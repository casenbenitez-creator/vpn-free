from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QSpinBox,
    QVBoxLayout,
)

from vpn_speed_selector.app import ThemeManager


class SettingsDialog(QDialog):
    def __init__(self, theme: ThemeManager, parent=None) -> None:
        super().__init__(parent)
        self._theme = theme
        self.setWindowTitle("Settings")
        self.setMinimumWidth(320)
        self._build_ui()
        self._apply_theme()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self._theme_combo = QComboBox(self)
        self._theme_combo.addItem("catppuccin-mocha")
        self._theme_combo.addItem("light")
        form.addRow("Theme:", self._theme_combo)

        self._region_combo = QComboBox(self)
        self._region_combo.addItem("All")
        self._region_combo.addItem("Japan")
        self._region_combo.addItem("South Korea")
        self._region_combo.addItem("Germany")
        self._region_combo.addItem("Russian Federation")
        form.addRow("Region filter:", self._region_combo)

        self._interval_spin = QSpinBox(self)
        self._interval_spin.setRange(5, 120)
        self._interval_spin.setValue(30)
        self._interval_spin.setSuffix(" min")
        form.addRow("Ping interval:", self._interval_spin)

        self._top_n_spin = QSpinBox(self)
        self._top_n_spin.setRange(3, 50)
        self._top_n_spin.setValue(20)
        form.addRow("Display top N:", self._top_n_spin)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @property
    def selected_theme(self) -> str:
        return self._theme_combo.currentText()

    @property
    def selected_region(self) -> str:
        return self._region_combo.currentText()

    @property
    def ping_interval(self) -> int:
        return self._interval_spin.value()

    @property
    def top_n(self) -> int:
        return self._top_n_spin.value()

    def _apply_theme(self) -> None:
        bg = self._theme.get("dialog", "background")
        fg = self._theme.get("dialog", "foreground")
        input_bg = self._theme.get("dialog", "input_background")
        input_fg = self._theme.get("dialog", "input_foreground")
        input_border = self._theme.get("dialog", "input_border")
        font_fam = self._theme.get("font", "family")
        font_size = self._theme.get("font", "size_base")
        self.setStyleSheet(
            "QDialog {{ background-color: {}; color: {}; font-family: '{}'; font-size: {}pt; }}"
            "QComboBox, QSpinBox {{ background-color: {}; color: {}; border: 1px solid {}; padding: 4px; }}"
            .format(
                bg, fg, font_fam, font_size,
                input_bg, input_fg, input_border,
            )
        )
