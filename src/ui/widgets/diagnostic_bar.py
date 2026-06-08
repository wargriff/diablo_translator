from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.infrastructure.asset_manager import AssetManager
from src.ui.services.diagnostic_service import DiagnosticService


class DiagnosticBar(QWidget):

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("DiagnosticBar")
        self._service = DiagnosticService.instance()

        icon = QLabel()
        icon.setPixmap(AssetManager.app_icon().pixmap(20, 20))

        self._status_label = QLabel(self._service.status_line)
        self._status_label.setObjectName("MutedText")
        self._status_label.setWordWrap(True)

        self._details_button = QPushButton(" Journal")
        self._details_button.setObjectName("CompactOcrButton")
        self._details_button.setIcon(AssetManager.icon("settings"))
        self._details_button.setToolTip("Voir le journal des erreurs et événements")
        self._details_button.clicked.connect(self._open_journal)

        row = QHBoxLayout()
        row.setContentsMargins(8, 4, 8, 4)
        row.setSpacing(8)
        row.addWidget(icon)
        row.addWidget(self._status_label, stretch=1)
        row.addWidget(self._details_button)
        self.setLayout(row)

        self._service.status_changed.connect(self._status_label.setText)
        self._service.event_added.connect(self._on_event)

    def _on_event(self, event) -> None:
        if event.level in {"error", "critical"}:
            self._status_label.setStyleSheet("color: #e57373;")
        else:
            self._status_label.setStyleSheet("")

    def _open_journal(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Diablo Translator — Journal diagnostic")
        dialog.setMinimumSize(520, 360)
        dialog.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        text = QTextEdit()
        text.setReadOnly(True)
        text.setFont(AssetManager.monospace_font(9))
        lines: list[str] = []
        for event in self._service.events():
            prefix = event.level.upper()
            line = f"[{prefix}] {event.source}: {event.message}"
            if event.detail:
                line += f"\n    {event.detail}"
            lines.append(line)
        text.setPlainText("\n\n".join(lines) if lines else "Aucun événement pour le moment.")

        close_button = QPushButton("Fermer")
        close_button.clicked.connect(dialog.accept)

        layout = QVBoxLayout()
        layout.addWidget(text)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignRight)
        dialog.setLayout(layout)
        dialog.exec()
