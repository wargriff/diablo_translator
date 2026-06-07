
import sys

from PyQt6.QtWidgets import QApplication

from src.infrastructure.container import Container
from src.infrastructure.logger import LoggerManager
from src.ui.main_window import MainWindow


class Application:

    def __init__(self):

        LoggerManager.setup()

        self.container = Container()

    def run(self):

        app = QApplication(sys.argv)

        window = MainWindow(
            self.container
        )

        window.show()

        sys.exit(app.exec())
