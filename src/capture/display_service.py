from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MonitorInfo:

    index: int
    left: int
    top: int
    width: int
    height: int

    @property
    def area(self) -> int:
        return self.width * self.height


@dataclass(frozen=True, slots=True)
class ScreenRect:

    left: int
    top: int
    width: int
    height: int

    @property
    def area(self) -> int:
        return max(self.width, 0) * max(self.height, 0)

    @property
    def center_x(self) -> int:
        return self.left + self.width // 2

    @property
    def center_y(self) -> int:
        return self.top + self.height // 2


class DisplayService:

    @classmethod
    def list_monitors(cls) -> tuple[MonitorInfo, ...]:
        import mss

        monitors: list[MonitorInfo] = []
        with mss.mss() as screen:
            for index, monitor in enumerate(screen.monitors[1:], start=1):
                monitors.append(
                    MonitorInfo(
                        index=index,
                        left=monitor["left"],
                        top=monitor["top"],
                        width=monitor["width"],
                        height=monitor["height"],
                    )
                )
        return tuple(monitors)

    @classmethod
    def primary_monitor(cls) -> MonitorInfo:
        monitors = cls.list_monitors()
        return monitors[0] if monitors else MonitorInfo(1, 0, 0, 1920, 1080)

    @classmethod
    def monitor_at(cls, x: int, y: int) -> MonitorInfo:
        monitors = cls.list_monitors()
        if not monitors:
            return cls.primary_monitor()

        user32 = ctypes.windll.user32
        monitor_handle = user32.MonitorFromPoint(
            wintypes.POINT(x, y),
            2,  # MONITOR_DEFAULTTONEAREST
        )
        if monitor_handle:
            class MONITORINFO(ctypes.Structure):
                _fields_ = [
                    ("cbSize", wintypes.DWORD),
                    ("rcMonitor", wintypes.RECT),
                    ("rcWork", wintypes.RECT),
                    ("dwFlags", wintypes.DWORD),
                ]

            info = MONITORINFO()
            info.cbSize = ctypes.sizeof(MONITORINFO)
            if user32.GetMonitorInfoW(monitor_handle, ctypes.byref(info)):
                rect = info.rcMonitor
                for monitor in monitors:
                    if (
                        monitor.left == rect.left
                        and monitor.top == rect.top
                        and monitor.width == rect.right - rect.left
                    ):
                        return monitor

        best = monitors[0]
        best_distance = float("inf")
        for monitor in monitors:
            cx = monitor.left + monitor.width // 2
            cy = monitor.top + monitor.height // 2
            distance = (cx - x) ** 2 + (cy - y) ** 2
            if distance < best_distance:
                best_distance = distance
                best = monitor
        return best

    @classmethod
    def monitor_for_rect(cls, rect: ScreenRect) -> MonitorInfo:
        return cls.monitor_at(rect.center_x, rect.center_y)

    @classmethod
    def detect_display_mode(
        cls,
        window_rect: ScreenRect,
        monitor: MonitorInfo,
    ) -> tuple[bool, str]:
        if window_rect.width <= 0 or window_rect.height <= 0:
            return False, "windowed"

        coverage = window_rect.area / monitor.area if monitor.area else 0.0
        aligned_left = abs(window_rect.left - monitor.left) <= 8
        aligned_top = abs(window_rect.top - monitor.top) <= 8
        near_full_width = window_rect.width >= monitor.width - 16
        near_full_height = window_rect.height >= monitor.height - 16

        if coverage >= 0.90 or (aligned_left and aligned_top and near_full_width and near_full_height):
            if near_full_width and near_full_height:
                return True, "fullscreen"
            return True, "borderless"

        return False, "windowed"
