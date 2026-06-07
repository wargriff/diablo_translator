from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from src.game_detection import SUPPORTED_GAMES, GameDetectionStatus
from src.infrastructure.container import Container


class GameStatusPanel(QWidget):

    def __init__(self, container: Container) -> None:
        super().__init__()
        self.container = container
        self._cards: dict[str, tuple[QFrame, QLabel, QLabel]] = {}

        self.summary_label = QLabel("Analyse des jeux Diablo...")
        self.summary_label.setObjectName("MutedText")

        grid = QGridLayout()
        grid.setSpacing(10)

        for index, game in enumerate(SUPPORTED_GAMES):
            card, title_label, status_label = self._create_card(game.title)
            self._cards[game.key] = (card, title_label, status_label)
            grid.addWidget(card, index // 2, index % 2)

        layout = QVBoxLayout()
        layout.addWidget(self._section_title("ÉTAT DES JEUX"))
        layout.addWidget(self.summary_label)
        layout.addLayout(grid)
        self.setLayout(layout)

    @staticmethod
    def _section_title(text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("SectionTitle")
        return label

    @staticmethod
    def _create_card(title: str) -> tuple[QFrame, QLabel, QLabel]:
        card = QFrame()
        card.setObjectName("GameCard")
        card.setProperty("running", False)

        title_label = QLabel(title)
        title_label.setObjectName("SectionTitle")

        status_label = QLabel("Hors ligne")
        status_label.setObjectName("StatusOffline")

        card_layout = QVBoxLayout()
        card_layout.addWidget(title_label)
        card_layout.addWidget(status_label)
        card.setLayout(card_layout)

        return card, title_label, status_label

    def update_status(self, status: GameDetectionStatus) -> None:
        self.summary_label.setText(status.summary())

        running_keys = {game.key for game in status.running_games}
        for game in SUPPORTED_GAMES:
            card, _, status_label = self._cards[game.key]
            is_running = game.key in running_keys

            card.setProperty("running", is_running)
            card.style().unpolish(card)
            card.style().polish(card)

            if is_running:
                process = status.active_processes.get(game.key, game.process_names[0])
                status_label.setText(f"En ligne ({process})")
                status_label.setObjectName("StatusOnline")
            else:
                status_label.setText("Hors ligne")
                status_label.setObjectName("StatusOffline")

            status_label.style().unpolish(status_label)
            status_label.style().polish(status_label)
