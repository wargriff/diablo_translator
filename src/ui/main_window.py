
from PyQt6.QtWidgets import (
    QLabel,
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout,
)

from src.infrastructure.logger import (
    LoggerManager
)


class MainWindow(QMainWindow):

    def __init__(
        self,
        container
    ):
        super().__init__()

        self.container = container

        self.logger = (
            LoggerManager.get_logger(
                "MainWindow"
            )
        )

        self.setWindowTitle(
            "Diablo III Translator"
        )

        self.resize(
            1400,
            900
        )

        self.setup_ui()

    def setup_ui(self):

        tabs = QTabWidget()

        home = QWidget()

        layout = QVBoxLayout()

        title = QLabel(
            "Diablo III Translator Professional"
        )

        layout.addWidget(
            title
        )

        home.setLayout(
            layout
        )

        tabs.addTab(
            home,
            "Accueil"
        )

        self.setCentralWidget(
            tabs
        )
