import os
import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from src.infrastructure import LoggerManager
from src.infrastructure.agent_debug_log import agent_log, log_paths, register_listener
from src.infrastructure.asset_manager import AssetManager
from src.infrastructure.container import Container
from src.infrastructure.paths import ensure_project_dirs
from src.ui.main_window import MainWindow
from src.ui.services.diagnostic_service import DiagnosticService
from src.ui.services.ui_thread_bridge import UiThreadBridge
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

        # #region agent log
        agent_log(
            "bootstrap/app.py:run",
            "Application demarree",
            hypothesis_id="D",
            run_id="user-verify",
            data={
                "frozen": getattr(sys, "frozen", False),
                "executable": sys.executable,
            },
        )
        # #endregion

        ui_bridge = UiThreadBridge()
        diagnostics = DiagnosticService.instance()

        def _handle_agent_log(payload: dict) -> None:
            level = "error" if payload.get("hypothesisId") in {"A", "B", "D"} else "info"
            if "error" in payload.get("message", "").lower():
                level = "error"
            diagnostics.record(
                payload.get("location", "debug"),
                payload.get("message", ""),
                level=level,
                detail=str(payload.get("data", {})),
            )

        ui_bridge.agent_log_payload.connect(_handle_agent_log)
        register_listener(ui_bridge.agent_log_payload.emit)
        diagnostics.record(
            "Debug",
            "Journal actif",
            level="info",
            detail=" | ".join(log_paths()),
        )

        def _qt_excepthook(exc_type, exc, tb) -> None:
            import traceback

            detail = "".join(traceback.format_exception(exc_type, exc, tb))
            agent_log(
                "bootstrap/app.py:qt_excepthook",
                "Exception Qt non geree",
                hypothesis_id="D",
                data={"error": str(exc), "traceback": detail[-800:]},
            )
            diagnostics.record(
                "Qt",
                f"Crash interface : {exc}",
                level="critical",
                detail=detail[-1200:],
            )
            sys.__excepthook__(exc_type, exc, tb)

        sys.excepthook = _qt_excepthook

        splash = create_startup_splash()
        splash.show()
        splash.set_progress(8, "Démarrage…")
        app.processEvents()

        if warn_if_already_running():
            splash.close()
            return

        splash.set_progress(18, "Chargement des services…")
        app.processEvents()

        container = Container(ui_bridge=ui_bridge)
        self.container = container

        splash.set_progress(55, "Ressources…")
        app.processEvents()
        AssetManager.prepare()
        app.setWindowIcon(AssetManager.app_icon())
        app.setFont(AssetManager.ui_font(10))

        splash.set_progress(82, "Interface…")
        app.processEvents()
        window = MainWindow(container)
        window.show()

        splash.set_progress(100, "Prêt")
        splash.finish(window)

        delay_ms = max(container.config.startup_delay_seconds, 0) * 1000
        if delay_ms == 0:
            window.enable_background_services()
        else:
            QTimer.singleShot(delay_ms, window.enable_background_services)

        sys.exit(app.exec())
