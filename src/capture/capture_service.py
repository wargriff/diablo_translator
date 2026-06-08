from __future__ import annotations

from typing import Any


class CaptureService:

    def __init__(self) -> None:
        self._screen: Any | None = None

    def capture_region(self, region: dict[str, int] | None = None) -> Any:
        from PIL import Image

        screen = self._get_screen()
        monitor = region or screen.monitors[1]
        shot = screen.grab(monitor)
        return Image.frombytes(
            "RGB",
            shot.size,
            shot.bgra,
            "raw",
            "BGRX",
        )

    def capture_monitor(self, monitor_index: int = 1) -> Any:
        screen = self._get_screen()
        monitor = screen.monitors[monitor_index]
        return self.capture_region(monitor)

    def close(self) -> None:
        if self._screen is not None:
            self._screen.close()
            self._screen = None

    def _get_screen(self):
        if self._screen is None:
            import mss

            self._screen = mss.mss()
        return self._screen
