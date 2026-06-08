from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizeGrip,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from src.domain.models.translation_result import TranslationResult
from src.infrastructure import LoggerManager
from src.infrastructure.asset_manager import AssetManager
from src.infrastructure.container import Container
from src.ui.dialogs import SettingsDialog
from src.ui.services import WindowBehaviorService
from src.ui.theme import apply as apply_theme
from src.ui.widgets.gameplay_widget import GameplayWidget
from src.ui.widgets.history_widget import HistoryWidget
from src.ui.widgets.window_title_bar import WindowTitleBar


class MainWindow(QMainWindow):

    translation_received = pyqtSignal(object)
    voice_received = pyqtSignal(object)

    def __init__(self, container: Container) -> None:
        super().__init__()

        self.container = container
        self.logger = LoggerManager.get_logger("MainWindow")
        self._tabs: QTabWidget | None = None
        self._central_layout: QVBoxLayout | None = None
        self._header_panel: QWidget | None = None
        self._title_bar: WindowTitleBar | None = None
        self._size_grip: QSizeGrip | None = None
        self._toolbar: QToolBar | None = None
        self._geometry_dirty = False

        apply_theme(self)
        self.setWindowTitle("Diablo Translator")
        self.setup_ui()
        self.setup_toolbar()
        self._auto_configure_for_game()
        self.apply_window_behavior()
        self.update_status_bar()

        self.translation_received.connect(self.on_live_translation)
        self.voice_received.connect(self.on_voice_result)
        self.container.set_translation_listener(
            self.translation_received.emit
        )
        self.container.set_status_listener(self.on_ocr_status)
        self.container.set_voice_listener(
            self.voice_received.emit
        )

        self._game_timer = QTimer(self)
        self._game_timer.setInterval(2500)
        self._game_timer.timeout.connect(self._on_game_timer)
        self._game_timer.start()

    def setup_ui(self) -> None:
        self._header_panel = self._build_header()
        self._title_bar = WindowTitleBar(self, title="Diablo Translator — Overlay")
        self._title_bar.close_requested.connect(self.close)
        self._title_bar.minimize_requested.connect(self.showMinimized)
        self._tabs = QTabWidget()

        sanctuary = self._build_sanctuary_tab()
        gameplay = GameplayWidget(
            self.container,
            on_status_update=self.update_status_bar,
        )
        gameplay.open_settings_requested.connect(self.open_settings)
        history = HistoryWidget(self.container)

        self._tabs.addTab(sanctuary, "Sanctuaire")
        self._tabs.addTab(gameplay, "Gameplay")
        self._tabs.addTab(history, "Grimoire")

        central = QWidget()
        self._central_layout = QVBoxLayout()
        self._central_layout.setContentsMargins(16, 16, 16, 8)
        self._central_layout.setSpacing(12)
        self._central_layout.addWidget(self._title_bar)
        self._central_layout.addWidget(self._header_panel)
        self._central_layout.addWidget(self._tabs, stretch=1)
        central.setLayout(self._central_layout)

        self.gameplay_widget = gameplay
        self._size_grip = QSizeGrip(central)
        grip_row = QHBoxLayout()
        grip_row.addStretch()
        grip_row.addWidget(self._size_grip, alignment=Qt.AlignmentFlag.AlignRight)
        self._central_layout.addLayout(grip_row)
        self.setCentralWidget(central)

    def setup_toolbar(self) -> None:
        toolbar = QToolBar("Actions rapides")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        self._toolbar = toolbar

        self.game_mode_action = QAction("Mode Jeu", self)
        self.game_mode_action.setCheckable(True)
        self.game_mode_action.setChecked(self.container.config.overlay_compact)
        self.game_mode_action.setToolTip(
            "Overlay compact sur le chat Diablo (bas gauche)"
        )
        self.game_mode_action.toggled.connect(self.toggle_game_mode)
        toolbar.addAction(self.game_mode_action)

        top_action = QAction("Toujours devant", self)
        top_action.setCheckable(True)
        top_action.setChecked(self.container.config.always_on_top)
        top_action.toggled.connect(self.toggle_always_on_top)
        toolbar.addAction(top_action)
        self._always_on_top_action = top_action

        monitor_action = QAction(
            AssetManager.icon("play"),
            "Surveiller le chat",
            self,
        )
        monitor_action.triggered.connect(self.gameplay_widget.start_worker)
        toolbar.addAction(monitor_action)

        stop_action = QAction(AssetManager.icon("stop"), "Arrêter", self)
        stop_action.triggered.connect(self.gameplay_widget.stop_worker)
        toolbar.addAction(stop_action)

        translate_action = QAction(
            AssetManager.icon("translate"),
            "Traduire",
            self,
        )
        translate_action.triggered.connect(self.gameplay_widget.translate_chat_message)
        toolbar.addAction(translate_action)

        settings_action = QAction(
            AssetManager.icon("settings"),
            "Paramètres",
            self,
        )
        settings_action.triggered.connect(self.open_settings)
        toolbar.addAction(settings_action)

    def _auto_configure_for_game(self) -> None:
        if not self.container.game_session.prepare_overlay_if_game_running():
            return

        self.game_mode_action.blockSignals(True)
        self.game_mode_action.setChecked(True)
        self.game_mode_action.blockSignals(False)
        self._always_on_top_action.blockSignals(True)
        self._always_on_top_action.setChecked(True)
        self._always_on_top_action.blockSignals(False)

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
        if self._header_panel is not None:
            self._header_panel.setVisible(not compact)
        if self._toolbar is not None:
            self._toolbar.setVisible(not compact)
        self.menuBar().setVisible(not compact)
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
            self._always_on_top_action.blockSignals(True)
            self._always_on_top_action.setChecked(True)
            self._always_on_top_action.blockSignals(False)
        else:
            self.container.config_service.replace(config)
        self.apply_window_behavior()
        self.update_status_bar()

    def toggle_always_on_top(self, enabled: bool) -> None:
        config = self.container.config_service.config
        config.always_on_top = enabled
        self.container.config_service.replace(config)
        self.apply_window_behavior()

    def _user_is_editing(self) -> bool:
        focused = QApplication.focusWidget()
        if focused is None:
            return False

        chat_input = self.gameplay_widget.chat_input
        return focused is chat_input or chat_input.isAncestorOf(focused)

    def _on_game_timer(self) -> None:
        status = self.container.game_detection.scan()
        if not status.is_any_running:
            return

        if (
            self.container.config.auto_start_monitor
            and not self.container.worker.is_running
            and self.container.config.chat_monitor_enabled
        ):
            self.gameplay_widget.start_worker(auto=True)

    def _build_header(self) -> QWidget:
        title = QLabel("DIABLO TRANSLATOR")
        title.setObjectName("AppTitle")
        title.setFont(AssetManager.ui_font(24, bold=True))

        subtitle = QLabel(
            "Overlay chat · Traduction live · Sans voler le focus du jeu"
        )
        subtitle.setObjectName("AppSubtitle")

        title_block = QVBoxLayout()
        title_block.addWidget(title)
        title_block.addWidget(subtitle)

        settings_button = QPushButton(" Paramètres")
        settings_button.setIcon(AssetManager.icon("settings"))
        settings_button.clicked.connect(self.open_settings)

        header = QHBoxLayout()
        header.addLayout(title_block)
        header.addStretch()
        header.addWidget(settings_button, alignment=Qt.AlignmentFlag.AlignTop)

        panel = QWidget()
        panel.setLayout(header)
        return panel

    def _build_sanctuary_tab(self) -> QWidget:
        widget = QWidget()
        widget.setObjectName("SanctuaryRoot")

        panel = QFrame()
        panel.setObjectName("Panel")
        layout = QVBoxLayout()

        intro = QLabel(
            "Mode Jeu (recommandé pendant Diablo) :\n\n"
            "• Fenêtre Windows : déplacer, redimensionner, fermer (barre native)\n"
            "• Overlay compact au-dessus du chat (bas gauche)\n"
            "• Position mémorisée à la fermeture\n"
            "• Compatible plein écran exclusif et borderless\n"
            "• Capture OCR sur le moniteur du jeu automatiquement\n"
            "• Surveillance OCR automatique au lancement du jeu\n"
            "• Messages étrangers → français affiché sur l'overlay\n"
            "• Vous écrivez en français → traduction copiée (coller en jeu)\n\n"
            "Paramètres → Overlay : barre Windows native ON/OFF"
        )
        intro.setWordWrap(True)
        intro.setObjectName("MutedText")

        layout.addWidget(self._section_title("SANCTUAIRE"))
        layout.addWidget(intro)
        layout.addStretch()
        panel.setLayout(layout)

        root = QVBoxLayout()
        root.addWidget(panel)
        widget.setLayout(root)
        return widget

    @staticmethod
    def _section_title(text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("SectionTitle")
        return label

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

    def open_settings(self) -> None:
        updated = SettingsDialog.edit(self.container.config, parent=self)
        if updated is None:
            return

        self.container.apply_config(updated)
        self.game_mode_action.setChecked(updated.overlay_compact)
        self._always_on_top_action.setChecked(updated.always_on_top)
        self.apply_window_behavior()
        self.gameplay_widget.refresh_game_status()
        self.update_status_bar()
        self.logger.info("Paramètres mis à jour")

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
