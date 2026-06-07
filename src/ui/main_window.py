from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
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

        apply_theme(self)
        self.setWindowTitle("Diablo Translator")
        self.resize(1480, 940)
        self.setup_ui()
        self.setup_toolbar()
        self.update_status_bar()

        self.translation_received.connect(self.on_live_translation)
        self.voice_received.connect(self.on_voice_result)
        self.container.set_translation_listener(
            self.translation_received.emit
        )
        self.container.set_voice_listener(
            self.voice_received.emit
        )

    def setup_ui(self) -> None:
        header = self._build_header()
        tabs = QTabWidget()

        sanctuary = self._build_sanctuary_tab()
        gameplay = GameplayWidget(
            self.container,
            on_status_update=self.update_status_bar,
        )
        history = HistoryWidget(self.container)

        tabs.addTab(sanctuary, "Sanctuaire")
        tabs.addTab(gameplay, "Gameplay")
        tabs.addTab(history, "Grimoire")

        central = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 8)
        layout.setSpacing(12)
        layout.addLayout(header)
        layout.addWidget(tabs, stretch=1)
        central.setLayout(layout)

        self.gameplay_widget = gameplay
        self.setCentralWidget(central)

    def setup_toolbar(self) -> None:
        toolbar = QToolBar("Actions rapides")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

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
        translate_action.setShortcut("Ctrl+Return")
        translate_action.triggered.connect(self.gameplay_widget.translate_chat_message)
        toolbar.addAction(translate_action)

        settings_action = QAction(
            AssetManager.icon("settings"),
            "Paramètres",
            self,
        )
        settings_action.triggered.connect(self.open_settings)
        toolbar.addAction(settings_action)

    def _build_header(self) -> QHBoxLayout:
        title = QLabel("DIABLO TRANSLATOR")
        title.setObjectName("AppTitle")
        title.setFont(AssetManager.ui_font(24, bold=True))

        subtitle = QLabel(
            "Chat live · DeepL/Google · Détection langue · Cache persistant"
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
            "Structure pro optimisée :\n\n"
            "• assets/ — thèmes, icônes, polices\n"
            "• cache/ — traductions persistées\n"
            "• models/ — modèles OCR locaux\n"
            "• build/ — compilation PyInstaller\n"
            "• tests/ — tests unitaires\n\n"
            "Raccourcis : Ctrl+Entrée traduire · Ctrl+M micro · F5 actualiser"
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

        game_text = (
            status.summary()
            if status.is_any_running
            else "Aucun jeu Diablo actif"
        )
        message = (
            f"{game_text}  |  Moteur: {provider}  |  "
            f"Cache: {cache.entries} entrées ({cache.hits} hits / {cache.misses} miss)"
        )
        self.statusBar().showMessage(message)

    def open_settings(self) -> None:
        updated = SettingsDialog.edit(self.container.config, parent=self)
        if updated is None:
            return

        self.container.apply_config(updated)
        self.gameplay_widget.refresh_game_status()
        self.update_status_bar()
        self.logger.info("Paramètres mis à jour")

    def on_live_translation(self, result: TranslationResult) -> None:
        self.gameplay_widget.show_live_translation(result)
        self.update_status_bar()

    def on_voice_result(self, payload) -> None:
        self.gameplay_widget.handle_voice_result(payload)
        self.update_status_bar()

    def closeEvent(self, event) -> None:
        self.gameplay_widget.shutdown()
        super().closeEvent(event)
