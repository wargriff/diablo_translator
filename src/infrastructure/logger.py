
import logging

from pathlib import Path

from logging.handlers import (
    RotatingFileHandler
)


class LoggerManager:

    @staticmethod
    def setup():

        Path("logs").mkdir(
            exist_ok=True
        )

        root = logging.getLogger()

        if root.handlers:
            return

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

        file_handler = (
            RotatingFileHandler(
                "logs/app.log",
                maxBytes=5_000_000,
                backupCount=5,
                encoding="utf-8"
            )
        )

        file_handler.setFormatter(
            formatter
        )

        root.setLevel(
            logging.INFO
        )

        root.addHandler(
            file_handler
        )

    @staticmethod
    def get_logger(
        name: str
    ):
        return logging.getLogger(
            name
        )
