from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path

from src.infrastructure.paths import EXPORTS_DIR
from src.services.history_service import HistoryService


class ExportService:

    def __init__(self) -> None:
        self._history = HistoryService()

    def export_json(self, destination: Path | None = None) -> Path:
        EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        path = destination or EXPORTS_DIR / f"history_{self._timestamp()}.json"
        records = self._history.to_dicts(limit=10_000)

        path.write_text(
            json.dumps(records, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )
        return path

    def export_csv(self, destination: Path | None = None) -> Path:
        EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        path = destination or EXPORTS_DIR / f"history_{self._timestamp()}.csv"
        records = self._history.list_recent(limit=10_000)

        with path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "id",
                    "source_text",
                    "translated_text",
                    "source_language",
                    "target_language",
                    "created_at",
                ]
            )
            for record in records:
                writer.writerow(
                    [
                        record.id,
                        record.source_text,
                        record.translated_text,
                        record.source_language or "",
                        record.target_language or "",
                        record.created_at,
                    ]
                )

        return path

    @staticmethod
    def _timestamp() -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
