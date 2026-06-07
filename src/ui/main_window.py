from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
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


class MainWindow(QMainWindow):

    translation_received = pyqtSignal(object)
    voice_received = pyqtSignal(object)

    def __init__(self, container: Container) -> None:
        super().__init__()

        self.container = container
        self.logger = LoggerManager.get_logger("MainWindow")
        self._tabs: QTabWidget | None = None

        apply_theme(self)
        self.setWindowTitle("Diablo Translator")
        self.setup_ui()
        self.setup_toolbar()
        self.apply_window_behavior()
        self.update_status_bar()

        self.translation_received.connect(self.on_live_translation)
        self.voice_received.connect(self.on_voice_result)
        self.container.set_translation_listener(
            self.translation_received.emit
        )
        self.container.set_voice_listener(
            self.voice_received.emit
        )

        self._game_timer = QTimer(self)
        self._game_timer.setInterval(2500)
        self._game_timer.timeout.connect(self._on_game_timer)
        self._game_timer.start()

    def setup_ui(self) -> None:
        header = self._build_header()
        self._tabs = QTabWidget()

        sanctuary = self._build_sanctuary_tab()
        gameplay = GameplayWidget(
            self.container,
            on_status_update=self.update_status_bar,
        )
        history = HistoryWidget(self.container)

        self._tabs.addTab(sanctuary, "Sanctuaire")
        self._tabs.addTab(gameplay, "Gameplay")
        self._tabs.addTab(history, "Grimoire")

        central = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 8)
        layout.setSpacing(12)
        layout.addLayout(header)
        layout.addWidget(self._tabs, stretch=1)
        central.setLayout(layout)

        self.gameplay_widget = gameplay
        self.setCentralWidget(central)

    def setup_toolbar(self) -> None:
        toolbar = QToolBar("Actions rapides")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        self.game_mode_action = QAction("Mode Jeu", self)
        self.game_mode_action.setCheckable(True)
        self.game_mode_action.setChecked(self.container.config.overlay_compact)
        self.game_mode_action.setToolTip(
            "Fenêtre compacte, transparente et toujours devant le jeu"
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

    def apply_window_behavior(self) -> None:
        config = self.container.config
        font = AssetManager.ui_font(config.ui_font_size)
        self.setFont(font)
        self.gameplay_widget.chat_log.setFont(
            AssetManager.monospace_font(config.ui_font_size)
        )
        WindowBehaviorService.apply(self, config)

    def toggle_game_mode(self, enabled: bool) -> None:
        self.container.config.overlay_compact = enabled
        if enabled:
            self.container.config.overlay_enabled = True
            self.container.config.always_on_top = True
            self._always_on_top_action.blockSignals(True)
            self._always_on_top_action.setChecked(True)
            self._always_on_top_action.blockSignals(False)
        self.apply_window_behavior()
        self.update_status_bar()

    def toggle_always_on_top(self, enabled: bool) -> None:
        self.container.config.always_on_top = enabled
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

        if self.container.config.auto_raise_on_game and not self._user_is_editing():
            WindowBehaviorService.raise_if_game_mode(self, self.container.config)

        if (
            self.container.config.auto_start_monitor
            and not self.container.worker.is_running
            and self.container.config.chat_monitor_enabled
        ):
            self.gameplay_widget.start_worker(auto=True)

    def _build_header(self) -> QHBoxLayout:
        title = QLabel("DIABLO TRANSLATOR")
        title.setObjectName("AppTitle")
        title.setFont(AssetManager.ui_font(24, bold=True))

        subtitle = QLabel(
            "Overlay transparent · Toujours devant · Chat live OCR"
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
        return header

    def _build_sanctuary_tab(self) -> QWidget:
        widget = QWidget()
        widget.setObjectName("SanctuaryRoot")

        panel = QFrame()
        panel.setObjectName("Panel")
        layout = QVBoxLayout()

        intro = QLabel(
            "Mode Jeu recommandé pendant Diablo :\n\n"
            "• Fenêtre compacte et transparente\n"
            "• Toujours devant le jeu (sans Alt+Entrée)\n"
            "• Surveillance chat automatique\n"
            "• Opacité réglable dans Paramètres → Overlay\n\n"
            "Raccourcis (hors champ de saisie) : Ctrl+Shift+M · Ctrl+Shift+R\n"
            "Dans le champ chat : Ctrl+Entrée pour traduire"
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
        if not self._user_is_editing():
            WindowBehaviorService.raise_if_game_mode(self, self.container.config)

    def on_voice_result(self, payload) -> None:
        self.gameplay_widget.handle_voice_result(payload)
        self.update_status_bar()

    def closeEvent(self, event) -> None:
        self.gameplay_widget.shutdown()
        super().closeEvent(event)
