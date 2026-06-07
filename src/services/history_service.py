from __future__ import annotations

import sqlite3
from dataclasses import asdict
from datetime import datetime

from src.domain.models import TranslationRecord
from src.infrastructure.database import Database


class HistoryService:

    def add(
        self,
        source_text: str,
        translated: str,
        source_language: str | None = None,
        target_language: str | None = None,
    ) -> None:
        with sqlite3.connect(Database.DB_PATH) as conn:
            conn.execute(
                """
                INSERT INTO translations
                    (source_text, translated_text, source_language, target_language)
                VALUES (?, ?, ?, ?)
                """,
                (source_text, translated, source_language, target_language),
            )
            conn.commit()

    def list_recent(self, limit: int = 50) -> list[TranslationRecord]:
        with sqlite3.connect(Database.DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT id, source_text, translated_text,
                       source_language, target_language, created_at
                FROM translations
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [
            TranslationRecord(
                id=row["id"],
                source_text=row["source_text"],
                translated_text=row["translated_text"],
                source_language=row["source_language"],
                target_language=row["target_language"],
                created_at=datetime.fromisoformat(row["created_at"]),
            )
            for row in rows
        ]

    def count(self) -> int:
        with sqlite3.connect(Database.DB_PATH) as conn:
            return conn.execute("SELECT COUNT(*) FROM translations").fetchone()[0]

    def to_dicts(self, limit: int = 50) -> list[dict]:
        return [asdict(record) for record in self.list_recent(limit=limit)]
