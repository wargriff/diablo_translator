from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)


class StartupSplash(QWidget):

    _STYLESHEET = """
    QWidget#StartupSplashRoot {
        background-color: #151210;
        border: 1px solid #5c4a32;
        border-top: 2px solid #b8860b;
    }
    QLabel#SplashTitle {
        color: #d4af37;
        font-size: 20px;
        font-weight: 700;
    }
    QLabel#SplashStatus {
        color: #8a8278;
        font-size: 11px;
    }
    QLabel#SplashPercent {
        color: #b8860b;
        font-size: 10px;
        font-weight: 600;
    }
    QProgressBar#SplashProgress {
        background-color: #0f0d0b;
        border: 1px solid #3d3428;
        border-radius: 4px;
        min-height: 14px;
        max-height: 14px;
        text-visible: false;
    }
    QProgressBar#SplashProgress::chunk {
        background-color: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0 #6b1a1a,
            stop:0.45 #b8860b,
            stop:1 #d4af37
        );
        border-radius: 3px;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("StartupSplashRoot")
        self.setWindowFlags(
            Qt.WindowType.SplashScreen
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setFixedSize(500, 210)
        self.setStyleSheet(self._STYLESHEET)

        self._title = QLabel("Diablo Translator")
        self._title.setObjectName("SplashTitle")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._status = QLabel("Chargement…")
        self._status.setObjectName("SplashStatus")
        self._status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status.setWordWrap(True)

        self._percent = QLabel("0 %")
        self._percent.setObjectName("SplashPercent")
        self._percent.setAlignment(Qt.AlignmentFlag.AlignRight)

        self._progress = QProgressBar()
        self._progress.setObjectName("SplashProgress")
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setTextVisible(False)

        layout = QVBoxLayout()
        layout.setContentsMargins(28, 24, 28, 22)
        layout.setSpacing(10)
        layout.addStretch()
        layout.addWidget(self._title)
        layout.addSpacing(6)
        layout.addWidget(self._status)
        layout.addWidget(self._percent)
        layout.addWidget(self._progress)
        self.setLayout(layout)

    def center_on_screen(self) -> None:
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return
        frame = self.frameGeometry()
        frame.moveCenter(screen.availableGeometry().center())
        self.move(frame.topLeft())

    def set_progress(self, value: int, message: str) -> None:
        clamped = max(0, min(100, value))
        self._progress.setValue(clamped)
        self._percent.setText(f"{clamped} %")
        self._status.setText(message)
        app = QApplication.instance()
        if app is not None:
            app.processEvents()

    def finish(self, window: QWidget | None = None) -> None:
        self.set_progress(100, "Prêt")
        if window is not None:
            window.raise_()
            window.activateWindow()
        self.close()


def create_startup_splash() -> StartupSplash:
    splash = StartupSplash()
    splash.center_on_screen()
    return splash
