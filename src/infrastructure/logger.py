import logging
from logging.handlers import RotatingFileHandler

from src.infrastructure.paths import LOGS_DIR


class LoggerManager:

    @staticmethod
    def setup() -> None:
        LOGS_DIR.mkdir(exist_ok=True)

        root = logging.getLogger()
        if root.handlers:
            return

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

        file_handler = RotatingFileHandler(
            LOGS_DIR / "app.log",
            maxBytes=5_000_000,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)

        root.setLevel(logging.INFO)
        root.addHandler(file_handler)

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        return logging.getLogger(name)
