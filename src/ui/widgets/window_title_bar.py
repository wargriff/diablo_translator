from __future__ import annotations

from PyQt6.QtCore import QPoint, Qt, pyqtSignal
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QWidget,
)

from src.infrastructure.asset_manager import AssetManager


class WindowTitleBar(QWidget):
    """Barre de titre style Windows pour mode overlay sans bordure native."""

    close_requested = pyqtSignal()
    minimize_requested = pyqtSignal()
    maximize_requested = pyqtSignal()

    def __init__(
        self,
        window: QMainWindow,
        *,
        title: str = "Diablo Translator",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("WindowTitleBar")
        self._window = window
        self._drag_offset: QPoint | None = None
        self._maximized = False
        self._restore_geometry = None

        icon = QLabel()
        icon.setPixmap(AssetManager.app_icon().pixmap(16, 16))
        icon.setFixedSize(18, 18)

        self._title_label = QLabel(title)
        self._title_label.setObjectName("WindowTitleText")

        self._min_button = self._make_button("—", "Réduire")
        self._max_button = self._make_button("□", "Agrandir / Restaurer")
        self._close_button = self._make_button("✕", "Fermer")
        self._close_button.setObjectName("WindowCloseButton")

        self._min_button.clicked.connect(self.minimize_requested.emit)
        self._max_button.clicked.connect(self._toggle_maximize)
        self._close_button.clicked.connect(self.close_requested.emit)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(icon)
        layout.addWidget(self._title_label)
        layout.addStretch()
        layout.addWidget(self._min_button)
        layout.addWidget(self._max_button)
        layout.addWidget(self._close_button)
        self.setLayout(layout)
        self.setFixedHeight(36)

    @staticmethod
    def _make_button(text: str, tooltip: str) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName("WindowControlButton")
        button.setToolTip(tooltip)
        button.setFixedSize(46, 28)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        return button

    def set_title(self, text: str) -> None:
        self._title_label.setText(text)

    def _toggle_maximize(self) -> None:
        if self._maximized:
            if self._restore_geometry is not None:
                self._window.setGeometry(self._restore_geometry)
            self._max_button.setText("□")
            self._maximized = False
            return

        self._restore_geometry = self._window.geometry()
        screen = self._window.screen()
        if screen is not None:
            self._window.setGeometry(screen.availableGeometry())
        self._max_button.setText("❐")
        self._maximized = True
        self.maximize_requested.emit()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = (
                event.globalPosition().toPoint() - self._window.frameGeometry().topLeft()
            )
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if (
            self._drag_offset is not None
            and event.buttons() & Qt.MouseButton.LeftButton
            and not self._maximized
        ):
            self._window.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_offset = None
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._toggle_maximize()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)
