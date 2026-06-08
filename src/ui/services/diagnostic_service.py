from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from PyQt6.QtCore import QObject, pyqtSignal


@dataclass(frozen=True, slots=True)
class DiagnosticEvent:

    level: str
    source: str
    message: str
    detail: str = ""


class DiagnosticService(QObject):

    event_added = pyqtSignal(object)
    status_changed = pyqtSignal(str)

    _instance: DiagnosticService | None = None

    def __init__(self) -> None:
        super().__init__()
        self._events: deque[DiagnosticEvent] = deque(maxlen=200)
        self._status = "Prêt"
        self._micro = "OFF"
        self._ocr = "OFF"
        self._game = "OFF"

    @classmethod
    def instance(cls) -> DiagnosticService:
        if cls._instance is None:
            cls._instance = DiagnosticService()
        return cls._instance

    @property
    def status_line(self) -> str:
        return (
            f"{self._status} · Micro {self._micro} · OCR {self._ocr} · Jeu {self._game}"
        )

    def set_status(self, status: str) -> None:
        self._status = status
        self.status_changed.emit(self.status_line)

    def set_micro(self, state: str) -> None:
        self._micro = state
        self.status_changed.emit(self.status_line)

    def set_ocr(self, state: str) -> None:
        self._ocr = state
        self.status_changed.emit(self.status_line)

    def set_game(self, state: str) -> None:
        self._game = state
        self.status_changed.emit(self.status_line)

    def record(
        self,
        source: str,
        message: str,
        *,
        level: str = "info",
        detail: str = "",
    ) -> None:
        event = DiagnosticEvent(
            level=level,
            source=source,
            message=message,
            detail=detail,
        )
        self._events.appendleft(event)
        self.event_added.emit(event)
        if level in {"error", "critical"}:
            self.set_status(message[:80])

    def events(self) -> list[DiagnosticEvent]:
        return list(self._events)
