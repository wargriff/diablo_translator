from __future__ import annotations

import webbrowser
from collections.abc import Callable

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from launcher.api_probe import probe_web_home
from launcher.diagnostics import collect_diagnostics
from launcher.service_ports import api_base_url, resolve_web_port, web_base_url


class ControlPanelWidget(QWidget):
    """Panneau unique pour lancer et surveiller tous les services."""

    def __init__(
        self,
        *,
        on_launch_desktop: Callable[[], None],
        on_launch_server: Callable[[], None],
        on_launch_web: Callable[[], None],
        on_launch_platform: Callable[[], None],
        on_launch_mobile: Callable[[], None],
        on_stop_all: Callable[[], None],
        on_open_live_web: Callable[[], None],
        on_build_exe: Callable[[], None],
        on_run_tool: Callable[[str], None],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setMinimumWidth(720)
        self._callbacks = {
            "desktop": on_launch_desktop,
            "server": on_launch_server,
            "web": on_launch_web,
            "platform": on_launch_platform,
            "mobile": on_launch_mobile,
            "stop": on_stop_all,
            "live": on_open_live_web,
            "web_home": self._open_web_home,
            "build": on_build_exe,
        }
        self._on_run_tool = on_run_tool
        self._diag_labels: list[QLabel] = []
        self._build_ui()
        QTimer.singleShot(400, self.refresh_diagnostics)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(10)

        root.addWidget(self._section("Applications"))
        root.addLayout(self._row(
            ("Interface OCR (jeu)", "desktop", "HubPrimaryPill"),
            ("Live web (/live)", "live", "HubPillButton"),
        ))

        root.addWidget(self._section("Services"))
        root.addLayout(self._row(
            ("API :8000", "server", "HubPillButton"),
            ("Web :3000", "web", "HubPillButton"),
            ("Plateforme API+Web", "platform", "HubPrimaryPill"),
        ))
        root.addLayout(self._row(
            ("Mobile Flutter", "mobile", "HubPillButton"),
            ("Accueil web", "web_home", "HubPillButton"),
            ("Arreter tout", "stop", "HubPillButton"),
        ))

        root.addWidget(self._section("Outils"))
        root.addLayout(self._row(
            ("Construire l'exe", "build", "HubPillButton"),
        ))
        tools = QHBoxLayout()
        for label, cmd in (
            ("Verifier deps", "check"),
            ("Tests", "test"),
            ("Jeu detecte", "game"),
            ("Stats", "stats"),
        ):
            btn = QPushButton(label)
            btn.setObjectName("HubPillButton")
            btn.clicked.connect(lambda _=False, c=cmd: self._on_run_tool(c))
            tools.addWidget(btn)
        tools.addStretch()
        root.addLayout(tools)

        root.addWidget(self._section("Diagnostics"))
        self._diag_frame = QFrame()
        self._diag_frame.setObjectName("HubHistoryPanel")
        diag_layout = QVBoxLayout(self._diag_frame)
        diag_layout.setSpacing(4)
        self._diag_layout = diag_layout
        root.addWidget(self._diag_frame)

        refresh = QPushButton("Actualiser diagnostics")
        refresh.setObjectName("HubPillButton")
        refresh.clicked.connect(self.refresh_diagnostics)
        root.addWidget(refresh)
        root.addStretch()

    @staticmethod
    def _section(title: str) -> QLabel:
        label = QLabel(title.upper())
        label.setObjectName("HubSectionLabel")
        return label

    def _row(self, *items: tuple[str, str, str]) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)
        for text, key, style in items:
            btn = QPushButton(text)
            btn.setObjectName(style)
            btn.clicked.connect(self._callbacks[key])
            row.addWidget(btn)
        row.addStretch()
        return row

    def refresh_diagnostics(self) -> None:
        while self._diag_layout.count():
            item = self._diag_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self._diag_labels.clear()
        for line in collect_diagnostics():
            row = QLabel(f"{'OK' if line.ok else '!!'}  {line.label} — {line.detail}")
            row.setObjectName("HubHistoryMeta" if line.ok else "HubHistoryText")
            row.setWordWrap(True)
            self._diag_layout.addWidget(row)
            self._diag_labels.append(row)

    def _open_web_home(self) -> None:
        port = resolve_web_port()
        if probe_web_home(port):
            webbrowser.open(f"{web_base_url(port)}/")
            return
        self._callbacks["platform"]()

    def open_web_home(self) -> None:
        port = resolve_web_port()
        webbrowser.open(f"{web_base_url(port)}/")

    def open_api_docs(self) -> None:
        webbrowser.open(f"{api_base_url()}/docs")
