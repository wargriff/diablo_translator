from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QMainWindow,
    QSizeGrip,
    QVBoxLayout,
    QWidget,
)

from src.domain.models.game_session import GameLaunchPhase
from src.domain.models.translation_result import TranslationResult
from src.infrastructure import LoggerManager
from src.infrastructure.asset_manager import AssetManager
from src.infrastructure.container import Container
from src.ui.services import WindowBehaviorService
from src.ui.theme import apply as apply_theme
from src.ui.widgets.diablo_tab_widget import DiabloTabWidget
from src.ui.widgets.diagnostic_bar import DiagnosticBar
from src.ui.widgets.gameplay_widget import GameplayWidget
from src.ui.widgets.history_widget import HistoryWidget
from src.ui.widgets.launch_tab_widget import LaunchTabWidget
from src.ui.widgets.settings_tab_widget import SettingsTabWidget
from src.ui.widgets.window_title_bar import WindowTitleBar


class MainWindow(QMainWindow):

    translation_received = pyqtSignal(object)
    voice_received = pyqtSignal(object)
    ocr_status_received = pyqtSignal(object)

    def __init__(self, container: Container) -> None:
        super().__init__()

        self.container = container
        self.logger = LoggerManager.get_logger("MainWindow")
        self._tabs: DiabloTabWidget | None = None
        self._central_layout: QVBoxLayout | None = None
        self._overlay_toggles: QWidget | None = None
        self._title_bar: WindowTitleBar | None = None
        self._size_grip: QSizeGrip | None = None
        self._geometry_dirty = False
        self._background_services_enabled = False

        apply_theme(self)
        self.setWindowTitle("Diablo Translator")
        self.setup_ui()
        self._auto_configure_for_game()
        self.apply_window_behavior()
        self.update_status_bar()

        self.translation_received.connect(self.on_live_translation)
        self.voice_received.connect(self.on_voice_result)
        self.container.set_translation_listener(self.translation_received.emit)
        self.ocr_status_received.connect(self.on_ocr_status)
        self.container.set_status_listener(self.ocr_status_received.emit)
        self.container.set_voice_listener(self.voice_received.emit)

        self._game_timer = QTimer(self)
        self._game_timer.setInterval(1000)
        self._game_timer.timeout.connect(self._on_game_timer)
        self._game_timer.start()

    def setup_ui(self) -> None:
        self._title_bar = WindowTitleBar(self, title="Diablo Translator — Overlay")
        self._title_bar.close_requested.connect(self.close)
        self._title_bar.minimize_requested.connect(self.showMinimized)

        self._tabs = DiabloTabWidget()

        self.gameplay_widget = GameplayWidget(
            self.container,
            on_status_update=self.update_status_bar,
        )
        self.launch_tab = LaunchTabWidget(self.container)
        self.history_widget = HistoryWidget(self.container)
        self.settings_tab = SettingsTabWidget(self.container)

        self._tabs.add_icon_tab(self.gameplay_widget, "play", "OCR — Chat et traduction live")
        self._tabs.add_icon_tab(
            self.launch_tab,
            "launch",
            "Launcher — Diablo III / IV / Immortal",
        )
        self._tabs.add_icon_tab(self.history_widget, "file", "Fichier — Grimoire et exports")
        self._tabs.add_icon_tab(self.settings_tab, "settings", "Réglages")

        self.launch_tab.refresh_requested.connect(self._on_launch_refresh)
        self.launch_tab.launch_requested.connect(self._on_game_launched)
        self.launch_tab.open_settings_requested.connect(self.select_settings_tab)
        self.settings_tab.settings_applied.connect(self._on_settings_applied)

        self._overlay_toggles = self._build_overlay_toggles()
        self._diagnostic_bar = DiagnosticBar()

        central = QWidget()
        self._central_layout = QVBoxLayout()
        self._central_layout.setContentsMargins(16, 16, 16, 8)
        self._central_layout.setSpacing(12)
        self._central_layout.addWidget(self._title_bar)
        self._central_layout.addWidget(self._tabs, stretch=1)
        self._central_layout.addWidget(self._overlay_toggles)
        self._central_layout.addWidget(self._diagnostic_bar)
        central.setLayout(self._central_layout)

        self._size_grip = QSizeGrip(central)
        grip_row = QHBoxLayout()
        grip_row.addStretch()
        grip_row.addWidget(self._size_grip, alignment=Qt.AlignmentFlag.AlignRight)
        self._central_layout.addLayout(grip_row)
        self.setCentralWidget(central)

    def _build_overlay_toggles(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("OverlayToggleBar")

        self.game_mode_checkbox = QCheckBox("Mode Jeu (overlay compact)")
        self.game_mode_checkbox.setChecked(self.container.config.overlay_compact)
        self.game_mode_checkbox.toggled.connect(self.toggle_game_mode)

        self.always_on_top_checkbox = QCheckBox("Toujours devant")
        self.always_on_top_checkbox.setChecked(self.container.config.always_on_top)
        self.always_on_top_checkbox.toggled.connect(self.toggle_always_on_top)

        row = QHBoxLayout()
        row.setContentsMargins(8, 0, 8, 0)
        row.addWidget(self.game_mode_checkbox)
        row.addWidget(self.always_on_top_checkbox)
        row.addStretch()
        panel.setLayout(row)
        return panel

    def _auto_configure_for_game(self) -> None:
        if not self.container.game_session.prepare_overlay_if_game_running():
            return

        self.game_mode_checkbox.blockSignals(True)
        self.game_mode_checkbox.setChecked(True)
        self.game_mode_checkbox.blockSignals(False)
        self.always_on_top_checkbox.blockSignals(True)
        self.always_on_top_checkbox.setChecked(True)
        self.always_on_top_checkbox.blockSignals(False)

    def apply_window_behavior(self) -> None:
        config = self.container.config
        compact = config.overlay_compact
        custom_title = WindowBehaviorService.uses_custom_title_bar(config)

        font = AssetManager.ui_font(config.ui_font_size)
        self.setFont(font)
        self.gameplay_widget.chat_log.setFont(
            AssetManager.monospace_font(config.ui_font_size)
        )

        if self._title_bar is not None:
            self._title_bar.setVisible(compact and custom_title)
        if self._size_grip is not None:
            self._size_grip.setVisible(compact and custom_title)
        if self._overlay_toggles is not None:
            self._overlay_toggles.setVisible(not compact)
        if self._tabs is not None:
            self._tabs.setVisible(True)
        self.menuBar().setVisible(False)
        self.statusBar().setVisible(not compact)

        if compact and not custom_title:
            self.setWindowTitle("Diablo Translator — Overlay chat")
        elif compact:
            self.setWindowTitle("Diablo Translator")
        else:
            self.setWindowTitle("Diablo Translator")

        if self._central_layout is not None:
            margin = 0 if custom_title else (4 if compact else 16)
            top = 0 if custom_title else margin
            self._central_layout.setContentsMargins(margin, top, margin, margin)
            self._central_layout.setSpacing(6 if compact else 12)

        self.gameplay_widget.set_compact_mode(compact)
        self.gameplay_widget._apply_ingame_mode()
        WindowBehaviorService.apply(self, config)

    def toggle_game_mode(self, enabled: bool) -> None:
        config = self.container.config_service.config
        config.overlay_compact = enabled
        if enabled:
            self.container.config_service.apply_overlay_preset()
            self.always_on_top_checkbox.blockSignals(True)
            self.always_on_top_checkbox.setChecked(True)
            self.always_on_top_checkbox.blockSignals(False)
        else:
            self.container.config_service.replace(config)
        self.apply_window_behavior()
        self.update_status_bar()

    def toggle_always_on_top(self, enabled: bool) -> None:
        config = self.container.config_service.config
        config.always_on_top = enabled
        self.container.config_service.replace(config)
        self.apply_window_behavior()

    def _on_settings_applied(self) -> None:
        updated = self.container.config
        self.game_mode_checkbox.setChecked(updated.overlay_compact)
        self.always_on_top_checkbox.setChecked(updated.always_on_top)
        self.apply_window_behavior()
        self.gameplay_widget.refresh_game_status()
        self.launch_tab.refresh_status()
        self.settings_tab.reload_from_container()
        self.update_status_bar()
        self.logger.info("Paramètres mis à jour")

    def _on_launch_refresh(self) -> None:
        self.gameplay_widget.refresh_game_status()
        self._try_auto_start_monitor()

    def _on_game_launched(self, _game_key: str) -> None:
        self._set_game_poll_interval(fast=True)
        QTimer.singleShot(1500, self._try_auto_start_monitor)

    def enable_background_services(self) -> None:
        self._background_services_enabled = True
        self._try_auto_start_monitor()

    def _try_auto_start_monitor(self) -> None:
        if not self._background_services_enabled:
            return

        if not self.container.config.auto_start_monitor:
            return
        if not self.container.config.chat_monitor_enabled:
            return

        state = self.container.game_launch.tick()
        if state.phase == GameLaunchPhase.IDLE:
            self._set_game_poll_interval(fast=False)
            return

        if state.hint:
            self.gameplay_widget.update_wait_hint(state.hint)

        if not self.container.worker.is_running:
            self.gameplay_widget.start_worker(auto=True)

        self._set_game_poll_interval(fast=state.phase != GameLaunchPhase.READY)

    def _set_game_poll_interval(self, *, fast: bool) -> None:
        interval = 800 if fast else 2000
        if self._game_timer.interval() != interval:
            self._game_timer.setInterval(interval)

    def _on_game_timer(self) -> None:
        if not self._background_services_enabled:
            return

        self._try_auto_start_monitor()
        if self._tabs.currentWidget() is self.launch_tab:
            self.launch_tab.refresh_status()

    def update_status_bar(self) -> None:
        if self.container.config.overlay_compact:
            return

        status = self.container.game_detection.scan()
        cache = self.container.pipeline.cache.stats
        provider = self.container.pipeline.translator.provider_name.upper()
        overlay = "ON" if self.container.config.overlay_enabled else "OFF"

        game_text = (
            status.summary()
            if status.is_any_running
            else "Aucun jeu Diablo actif"
        )
        message = (
            f"{game_text}  |  Overlay: {overlay}  |  Moteur: {provider}  |  "
            f"Cache: {cache.entries} ({cache.hits}/{cache.misses})"
        )
        self.statusBar().showMessage(message)

    def on_live_translation(self, result: TranslationResult) -> None:
        self.gameplay_widget.show_live_translation(result)
        self.update_status_bar()

    def on_ocr_status(self, status) -> None:
        self.gameplay_widget.update_ocr_status(status)

    def on_voice_result(self, payload) -> None:
        self.gameplay_widget.handle_voice_result(payload)
        self.update_status_bar()

    def moveEvent(self, event) -> None:
        self._geometry_dirty = True
        super().moveEvent(event)

    def resizeEvent(self, event) -> None:
        self._geometry_dirty = True
        super().resizeEvent(event)

    def _persist_window_geometry(self) -> None:
        if not self.container.config.overlay_compact:
            return
        if not self._geometry_dirty:
            return

        config = WindowBehaviorService.save_geometry(self, self.container.config)
        self.container.config_service.replace(config)
        from src.infrastructure.config_manager import ConfigManager

        ConfigManager.save(config)
        self._geometry_dirty = False

    def closeEvent(self, event) -> None:
        self._persist_window_geometry()
        self.gameplay_widget.shutdown()
        super().closeEvent(event)

    def select_ocr_tab(self) -> None:
        if self._tabs is not None:
            self._tabs.setCurrentWidget(self.gameplay_widget)

    def select_settings_tab(self) -> None:
        if self._tabs is not None:
            self._tabs.setCurrentWidget(self.settings_tab)
