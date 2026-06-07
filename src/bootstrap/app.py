import sys

from PyQt6.QtWidgets import QApplication

from src.infrastructure import LoggerManager
from src.infrastructure.container import Container
from src.ui.main_window import MainWindow


class Application:

    def __init__(self) -> None:
        LoggerManager.setup()
        self.container = Container()

    def run(self) -> None:
        app = QApplication(sys.argv)
        window = MainWindow(self.container)
        window.show()
        sys.exit(app.exec())
