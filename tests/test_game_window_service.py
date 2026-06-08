import unittest
from unittest.mock import MagicMock, patch

from src.capture.game_window_service import (
    MIN_CLIENT_AREA,
    PREFERRED_CLIENT_AREA,
    GameWindowService,
)


class GameWindowServiceTests(unittest.TestCase):

    @patch("src.capture.game_window_service.GameWindowService._collect_window_matches")
    @patch("psutil.process_iter")
    def test_prefers_larger_client_area(self, process_iter, collect_matches) -> None:
        process_iter.return_value = [
            MagicMock(info={"pid": 42, "name": "Diablo III64.exe"}),
        ]

        small = (MIN_CLIENT_AREA + 10_000, "Loading", 1, MagicMock(), MagicMock())
        large = (PREFERRED_CLIENT_AREA + 50_000, "Diablo III", 2, MagicMock(), MagicMock())
        collect_matches.return_value = [small, large]

        with patch("src.capture.game_window_service.DisplayService.monitor_for_rect") as monitor_for:
            monitor_for.return_value = MagicMock(index=1)
            with patch("src.capture.game_window_service.DisplayService.detect_display_mode") as detect_mode:
                detect_mode.return_value = (True, "fullscreen")
                info = GameWindowService._find_window_info("Diablo III64.exe")

        self.assertIsNotNone(info)
        self.assertEqual(info.hwnd, 2)
        self.assertEqual(info.window_title, "Diablo III")

    @patch("src.capture.game_window_service.GameWindowService._collect_window_matches")
    @patch("psutil.process_iter")
    def test_accepts_loading_window_when_no_large_window(self, process_iter, collect_matches) -> None:
        process_iter.return_value = [
            MagicMock(info={"pid": 7, "name": "Diablo IV.exe"}),
        ]
        loading = (MIN_CLIENT_AREA + 1_000, "", 9, MagicMock(), MagicMock())
        collect_matches.return_value = [loading]

        with patch("src.capture.game_window_service.DisplayService.monitor_for_rect") as monitor_for:
            monitor_for.return_value = MagicMock(index=1)
            with patch("src.capture.game_window_service.DisplayService.detect_display_mode") as detect_mode:
                detect_mode.return_value = (False, "windowed")
                info = GameWindowService._find_window_info("Diablo IV.exe")

        self.assertIsNotNone(info)
        self.assertEqual(info.hwnd, 9)

    @patch("src.capture.game_window_service.GameWindowService._collect_window_matches")
    @patch("psutil.process_iter")
    def test_returns_none_when_process_missing(self, process_iter, collect_matches) -> None:
        process_iter.return_value = []
        info = GameWindowService._find_window_info("Diablo III64.exe")
        self.assertIsNone(info)
        collect_matches.assert_not_called()


if __name__ == "__main__":
    unittest.main()
