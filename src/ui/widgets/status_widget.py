from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.infrastructure.container import Container


class StatusWidget(QWidget):

    def __init__(self, container: Container) -> None:
        super().__init__()
        self.container = container
        self.worker = container.worker

        self.game_label = QLabel()
        self.stats_label = QLabel()
        self.translation_label = QLabel("En attente de traduction...")
        self.start_button = QPushButton("Démarrer la traduction auto")
        self.stop_button = QPushButton("Arrêter")
        self.refresh_button = QPushButton("Actualiser")

        self.start_button.clicked.connect(self.start_worker)
        self.stop_button.clicked.connect(self.stop_worker)
        self.refresh_button.clicked.connect(self.refresh)

        buttons = QHBoxLayout()
        buttons.addWidget(self.start_button)
        buttons.addWidget(self.stop_button)
        buttons.addWidget(self.refresh_button)

        layout = QVBoxLayout()
        layout.addWidget(self.game_label)
        layout.addWidget(self.stats_label)
        layout.addWidget(self.translation_label)
        layout.addLayout(buttons)
        self.setLayout(layout)

        self.refresh()

    def start_worker(self) -> None:
        self.worker.start()
        self.translation_label.setText("Traduction automatique active...")

    def stop_worker(self) -> None:
        self.worker.stop()
        self.translation_label.setText("Traduction automatique arrêtée.")

    def show_translation(self, text: str) -> None:
        self.translation_label.setText(text)

    def refresh(self) -> None:
        running = self.container.game_detection.is_running()
        self.game_label.setText(
            "Jeu : Diablo III détecté" if running else "Jeu : Diablo III non détecté"
        )

        summary = self.container.analytics.get_summary()
        self.stats_label.setText(
            "Statistiques : "
            f"{summary.total_translations} traductions | "
            f"{summary.translations_today} aujourd'hui | "
            f"{summary.unique_sources} textes uniques"
        )
