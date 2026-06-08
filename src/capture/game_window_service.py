from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import dataclass

from src.capture.display_service import DisplayService, ScreenRect
from src.game_detection.game_detection_service import GameDetectionService, GameDetectionStatus

GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x00000080
MIN_CLIENT_AREA = 50_000
PREFERRED_CLIENT_AREA = 200_000


@dataclass(frozen=True, slots=True)
class GameWindowInfo:

    hwnd: int
    client: ScreenRect
    window: ScreenRect
    process_name: str
    window_title: str
    monitor_index: int
    is_fullscreen: bool
    display_mode: str


class GameWindowService:

    @classmethod
    def find_primary_game_info(
        cls,
        game_detection_service: GameDetectionService,
        *,
        status: GameDetectionStatus | None = None,
    ) -> GameWindowInfo | None:
        status = status or game_detection_service.scan()
        game = status.primary_game
        if game is None:
            return None

        process_name = status.active_processes.get(game.key)
        if not process_name:
            return None

        return cls._find_window_info(process_name)

    @classmethod
    def find_primary_game_rect(
        cls,
        game_detection_service: GameDetectionService,
    ) -> ScreenRect | None:
        info = cls.find_primary_game_info(game_detection_service)
        if info is None:
            return None
        return info.client

    @classmethod
    def _find_window_info(cls, process_name: str) -> GameWindowInfo | None:
        import psutil

        target_pids: set[int] = set()
        for process in psutil.process_iter(["pid", "name"]):
            name = process.info.get("name")
            if name and name.casefold() == process_name.casefold():
                target_pids.add(process.info["pid"])

        if not target_pids:
            return None

        matches = cls._collect_window_matches(target_pids)
        if not matches:
            return None

        preferred = [item for item in matches if item[0] >= PREFERRED_CLIENT_AREA]
        pool = preferred or matches
        pool.sort(key=lambda item: item[0], reverse=True)
        _, title, hwnd, client_rect, window_rect = pool[0]
        monitor = DisplayService.monitor_for_rect(window_rect)
        is_fullscreen, display_mode = DisplayService.detect_display_mode(
            window_rect,
            monitor,
        )

        return GameWindowInfo(
            hwnd=hwnd,
            client=client_rect,
            window=window_rect,
            process_name=process_name,
            window_title=title,
            monitor_index=monitor.index,
            is_fullscreen=is_fullscreen,
            display_mode=display_mode,
        )

    @classmethod
    def _collect_window_matches(
        cls,
        target_pids: set[int],
    ) -> list[tuple[int, str, int, ScreenRect, ScreenRect]]:
        user32 = ctypes.windll.user32
        matches: list[tuple[int, str, int, ScreenRect, ScreenRect]] = []

        def enum_callback(hwnd, _):
            if not user32.IsWindowVisible(hwnd):
                return True

            if user32.IsIconic(hwnd):
                return True

            ex_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            if ex_style & WS_EX_TOOLWINDOW:
                return True

            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if pid.value not in target_pids:
                return True

            length = user32.GetWindowTextLengthW(hwnd)
            title = ""
            if length > 0:
                buffer = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buffer, length + 1)
                title = buffer.value.strip()

            client = wintypes.RECT()
            user32.GetClientRect(hwnd, ctypes.byref(client))
            area = client.right * client.bottom
            if area < MIN_CLIENT_AREA:
                return True

            origin = wintypes.POINT(0, 0)
            user32.ClientToScreen(hwnd, ctypes.byref(origin))
            client_rect = ScreenRect(
                left=origin.x,
                top=origin.y,
                width=client.right,
                height=client.bottom,
            )

            outer = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(outer))
            window_rect = ScreenRect(
                left=outer.left,
                top=outer.top,
                width=outer.right - outer.left,
                height=outer.bottom - outer.top,
            )

            matches.append((area, title, int(hwnd), client_rect, window_rect))
            return True

        enum_proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        user32.EnumWindows(enum_proc(enum_callback), 0)
        return matches
