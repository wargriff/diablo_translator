from __future__ import annotations

from typing import Protocol


class GameDetectionPort(Protocol):

    def scan(self): ...

    def is_running(self) -> bool: ...
