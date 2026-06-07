from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QLabel,
)

from src.infrastructure.container import Container


class HistoryWidget(QWidget):

    def __init__(self, container: Container) -> None:
        super().__init__()
        self.container = container

        title = QLabel("GRIMOIRE — HISTORIQUE DES TRADUCTIONS")
        title.setObjectName("SectionTitle")

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(
            ["Source", "Traduction", "Date"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)

        self.status_label = QLabel("")
        self.status_label.setObjectName("MutedText")

        self.refresh_button = QPushButton("Actualiser")
        self.export_json_button = QPushButton("Exporter JSON")
        self.export_csv_button = QPushButton("Exporter CSV")

        self.refresh_button.clicked.connect(self.refresh)
        self.export_json_button.clicked.connect(self.export_json)
        self.export_csv_button.clicked.connect(self.export_csv)

        actions = QHBoxLayout()
        actions.addWidget(self.refresh_button)
        actions.addWidget(self.export_json_button)
        actions.addWidget(self.export_csv_button)
        actions.addStretch()

        panel = QFrame()
        panel.setObjectName("Panel")
        panel_layout = QVBoxLayout()
        panel_layout.addWidget(self.table)
        panel_layout.addLayout(actions)
        panel_layout.addWidget(self.status_label)
        panel.setLayout(panel_layout)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(panel)
        self.setLayout(layout)

        self.refresh()

    def refresh(self) -> None:
        records = self.container.pipeline.history.list_recent(limit=100)
        self.table.setRowCount(len(records))

        for row_index, record in enumerate(records):
            self.table.setItem(row_index, 0, QTableWidgetItem(record.source_text))
            self.table.setItem(row_index, 1, QTableWidgetItem(record.translated_text))
            self.table.setItem(
                row_index,
                2,
                QTableWidgetItem(str(record.created_at)),
            )

        self.status_label.setText(f"{len(records)} entrées affichées")

    def export_json(self) -> None:
        path = self.container.export.export_json()
        self.status_label.setText(f"Export JSON créé : {path}")

    def export_csv(self) -> None:
        path = self.container.export.export_csv()
        self.status_label.setText(f"Export CSV créé : {path}")
