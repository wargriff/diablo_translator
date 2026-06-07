from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
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
from src.ui.widgets import HistoryWidget, StatusWidget


class MainWindow(QMainWindow):

    translation_received = pyqtSignal(str)

    def __init__(self, container: Container) -> None:
        super().__init__()

        self.container = container
        self.logger = LoggerManager.get_logger("MainWindow")

        self.setWindowTitle("Diablo III Translator")
        self.resize(1400, 900)
        self.setup_ui()

        self.translation_received.connect(self.on_translation)
        self.container.set_translation_listener(
            self.translation_received.emit
        )

    def setup_ui(self) -> None:
        tabs = QTabWidget()

        home = self._build_home_tab()
        status = StatusWidget(self.container)
        history = HistoryWidget(self.container)

        tabs.addTab(home, "Accueil")
        tabs.addTab(status, "Traduction")
        tabs.addTab(history, "Historique")

        settings_button = QPushButton("Paramètres")
        settings_button.clicked.connect(self.open_settings)

        central = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(tabs)
        layout.addWidget(settings_button, alignment=Qt.AlignmentFlag.AlignRight)
        central.setLayout(layout)

        self.status_widget = status
        self.setCentralWidget(central)

    def _build_home_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Diablo III Translator Professional")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")

        info = QLabel(
            "Programmes disponibles via launcher.py :\n"
            "  gui | check | translate | game | export | stats"
        )

        layout.addWidget(title)
        layout.addWidget(info)
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def open_settings(self) -> None:
        updated = SettingsDialog.edit(self.container.config, parent=self)
        if updated is None:
            return

        self.container.config = updated
        self.logger.info("Paramètres mis à jour")

    def on_translation(self, text: str) -> None:
        self.status_widget.show_translation(text)

    def closeEvent(self, event) -> None:
        self.container.worker.stop()
        super().closeEvent(event)
