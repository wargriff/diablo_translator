from __future__ import annotations

import subprocess
import sys
import webbrowser
from datetime import datetime

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QScrollArea,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from launcher.control_panel import ControlPanelWidget
from launcher.hub_sounds import HubSoundPlayer
from launcher.hub_translator import HubTranslatorPanel
from launcher.hub_workers import HubStatusWorker
from launcher.processes import (
    launch_platform_orchestrated,
    prepare_live_web,
    run_cli_tool,
    run_desktop,
    run_mobile,
    run_server,
    run_web,
    stop_all_services,
)
from launcher.service_ports import resolve_web_port, web_base_url
from src.infrastructure.paths import BUNDLE_ROOT, PROJECT_ROOT
from src.services.history_events import on_translation_added

THEME_PATH = BUNDLE_ROOT / "assets" / "themes" / "diablo_dark.qss"
HUB_STYLES = BUNDLE_ROOT / "launcher" / "hub_theme.qss"
HISTORY_LIMIT = 15

VIEW_CONTROL = 0
VIEW_TRANSLATION = 1
VIEW_HISTORY = 2


class SanctuaryHubWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Diablo Translator — Centre de contrôle")
        self.setMinimumSize(920, 640)
        self.resize(980, 720)
        self._children: list[subprocess.Popen] = []
        self._service_online = {"api": False, "web": False}
        self._sounds = HubSoundPlayer()
        self._history_layout: QVBoxLayout | None = None
        self._sound_action: QAction | None = None
        self._view_actions: list[QAction] = []
        self._live_action: QAction | None = None
        self._stack: QStackedWidget | None = None
        self._control_panel: ControlPanelWidget | None = None
        self._status_refresh_running = False
        self._current_view = VIEW_CONTROL

        self._build_menubar()
        self._build_statusbar()
        self._build_ui()
        self._apply_theme()

        on_translation_added(self._on_translation_added)

        timer = QTimer(self)
        timer.timeout.connect(self._refresh_status)
        timer.start(8000)
        QTimer.singleShot(200, self._refresh_status)
        QTimer.singleShot(300, self._warmup_pipeline)
        self._sounds.play("open")

    def _warmup_pipeline(self) -> None:
        import threading

        threading.Thread(target=self._load_pipeline, daemon=True).start()

    @staticmethod
    def _load_pipeline() -> None:
        from launcher.hub_services import get_hub_pipeline

        get_hub_pipeline()

    def _apply_theme(self) -> None:
        styles = ""
        if THEME_PATH.exists():
            styles += THEME_PATH.read_text(encoding="utf-8")
        if HUB_STYLES.exists():
            styles += "\n" + HUB_STYLES.read_text(encoding="utf-8")
        if styles:
            self.setStyleSheet(styles)

    def _build_menubar(self) -> None:
        bar = self.menuBar()
        bar.setObjectName("HubMenuBar")

        sanctuary = bar.addMenu("Sanctuaire")
        sanctuary.addAction("Actualiser", self._refresh_all)
        sanctuary.addSeparator()
        sanctuary.addAction("Quitter", self.close)

        diablo = bar.addMenu("Diablo")
        self._live_action = diablo.addAction("Interface en direct (OCR)", self._launch_live_desktop)
        diablo.addAction("Live web", self._open_live_web)
        diablo.addSeparator()
        diablo.addAction("Détecter le jeu", lambda: self._run_tool("game"))

        services = bar.addMenu("Services")
        services.addAction("API Server (:8000)", self._launch_server)
        services.addAction("Web Companion (:3000)", self._launch_web)
        services.addAction("Mobile Flutter", self._launch_mobile)
        services.addSeparator()
        services.addAction("Plateforme complète", self._launch_platform)
        services.addAction("Arrêter tout", self._stop_all)

        view = bar.addMenu("Affichage")
        for label, view_index in (
            ("Contrôle", VIEW_CONTROL),
            ("Traduction", VIEW_TRANSLATION),
            ("Chroniques", VIEW_HISTORY),
        ):
            action = view.addAction(label, lambda checked=False, i=view_index: self._switch_view(i))
            action.setCheckable(True)
            action.setChecked(view_index == VIEW_CONTROL)
            self._view_actions.append(action)

        rites = bar.addMenu("Rites")
        self._sound_action = rites.addAction("", self._toggle_sounds)
        self._sync_sound_menu_label()

        parametres = bar.addMenu("Paramètres")
        parametres.addAction("settings.json", self._open_settings_file)
        parametres.addAction("Réglages web", lambda: webbrowser.open(f"{web_base_url()}/parametres"))
        parametres.addSeparator()
        parametres.addAction("Statistiques", lambda: self._run_tool("stats"))
        parametres.addAction("Exporter historique", lambda: self._run_tool("export"))
        parametres.addAction("Tests unitaires", lambda: self._run_tool("test"))
        parametres.addAction("Logs web", lambda: webbrowser.open(f"{web_base_url()}/logs"))

    def _build_ui(self) -> None:
        root = QWidget()
        root.setObjectName("SanctuaryRoot")
        outer = QVBoxLayout(root)
        outer.setContentsMargins(14, 12, 14, 14)
        outer.setSpacing(8)
        outer.addWidget(self._build_header())
        outer.addWidget(self._build_stack(), stretch=1)
        self.setCentralWidget(root)

    def _build_header(self) -> QFrame:
        header = QFrame()
        header.setObjectName("HubHeader")
        row = QHBoxLayout(header)
        row.setContentsMargins(12, 8, 12, 8)

        title = QLabel("DIABLO TRANSLATOR")
        title.setObjectName("HubHeaderTitle")
        subtitle = QLabel("Centre de contrôle — lanceurs & services")
        subtitle.setObjectName("MutedText")

        left = QVBoxLayout()
        left.addWidget(title)
        left.addWidget(subtitle)

        self._badge_api = QLabel("API off")
        self._badge_api.setObjectName("HubBadgeOffline")
        self._badge_web = QLabel("Web off")
        self._badge_web.setObjectName("HubBadgeOffline")
        self._badge_game = QLabel("Jeu : …")
        self._badge_game.setObjectName("HubBadgeOffline")

        row.addLayout(left)
        row.addStretch()
        row.addWidget(self._badge_game)
        row.addWidget(self._badge_api)
        row.addWidget(self._badge_web)
        return header

    def _build_stack(self) -> QStackedWidget:
        self._stack = QStackedWidget()
        self._control_panel = ControlPanelWidget(
            on_launch_desktop=self._launch_live_desktop,
            on_launch_server=self._launch_server,
            on_launch_web=self._launch_web,
            on_launch_platform=self._launch_platform,
            on_launch_mobile=self._launch_mobile,
            on_stop_all=self._stop_all,
            on_open_live_web=self._open_live_web,
            on_build_exe=self._build_exe,
            on_run_tool=self._run_tool,
        )
        self._stack.addWidget(self._wrap_center(self._control_panel, wide=True))
        self._translator = HubTranslatorPanel()
        self._translator.set_status_callback(self._status.setText)
        self._stack.addWidget(self._wrap_center(self._translator))
        self._stack.addWidget(self._wrap_center(self._build_history_panel()))
        self._stack.setCurrentIndex(VIEW_CONTROL)
        return self._stack

    @staticmethod
    def _wrap_center(widget: QWidget, *, wide: bool = False) -> QWidget:
        wrapper = QWidget()
        layout = QHBoxLayout(wrapper)
        if not wide:
            layout.addStretch()
        layout.addWidget(widget, stretch=1 if wide else 0)
        if not wide:
            layout.addStretch()
        return wrapper

    def _switch_view(self, view_index: int) -> None:
        self._current_view = view_index
        if self._stack is not None:
            self._stack.setCurrentIndex(view_index)
        for index, action in enumerate(self._view_actions):
            action.blockSignals(True)
            action.setChecked(index == view_index)
            action.blockSignals(False)
        if view_index == VIEW_HISTORY:
            QTimer.singleShot(0, self._refresh_history)
        if view_index == VIEW_CONTROL and self._control_panel is not None:
            QTimer.singleShot(0, self._control_panel.refresh_diagnostics)

    def _build_history_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("HubHistoryPanel")
        panel.setMinimumSize(640, 420)
        outer = QVBoxLayout(panel)
        outer.addWidget(self._section_label("Chroniques récentes"))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        self._history_layout = QVBoxLayout(container)
        self._history_layout.setSpacing(6)
        scroll.setWidget(container)
        outer.addWidget(scroll, stretch=1)
        return panel

    @staticmethod
    def _section_label(text: str) -> QLabel:
        label = QLabel(text.upper())
        label.setObjectName("HubSectionLabel")
        return label

    def _build_statusbar(self) -> None:
        bar = QStatusBar()
        self._status = QLabel("Prêt")
        bar.addWidget(self._status)
        self.setStatusBar(bar)

    def _refresh_all(self) -> None:
        self._refresh_status()
        if self._current_view == VIEW_HISTORY:
            self._refresh_history()

    def _refresh_status(self) -> None:
        if self._status_refresh_running:
            return
        self._status_refresh_running = True
        worker = HubStatusWorker(self)

        def on_finished(api_ok: bool, web_ok: bool) -> None:
            self._status_refresh_running = False
            self._apply_status(api_ok, web_ok)
            worker.deleteLater()

        worker.finished.connect(on_finished)
        worker.start()

    def _apply_status(self, api_ok: bool, web_ok: bool) -> None:
        self._service_online["api"] = api_ok
        self._service_online["web"] = web_ok
        self._set_badge(self._badge_api, api_ok, "API OK", "API off")
        self._set_badge(self._badge_web, web_ok, "Web OK", "Web off")

        game_running = False
        game_label = "Jeu : aucun"
        try:
            from src.game_detection.game_detection_service import GameDetectionService

            status = GameDetectionService().scan()
            game_running = status.is_any_running
            if status.running_games:
                names = ", ".join(game.short_title for game in status.running_games)
                game_label = f"Jeu : {names}"
        except Exception:
            game_label = "Jeu : ?"

        self._badge_game.setText(game_label)
        self._badge_game.setObjectName("HubBadgeOnline" if game_running else "HubBadgeOffline")
        if self._live_action is not None:
            self._live_action.setEnabled(True)
        style = self._badge_game.style()
        if style is not None:
            style.unpolish(self._badge_game)
            style.polish(self._badge_game)

        alive = sum(1 for proc in self._children if proc.poll() is None)
        web_port = resolve_web_port()
        self._status.setText(
            f"Web {'OK' if web_ok else 'off'} (:{web_port}) | "
            f"API {'OK' if api_ok else 'off'} | Processus {alive} | "
            f"Contrôle → Plateforme API+Web"
        )
        if self._control_panel is not None and self._current_view == VIEW_CONTROL:
            self._control_panel.refresh_diagnostics()

    @staticmethod
    def _set_badge(label: QLabel, online: bool, online_text: str, offline_text: str) -> None:
        text = online_text if online else offline_text
        object_name = "HubBadgeOnline" if online else "HubBadgeOffline"
        if label.text() == text and label.objectName() == object_name:
            return
        label.setText(text)
        label.setObjectName(object_name)
        style = label.style()
        if style is not None:
            style.unpolish(label)
            style.polish(label)

    def _refresh_history(self) -> None:
        if self._history_layout is None:
            return
        while self._history_layout.count():
            item = self._history_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        try:
            from src.infrastructure.database import Database
            from src.services.history_service import HistoryService

            Database.initialize()
            records = HistoryService().list_recent(limit=HISTORY_LIMIT)
        except Exception as exc:
            self._history_layout.addWidget(self._muted_label(str(exc)))
            self._history_layout.addStretch()
            return
        if not records:
            self._history_layout.addWidget(self._muted_label("Aucune traduction enregistrée."))
            self._history_layout.addStretch()
            return
        for record in records:
            self._history_layout.addWidget(self._history_row(record))
        self._history_layout.addStretch()

    @staticmethod
    def _muted_label(text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("MutedText")
        label.setWordWrap(True)
        return label

    def _history_row(self, record) -> QFrame:
        row = QFrame()
        row.setObjectName("HubHistoryItem")
        layout = QVBoxLayout(row)
        meta = QLabel(
            f"{record.source_language or '?'} → {record.target_language or '?'} · "
            f"{self._format_time(record.created_at)}"
        )
        meta.setObjectName("HubHistoryMeta")
        text = QLabel(record.translated_text)
        text.setObjectName("HubHistoryText")
        text.setWordWrap(True)
        layout.addWidget(meta)
        layout.addWidget(text)
        return row

    @staticmethod
    def _format_time(value) -> str:
        if isinstance(value, datetime):
            return value.strftime("%H:%M")
        return str(value)[:16]

    def _on_translation_added(self, _record) -> None:
        if self._current_view == VIEW_HISTORY:
            QTimer.singleShot(0, self._refresh_history)

    def _track(self, proc: subprocess.Popen) -> None:
        self._children.append(proc)
        self._sounds.play("launch")

    def _launch_live_desktop(self) -> None:
        """Interface OCR overlay en jeu — menu Diablo."""
        self._track(run_desktop())
        self._status.setText("Interface en direct lancée — overlay Diablo actif")

    def _open_live_web(self) -> None:
        self._status.setText("Démarrage API + Web pour Live…")
        import threading

        def task() -> None:
            ok, message = prepare_live_web(
                self._children,
                on_spawn=lambda proc: QTimer.singleShot(0, lambda p=proc: self._track(p)),
            )
            QTimer.singleShot(0, lambda: self._on_live_web_ready(ok, message))

        threading.Thread(target=task, daemon=True).start()

    def _on_live_web_ready(self, ok: bool, message: str) -> None:
        self._status.setText(message)
        if ok:
            self._sounds.play("success")
        self._refresh_status()

    def _launch_server(self) -> None:
        try:
            self._track(run_server())
        except RuntimeError as exc:
            self._status.setText(str(exc))
            return
        self._status.setText("API lancee (:8000) — attente demarrage…")

    def _launch_web(self) -> None:
        try:
            self._track(run_web(kill=True))
        except RuntimeError as exc:
            self._status.setText(str(exc))
            return
        self._status.setText("Web lance (:3000)")

    def _launch_mobile(self) -> None:
        try:
            self._track(run_mobile())
        except RuntimeError as exc:
            self._status.setText(str(exc))
            return
        self._status.setText("Mobile lance")

    def _launch_platform(self) -> None:
        self._status.setText("Demarrage plateforme API + Web (patientez)…")
        import threading

        def task() -> None:
            ok, message = launch_platform_orchestrated(
                self._children,
                on_spawn=lambda proc: QTimer.singleShot(0, lambda p=proc: self._track(p)),
                open_browser=True,
            )
            QTimer.singleShot(0, lambda: self._on_platform_ready(ok, message))

        threading.Thread(target=task, daemon=True).start()

    def _on_platform_ready(self, ok: bool, message: str) -> None:
        self._status.setText(message)
        if ok:
            self._sounds.play("success")
        self._refresh_status()

    def _build_exe(self) -> None:
        script = PROJECT_ROOT / "Build-Pro.bat"
        if not script.exists():
            script = PROJECT_ROOT / "build" / "Build-Pro.bat"
        if not script.exists():
            QMessageBox.warning(self, "Build", "Build-Pro.bat introuvable.")
            return
        flags = subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
        proc = subprocess.Popen(
            ["cmd", "/c", str(script)],
            cwd=PROJECT_ROOT,
            creationflags=flags,  # type: ignore[arg-type]
        )
        self._track(proc)
        self._status.setText("Build exe lance — voir fenetre console")

    def _stop_all(self) -> None:
        stopped = stop_all_services(self._children)
        self._sounds.play("success")
        self._status.setText(f"{stopped} service(s) arrete(s)")
        self._refresh_status()

    def _run_tool(self, command: str) -> None:
        self._status.setText(f"Lancement {command}…")
        QTimer.singleShot(0, lambda: self._run_tool_async(command))

    def _run_tool_async(self, command: str) -> None:
        import threading

        def task() -> None:
            code = run_cli_tool(command)
            QTimer.singleShot(0, lambda: self._status.setText(f"'{command}' terminé (code {code})"))

        threading.Thread(target=task, daemon=True).start()

    def _toggle_sounds(self) -> None:
        self._sounds.set_enabled(not self._sounds.enabled)
        self._sync_sound_menu_label()

    def _sync_sound_menu_label(self) -> None:
        if self._sound_action is not None:
            state = "activés" if self._sounds.enabled else "désactivés"
            self._sound_action.setText(f"Sons : {state}")

    def _open_settings_file(self) -> None:
        path = PROJECT_ROOT / "user_data" / "settings.json"
        if not path.exists():
            QMessageBox.warning(self, "Paramètres", f"Fichier introuvable :\n{path}")
            return
        if sys.platform == "win32":
            import os

            os.startfile(path)  # noqa: S606
        else:
            webbrowser.open(path.as_uri())


def run_hub() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Diablo Translator Control")
    app.setFont(QFont("Segoe UI", 10))
    window = SanctuaryHubWindow()
    window.show()
    return app.exec()


run_control = run_hub
