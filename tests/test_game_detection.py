import unittest

from src.game_detection.game_detection_service import (
    SUPPORTED_GAMES,
    GameDetectionService,
)


class GameDetectionTests(unittest.TestCase):

    def test_supported_games_contains_d3_d4_immortal(self) -> None:
        keys = {game.key for game in SUPPORTED_GAMES}
        self.assertEqual(keys, {"d3", "d4", "immortal"})

    def test_scan_returns_status(self) -> None:
        status = GameDetectionService().scan()
        self.assertIsNotNone(status.summary())


if __name__ == "__main__":
    unittest.main()
