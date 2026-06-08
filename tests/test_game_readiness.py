import unittest
from unittest.mock import MagicMock, patch

from src.application.game_readiness_service import GameReadinessService


class GameReadinessServiceTests(unittest.TestCase):

    def setUp(self) -> None:
        self.service = GameReadinessService()
        self.game_detection = MagicMock()

    def test_not_ready_when_process_missing(self) -> None:
        self.game_detection.is_running.return_value = False
        hint = self.service.evaluate(self.game_detection, grace_seconds=5)
        self.assertEqual(hint, "Jeu Diablo non détecté")

    @patch("src.application.game_readiness_service.GameWindowService.find_primary_game_info")
    def test_not_ready_when_window_too_small(self, find_window) -> None:
        self.game_detection.is_running.return_value = True
        window = MagicMock()
        window.client.width = 800
        window.client.height = 600
        find_window.return_value = window

        hint = self.service.evaluate(self.game_detection, grace_seconds=5)
        self.assertIn("chargement", hint.casefold())

    @patch("src.application.game_readiness_service.time.time")
    @patch("src.application.game_readiness_service.GameWindowService.find_primary_game_info")
    def test_ready_after_grace_period(self, find_window, mock_time) -> None:
        self.game_detection.is_running.return_value = True
        window = MagicMock()
        window.client.width = 1920
        window.client.height = 1080
        find_window.return_value = window

        mock_time.return_value = 100.0
        self.assertFalse(
            self.service.is_ready(self.game_detection, grace_seconds=10)
        )

        mock_time.return_value = 111.0
        self.assertTrue(
            self.service.is_ready(self.game_detection, grace_seconds=10)
        )


if __name__ == "__main__":
    unittest.main()
