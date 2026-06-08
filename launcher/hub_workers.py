from __future__ import annotations

import urllib.error
import urllib.request

from PyQt6.QtCore import QThread, pyqtSignal


class HubStatusWorker(QThread):
    finished = pyqtSignal(bool, bool)

    def run(self) -> None:
        api_ok = self._probe("http://127.0.0.1:8000/api/v1/health")
        web_ok = self._probe("http://127.0.0.1:3000")
        self.finished.emit(api_ok, web_ok)

    @staticmethod
    def _probe(url: str) -> bool:
        try:
            with urllib.request.urlopen(url, timeout=0.6) as response:
                return response.status == 200
        except (urllib.error.URLError, TimeoutError, OSError):
            return False


class HubTranslateWorker(QThread):
    finished = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(
        self,
        text: str,
        source_language: str,
        target_language: str,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._text = text
        self._source_language = source_language
        self._target_language = target_language

    def run(self) -> None:
        try:
            from launcher.hub_services import get_hub_pipeline

            result = get_hub_pipeline().process_text(
                self._text,
                origin="user",
                source_language=self._source_language,
                target_language=self._target_language,
            )
            self.finished.emit(result.translated_text)
        except Exception as exc:
            self.failed.emit(str(exc))
