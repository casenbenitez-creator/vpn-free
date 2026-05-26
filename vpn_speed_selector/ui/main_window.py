from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
    QMainWindow,
    QTableView,
)

from vpn_speed_selector.app import ThemeManager
from vpn_speed_selector.core.connector import VPNConnector, ConnectionState
from vpn_speed_selector.core.config_store import ConfigStore
from vpn_speed_selector.core.scraper import DUMMY_SERVERS, ServerInfo
from vpn_speed_selector.core.ranker import rank_servers
from vpn_speed_selector.ui.log_widget import LogWidget
from vpn_speed_selector.ui.server_table import ServerTableModel
from vpn_speed_selector.ui.settings_dialog import SettingsDialog
from vpn_speed_selector.ui.status_widget import StatusWidget


class MainWindow(QMainWindow):
    def __init__(self, theme: ThemeManager, parent=None) -> None:
        super().__init__(parent)
        self._theme = theme
        self._connector = VPNConnector(parent=self)
        self._config = ConfigStore()
        self._servers: list[ServerInfo] = []

        self.setWindowTitle("VPN Speed Selector")
        self.setMinimumSize(720, 520)
        self.resize(860, 600)

        self._build_ui()
        self._connect_signals()
        self._apply_theme()
        self._load_dummy_data()

        self._connector.state_changed.connect(self._on_state_changed)
        self._connector.log_line.connect(self._on_log_line)
        self._theme.theme_changed.connect(self._apply_theme)

    def _build_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        toolbar = self._build_toolbar()
        root.addWidget(toolbar)

        self._table_model = ServerTableModel(parent=self)
        self._table = QTableView(self)
        self._table.setModel(self._table_model)
        self._table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self._table.setShowGrid(True)
        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)
        header = self._table.horizontalHeader()
        header.setStretchLastSection(True)
        for col in range(self._table_model.columnCount()):
            header.resizeSection(col, self._table_model.column_width(col))

        self._status_widget = StatusWidget(self._theme, parent=self)

        self._log_widget = LogWidget(self._theme, parent=self)

        splitter = QSplitter(Qt.Orientation.Vertical, self)
        splitter.addWidget(self._table)
        bottom = QWidget(self)
        bottom_layout = QVBoxLayout(bottom)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(0)
        bottom_layout.addWidget(self._status_widget)
        bottom_layout.addWidget(self._log_widget)
        splitter.addWidget(bottom)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        root.addWidget(splitter, 1)

    def _build_toolbar(self) -> QWidget:
        bar = QWidget(self)
        bar.setObjectName("toolbar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(8, 4, 8, 4)

        self._region_combo = QComboBox(bar)
        self._region_combo.addItem("All")
        self._region_combo.addItem("Japan")
        self._region_combo.addItem("South Korea")
        self._region_combo.addItem("Germany")
        self._region_combo.addItem("Russian Federation")
        self._region_combo.setCurrentText(self._config.region_filter())

        self._refresh_btn = QPushButton("Refresh", bar)
        self._connect_btn = QPushButton("Connect Best", bar)
        self._disconnect_btn = QPushButton("Disconnect", bar)
        self._settings_btn = QPushButton("Settings", bar)

        layout.addWidget(QLabel("Region:", bar))
        layout.addWidget(self._region_combo)
        layout.addStretch(1)
        layout.addWidget(self._refresh_btn)
        layout.addWidget(self._connect_btn)
        layout.addWidget(self._disconnect_btn)
        layout.addWidget(self._settings_btn)

        return bar

    def _connect_signals(self) -> None:
        self._refresh_btn.clicked.connect(self._on_refresh)
        self._connect_btn.clicked.connect(self._on_connect_best)
        self._disconnect_btn.clicked.connect(self._on_disconnect)
        self._settings_btn.clicked.connect(self._on_settings)
        self._region_combo.currentTextChanged.connect(self._on_region_changed)
        self._table.doubleClicked.connect(self._on_table_double_click)

    def _load_dummy_data(self) -> None:
        self._servers = rank_servers(list(DUMMY_SERVERS))
        self._apply_region_filter()

    def _apply_region_filter(self) -> None:
        region = self._region_combo.currentText()
        if region == "All":
            filtered = self._servers
        else:
            filtered = [s for s in self._servers if s.country == region]
        self._table_model.set_servers(filtered)

    def _on_refresh(self) -> None:
        self._load_dummy_data()
        self._on_log_line("[SCAN] Refreshed server list (mock data)")

    def _on_connect_best(self) -> None:
        server = self._table_model.server_at(0)
        if server is None:
            self._on_log_line("[ERR] No servers available")
            return
        self._connector.connect_to(server)

    def _on_disconnect(self) -> None:
        self._connector.disconnect()

    def _on_settings(self) -> None:
        dlg = SettingsDialog(self._theme, parent=self)
        if dlg.exec() == SettingsDialog.DialogCode.Accepted:
            new_theme = dlg.selected_theme
            if new_theme != self._theme.theme_name:
                self._theme.load(new_theme)
                self._config.set_theme_name(new_theme)

    def _on_region_changed(self, region: str) -> None:
        self._config.set_region_filter(region)
        self._apply_region_filter()

    def _on_table_double_click(self, index) -> None:
        server = self._table_model.server_at(index.row())
        if server is not None:
            self._connector.connect_to(server)

    def _on_state_changed(self, state_name: str) -> None:
        state = ConnectionState(state_name)
        if state == ConnectionState.DISCONNECTED:
            self._status_widget.set_disconnected()
        elif state == ConnectionState.CONNECTING:
            srv = self._connector.current_server
            if srv is not None:
                self._status_widget.set_connecting(srv.ip)
        elif state == ConnectionState.CONNECTED:
            srv = self._connector.current_server
            if srv is not None:
                ping = srv.actual_ping_ms or srv.site_ping_ms
                self._status_widget.set_connected(srv.ip, srv.country, ping)
        elif state == ConnectionState.FAILED:
            self._status_widget.set_failed("Connection failed")

    def _on_log_line(self, text: str) -> None:
        self._log_widget.append_line(text)

    def _apply_theme(self) -> None:
        win_bg = self._theme.get("window", "background")
        win_fg = self._theme.get("window", "foreground")
        font_fam = self._theme.get("font", "family")
        font_size = self._theme.get("font", "size_base")
        border = self._theme.get("window", "border")
        self.setStyleSheet(
            "QMainWindow {{ background-color: {}; color: {}; font-family: '{}'; font-size: {}pt; }}"
            .format(win_bg, win_fg, font_fam, font_size)
        )

        tb_bg = self._theme.get("toolbar", "background")
        tb_fg = self._theme.get("toolbar", "foreground")
        btn_bg = self._theme.get("toolbar", "button_background")
        btn_fg = self._theme.get("toolbar", "button_foreground")
        btn_hover = self._theme.get("toolbar", "button_hover")
        font_hdr = self._theme.get("font", "size_header")
        self.findChild(QWidget, "toolbar").setStyleSheet(
            "#toolbar {{ background-color: {}; color: {}; }}"
            "QPushButton {{ background-color: {}; color: {}; border: 1px solid {}; border-radius: 4px; padding: 6px 14px; font-size: {}pt; }}"
            "QPushButton:hover {{ background-color: {}; }}"
            "QComboBox {{ background-color: {}; color: {}; border: 1px solid {}; border-radius: 4px; padding: 4px 8px; }}"
            "QLabel {{ color: {}; font-size: {}pt; }}"
            .format(
                tb_bg, tb_fg,
                btn_bg, btn_fg, border, font_hdr,
                btn_hover,
                btn_bg, btn_fg, border,
                tb_fg, font_size,
            )
        )

        tbl_bg = self._theme.get("table", "background")
        tbl_fg = self._theme.get("table", "foreground")
        row_odd = self._theme.get("table", "row_odd")
        hdr_bg = self._theme.get("table", "header_bg")
        hdr_fg = self._theme.get("table", "header_fg")
        sel_bg = self._theme.get("table", "selected")
        grid = self._theme.get("table", "grid_line")
        top5 = self._theme.get("table", "top5_indicator")
        self._table.setStyleSheet(
            "QTableView {{ background-color: {}; color: {}; gridline-color: {}; alternate-background-color: {}; selection-background-color: {}; font-size: {}pt; }}"
            "QHeaderView::section {{ background-color: {}; color: {}; border: 1px solid {}; padding: 4px; font-size: {}pt; }}"
            .format(
                tbl_bg, tbl_fg, grid, row_odd, sel_bg, font_size,
                hdr_bg, hdr_fg, border, font_hdr,
            )
        )

        self._status_widget._apply_theme()
        self._log_widget._apply_theme()
