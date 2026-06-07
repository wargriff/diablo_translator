from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class CaptureRegion:

    left: int
    top: int
    width: int
    height: int


class ScreenCapturePort(Protocol):

    def capture_region(self, region: CaptureRegion | dict[str, int] | None = None) -> Any: ...
