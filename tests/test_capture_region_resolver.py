from __future__ import annotations

import unittest
from dataclasses import dataclass

from src.capture.capture_region_resolver import CaptureRegionResolver
from src.capture.display_service import MonitorInfo, ScreenRect
from src.infrastructure.config_manager import AppConfig


@dataclass
class FakeGame:
    key: str = "d3"


@dataclass
class FakeStatus:
    primary_game: FakeGame | None = None
    is_any_running: bool = True

    def __post_init__(self):
        if self.primary_game is None:
            self.primary_game = FakeGame()


class FakeGameDetection:

    def scan(self):
        return FakeStatus()


@dataclass
class FakeWindow:
    client: ScreenRect
    monitor: MonitorInfo
    window: ScreenRect | None = None
    is_fullscreen: bool = False
    display_mode: str = "windowed"

    def __post_init__(self):
        if self.window is None:
            self.window = self.client

    @property
    def monitor_index(self) -> int:
        return self.monitor.index


class CaptureRegionResolverTests(unittest.TestCase):

    def test_fullscreen_uses_game_monitor(self):
        config = AppConfig(
            capture_from_game_window=True,
            capture_fullscreen_monitor=True,
            display_mode="auto",
        )
        window = ScreenRect(left=0, top=0, width=1920, height=1080)
        monitor = MonitorInfo(index=1, left=0, top=0, width=1920, height=1080)

        base, source = CaptureRegionResolver._select_base_rect(
            FakeWindow(window, monitor, is_fullscreen=True, display_mode="fullscreen"),
            config,
        )

        self.assertEqual(source, "game_monitor_fullscreen")
        self.assertEqual(base.width, 1920)

    def test_windowed_uses_client_area(self):
        config = AppConfig(display_mode="auto")
        client = ScreenRect(left=100, top=80, width=1600, height=900)
        window = ScreenRect(left=90, top=40, width=1620, height=980)
        monitor = MonitorInfo(index=1, left=0, top=0, width=1920, height=1080)

        base, source = CaptureRegionResolver._select_base_rect(
            FakeWindow(client, monitor, window=window, display_mode="windowed"),
            config,
        )

        self.assertEqual(source, "game_client")
        self.assertEqual(base, client)

    def test_resolve_fallback_monitor(self):
        config = AppConfig(chat_region_preset="d3", capture_from_game_window=False)
        resolved = CaptureRegionResolver.resolve(FakeGameDetection(), config)
        self.assertEqual(resolved.source, "monitor_primary")
        self.assertGreaterEqual(resolved.width, 120)


if __name__ == "__main__":
    unittest.main()
