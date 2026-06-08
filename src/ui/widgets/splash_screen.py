from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPixmap
from PyQt6.QtWidgets import QSplashScreen


def create_startup_splash() -> QSplashScreen:
    pixmap = QPixmap(460, 150)
    pixmap.fill(QColor("#151210"))

    painter = QPainter(pixmap)
    painter.setPen(QColor("#d4af37"))
    painter.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "Diablo Translator")
    painter.setPen(QColor("#8a8278"))
    painter.setFont(QFont("Segoe UI", 10))
    painter.drawText(
        0,
        92,
        pixmap.width(),
        40,
        Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
        "Chargement…",
    )
    painter.end()

    splash = QSplashScreen(pixmap)
    splash.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
    return splash
