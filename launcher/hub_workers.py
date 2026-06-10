from __future__ import annotations

from PyQt6.QtCore import QThread, pyqtSignal

from launcher.api_probe import probe_diablo_api, probe_web_home
from launcher.service_ports import resolve_api_port, resolve_web_port


class HubStatusWorker(QThread):
    finished = pyqtSignal(bool, bool)

    def run(self) -> None:
        api_port = resolve_api_port()
        web_port = resolve_web_port()
        api_ok = probe_diablo_api(api_port)
        web_ok = probe_web_home(web_port)
        self.finished.emit(api_ok, web_ok)


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
