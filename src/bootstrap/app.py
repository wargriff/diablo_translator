import os
import sys

from PyQt6.QtCore import QThread, QTimer, pyqtSignal
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


class _ContainerLoader(QThread):

    loaded = pyqtSignal(object)

    def run(self) -> None:
        self.loaded.emit(Container())


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
        splash.set_progress(8, "Démarrage…")

        if warn_if_already_running():
            splash.close()
            return

        splash.set_progress(18, "Chargement des services…")
        loader = _ContainerLoader()

        def on_container_loaded(container: Container) -> None:
            self.container = container
            splash.set_progress(55, "Ressources…")
            AssetManager.prepare()
            app.setWindowIcon(AssetManager.app_icon())
            app.setFont(AssetManager.ui_font(10))

            splash.set_progress(82, "Interface…")
            window = MainWindow(container)
            window.show()

            splash.set_progress(100, "Prêt")
            splash.finish(window)

            delay_ms = max(container.config.startup_delay_seconds, 1) * 1000
            QTimer.singleShot(delay_ms, window.enable_background_services)

        loader.loaded.connect(on_container_loaded)
        loader.start()

        sys.exit(app.exec())
