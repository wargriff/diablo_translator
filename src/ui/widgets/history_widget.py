from PyQt6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.infrastructure.container import Container


class HistoryWidget(QWidget):

    def __init__(self, container: Container) -> None:
        super().__init__()
        self.container = container

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(
            ["Source", "Traduction", "Date"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)

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

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(actions)
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

    def export_json(self) -> None:
        path = self.container.export.export_json()
        self.refresh_button.setText(f"Export JSON : {path.name}")

    def export_csv(self) -> None:
        path = self.container.export.export_csv()
        self.refresh_button.setText(f"Export CSV : {path.name}")
