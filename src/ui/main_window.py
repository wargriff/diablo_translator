from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.infrastructure import LoggerManager
from src.infrastructure.container import Container
from src.ui.dialogs import SettingsDialog
from src.ui.theme import apply as apply_theme
from src.ui.widgets.gameplay_widget import GameplayWidget
from src.ui.widgets.history_widget import HistoryWidget


class MainWindow(QMainWindow):

    translation_received = pyqtSignal(str)

    def __init__(self, container: Container) -> None:
        super().__init__()

        self.container = container
        self.logger = LoggerManager.get_logger("MainWindow")

        apply_theme(self)
        self.setWindowTitle("Diablo Translator")
        self.resize(1440, 920)
        self.setup_ui()

        self.translation_received.connect(self.on_live_translation)
        self.container.set_translation_listener(
            self.translation_received.emit
        )

    def setup_ui(self) -> None:
        header = self._build_header()
        tabs = QTabWidget()

        sanctuary = self._build_sanctuary_tab()
        gameplay = GameplayWidget(self.container)
        history = HistoryWidget(self.container)

        tabs.addTab(sanctuary, "Sanctuaire")
        tabs.addTab(gameplay, "Gameplay")
        tabs.addTab(history, "Grimoire")

        central = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        layout.addLayout(header)
        layout.addWidget(tabs, stretch=1)
        central.setLayout(layout)

        self.gameplay_widget = gameplay
        self.setCentralWidget(central)

    def _build_header(self) -> QHBoxLayout:
        title = QLabel("DIABLO TRANSLATOR")
        title.setObjectName("AppTitle")

        subtitle = QLabel("Traduction chat & capture — D3 · D4 · Immortal")
        subtitle.setObjectName("AppSubtitle")

        title_block = QVBoxLayout()
        title_block.addWidget(title)
        title_block.addWidget(subtitle)

        settings_button = QPushButton("Paramètres")
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
            "Bienvenue dans le Sanctuaire.\n\n"
            "L'onglet Gameplay détecte Diablo III, Diablo IV et Diablo Immortal, "
            "permet de tester la traduction du chat en direct, "
            "et lance la capture automatique quand un jeu est actif."
        )
        intro.setWordWrap(True)
        intro.setObjectName("MutedText")

        commands = QLabel(
            "Commandes CLI :\n"
            "  python launcher.py gui\n"
            "  python launcher.py game\n"
            "  python launcher.py translate \"hello\""
        )
        commands.setObjectName("MutedText")

        layout.addWidget(self._section_title("SANCTUAIRE"))
        layout.addWidget(intro)
        layout.addWidget(commands)
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

    def open_settings(self) -> None:
        updated = SettingsDialog.edit(self.container.config, parent=self)
        if updated is None:
            return

        self.container.config = updated
        self.logger.info("Paramètres mis à jour")

    def on_live_translation(self, text: str) -> None:
        self.gameplay_widget.show_live_translation(text)

    def closeEvent(self, event) -> None:
        self.container.worker.stop()
        super().closeEvent(event)
