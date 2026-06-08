import unittest
from unittest.mock import MagicMock, patch

from src.application.game_session_service import GameSessionService


class GameSessionServiceTests(unittest.TestCase):

    def setUp(self) -> None:
        self.game_detection = MagicMock()
        self.config_service = MagicMock()
        self.service = GameSessionService(self.game_detection, self.config_service)

    @patch("src.application.game_session_service.GameWindowService.find_primary_game_info")
    @patch("src.application.game_session_service.time.time")
    def test_snapshot_is_cached(self, mock_time, find_window) -> None:
        status = MagicMock()
        status.is_any_running = True
        self.game_detection.scan.return_value = status
        find_window.return_value = MagicMock()
        mock_time.side_effect = [10.0, 10.2, 10.2]

        first = self.service.snapshot()
        second = self.service.snapshot()

        self.assertIs(first, second)
        self.game_detection.scan.assert_called_once()

    @patch("src.application.game_session_service.time.time")
    def test_invalidate_forces_rescan(self, mock_time) -> None:
        status = MagicMock()
        status.is_any_running = False
        self.game_detection.scan.return_value = status
        mock_time.side_effect = [10.0, 10.2, 10.2]

        self.service.snapshot()
        self.service.invalidate()
        self.service.snapshot(force=True)

        self.assertEqual(self.game_detection.scan.call_count, 2)


if __name__ == "__main__":
    unittest.main()
