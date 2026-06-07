import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from src.infrastructure import LoggerManager
from src.infrastructure.asset_manager import AssetManager
from src.infrastructure.container import Container
from src.infrastructure.paths import ensure_project_dirs
from src.ui.main_window import MainWindow


class Application:

    def __init__(self) -> None:
        ensure_project_dirs()
        LoggerManager.setup()
        self.container = Container()

    def run(self) -> None:
        app = QApplication(sys.argv)
        app.setApplicationName("Diablo Translator")
        app.setOrganizationName("DiabloTranslator")
        app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

        AssetManager.prepare()
        app.setWindowIcon(AssetManager.app_icon())
        app.setFont(AssetManager.ui_font(10))

        window = MainWindow(self.container)
        window.show()
        sys.exit(app.exec())
