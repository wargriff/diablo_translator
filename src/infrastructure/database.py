
from pathlib import Path
import sqlite3


class Database:

    DB_PATH = Path(
        "user_data/history.db"
    )

    @classmethod
    def initialize(cls):

        cls.DB_PATH.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with sqlite3.connect(
            cls.DB_PATH
        ) as conn:

            conn.execute(
                '''
                CREATE TABLE IF NOT EXISTS translations
                (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    source_text TEXT NOT NULL,

                    translated_text TEXT NOT NULL,

                    source_language TEXT,

                    target_language TEXT,

                    created_at DATETIME
                    DEFAULT CURRENT_TIMESTAMP
                )
                '''
            )

            conn.commit()
