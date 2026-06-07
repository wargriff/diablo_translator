from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from src.infrastructure.database import Database


@dataclass(slots=True)
class AnalyticsSummary:

    total_translations: int
    translations_today: int
    unique_sources: int


class AnalyticsService:

    def get_summary(self) -> AnalyticsSummary:
        with sqlite3.connect(Database.DB_PATH) as conn:
            total = conn.execute(
                "SELECT COUNT(*) FROM translations"
            ).fetchone()[0]

            today = conn.execute(
                """
                SELECT COUNT(*) FROM translations
                WHERE date(created_at) = date('now', 'localtime')
                """
            ).fetchone()[0]

            unique = conn.execute(
                "SELECT COUNT(DISTINCT source_text) FROM translations"
            ).fetchone()[0]

        return AnalyticsSummary(
            total_translations=total,
            translations_today=today,
            unique_sources=unique,
        )
