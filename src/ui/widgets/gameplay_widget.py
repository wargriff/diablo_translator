from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.infrastructure.container import Container
from src.ui.widgets.game_status_panel import GameStatusPanel


class GameplayWidget(QWidget):

    def __init__(self, container: Container) -> None:
        super().__init__()
        self.setObjectName("GameplayRoot")
        self.container = container
        self.worker = container.worker

        self.game_status = GameStatusPanel(container)
        self.chat_log = QTextEdit()
        self.chat_log.setObjectName("ChatLog")
        self.chat_log.setReadOnly(True)
        self.chat_log.setMinimumHeight(260)

        chat_font = QFont("Cascadia Mono", 10)
        chat_font.setStyleHint(QFont.StyleHint.Monospace)
        self.chat_log.setFont(chat_font)

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText(
            "Tapez un message de chat pour tester la traduction..."
        )
        self.chat_input.returnPressed.connect(self.translate_chat_message)

        self.translate_button = QPushButton("Traduire")
        self.translate_button.setObjectName("PrimaryButton")
        self.translate_button.clicked.connect(self.translate_chat_message)

        self.start_button = QPushButton("Démarrer capture auto")
        self.stop_button = QPushButton("Arrêter capture")
        self.refresh_button = QPushButton("Actualiser")

        self.last_translation_label = QLabel("Dernière traduction : en attente...")
        self.last_translation_label.setObjectName("MutedText")
        self.last_translation_label.setWordWrap(True)

        self.auto_status_label = QLabel("Capture automatique : arrêtée")
        self.auto_status_label.setObjectName("MutedText")

        self.start_button.clicked.connect(self.start_worker)
        self.stop_button.clicked.connect(self.stop_worker)
        self.refresh_button.clicked.connect(self.refresh_game_status)

        input_row = QHBoxLayout()
        input_row.addWidget(self.chat_input, stretch=1)
        input_row.addWidget(self.translate_button)

        auto_row = QHBoxLayout()
        auto_row.addWidget(self.start_button)
        auto_row.addWidget(self.stop_button)
        auto_row.addWidget(self.refresh_button)
        auto_row.addStretch()

        chat_panel = QFrame()
        chat_panel.setObjectName("ChatPanel")
        chat_layout = QVBoxLayout()
        chat_layout.addWidget(self.chat_log)
        chat_panel.setLayout(chat_layout)

        layout = QVBoxLayout()
        layout.setSpacing(14)
        layout.addWidget(self.game_status)
        layout.addWidget(self._section_title("CHAT — TEST DE TRADUCTION"))
        layout.addWidget(chat_panel)
        layout.addLayout(input_row)
        layout.addWidget(self._section_title("CAPTURE AUTOMATIQUE"))
        layout.addLayout(auto_row)
        layout.addWidget(self.auto_status_label)
        layout.addWidget(self.last_translation_label)
        self.setLayout(layout)

        self._timer = QTimer(self)
        self._timer.setInterval(2000)
        self._timer.timeout.connect(self.refresh_game_status)
        self._timer.start()

        self.refresh_game_status()
        self._append_system_message(
            "Interface prête. Écrivez dans le chat pour tester la traduction."
        )

    @staticmethod
    def _section_title(text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("SectionTitle")
        return label

    def translate_chat_message(self) -> None:
        text = self.chat_input.text().strip()
        if not text:
            return

        self.chat_input.clear()
        self._append_chat_line("Vous", text, "#c9a24d")

        try:
            translated = self.container.pipeline.translator.translate(text)
        except Exception as exc:
            self._append_chat_line("Erreur", str(exc), "#c0392b")
            return

        self.container.pipeline.cache.set(text, translated)
        self.container.pipeline.history.add(text, translated)
        self._append_chat_line("Traduction", translated, "#7cb342")
        self.show_translation(text, translated)

    def start_worker(self) -> None:
        status = self.container.game_detection.scan()
        if not status.is_any_running:
            self._append_system_message(
                "Aucun jeu Diablo détecté. Lancez D3, D4 ou Immortal pour la capture auto."
            )
            return

        self.worker.start()
        self.auto_status_label.setText(
            f"Capture automatique : active ({status.summary()})"
        )
        self._append_system_message(
            f"Capture démarrée — {status.summary()}"
        )

    def stop_worker(self) -> None:
        self.worker.stop()
        self.auto_status_label.setText("Capture automatique : arrêtée")
        self._append_system_message("Capture automatique arrêtée.")

    def show_translation(self, source: str, translated: str) -> None:
        self.last_translation_label.setText(
            f"Dernière traduction : {source} → {translated}"
        )

    def show_live_translation(self, translated: str) -> None:
        self.last_translation_label.setText(f"Dernière capture OCR : {translated}")
        self._append_chat_line("Capture", translated, "#8ab4f8")

    def refresh_game_status(self) -> None:
        status = self.container.game_detection.scan()
        self.game_status.update_status(status)

        if self.worker.is_running and status.is_any_running:
            self.auto_status_label.setText(
                f"Capture automatique : active ({status.summary()})"
            )

    def _append_chat_line(self, speaker: str, message: str, color: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_log.append(
            f'<span style="color:#6b5f52;">[{timestamp}]</span> '
            f'<span style="color:{color}; font-weight:600;">[{speaker}]</span> '
            f'<span style="color:#e8dcc8;">{self._escape_html(message)}</span>'
        )

    def _append_system_message(self, message: str) -> None:
        self._append_chat_line("Système", message, "#8a8278")

    @staticmethod
    def _escape_html(value: str) -> str:
        return (
            value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
