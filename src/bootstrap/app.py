import os
import sys

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication

from src.infrastructure import LoggerManager
from src.infrastructure.asset_manager import AssetManager
from src.infrastructure.container import Container
from src.infrastructure.paths import ensure_project_dirs
from src.ui.main_window import MainWindow
from src.ui.widgets.splash_screen import create_startup_splash


def _configure_fast_startup() -> None:
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")


class Application:

    def __init__(self) -> None:
        _configure_fast_startup()
        ensure_project_dirs()
        LoggerManager.setup()
        self.container: Container | None = None

    def run(self) -> None:
        from src.infrastructure.single_instance import warn_if_already_running

        app = QApplication(sys.argv)
        app.setApplicationName("Diablo Translator")
        app.setOrganizationName("DiabloTranslator")

        splash = create_startup_splash()
        splash.show()
        app.processEvents()

        if warn_if_already_running():
            splash.close()
            return

        splash.showMessage(
            "Initialisation des services…",
            alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
            color="#d4af37",
        )
        app.processEvents()

        self.container = Container()

        AssetManager.prepare()
        app.setWindowIcon(AssetManager.app_icon())
        app.setFont(AssetManager.ui_font(10))

        splash.showMessage(
            "Préparation de l'interface…",
            alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
            color="#d4af37",
        )
        app.processEvents()

        window = MainWindow(self.container)
        window.show()
        splash.finish(window)

        delay_ms = max(self.container.config.startup_delay_seconds, 1) * 1000
        QTimer.singleShot(delay_ms, window.enable_background_services)
        sys.exit(app.exec())
