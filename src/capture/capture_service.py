from __future__ import annotations

from typing import Any


class CaptureService:

    def capture_region(self, region: dict[str, int] | None = None) -> Any:
        import mss
        from PIL import Image

        with mss.mss() as screen:
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
        import mss

        with mss.mss() as screen:
            monitor = screen.monitors[monitor_index]
            return self.capture_region(monitor)
