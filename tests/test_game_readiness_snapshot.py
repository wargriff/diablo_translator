import unittest
from unittest.mock import MagicMock, patch

from src.application.game_readiness_service import GameReadinessService
from src.domain.models.game_session import GameSessionSnapshot
from src.game_detection.game_detection_service import GameDetectionStatus, SupportedGame


class GameReadinessSnapshotTests(unittest.TestCase):

    def setUp(self) -> None:
        self.service = GameReadinessService()
        self.game = SupportedGame(
            key="d3",
            title="Diablo III",
            short_title="D3",
            process_names=("Diablo III64.exe",),
        )

    def test_not_ready_when_process_missing(self) -> None:
        snapshot = GameSessionSnapshot(
            status=GameDetectionStatus([], {}),
            window=None,
            scanned_at=0.0,
        )
        hint = self.service.evaluate_snapshot(snapshot, grace_seconds=5)
        self.assertEqual(hint, "Jeu Diablo non détecté")

    def test_not_ready_when_window_too_small(self) -> None:
        window = MagicMock()
        window.client.width = 800
        window.client.height = 600
        snapshot = GameSessionSnapshot(
            status=GameDetectionStatus([self.game], {"d3": "Diablo III64.exe"}),
            window=window,
            scanned_at=0.0,
        )

        hint = self.service.evaluate_snapshot(snapshot, grace_seconds=5)
        self.assertIn("chargement", hint.casefold())

    @patch("src.application.game_readiness_service.time.time")
    def test_ready_after_grace_period(self, mock_time) -> None:
        window = MagicMock()
        window.client.width = 1920
        window.client.height = 1080
        snapshot = GameSessionSnapshot(
            status=GameDetectionStatus([self.game], {"d3": "Diablo III64.exe"}),
            window=window,
            scanned_at=0.0,
        )

        mock_time.return_value = 100.0
        self.assertFalse(
            self.service.is_ready_snapshot(snapshot, grace_seconds=10)
        )

        mock_time.return_value = 111.0
        self.assertTrue(
            self.service.is_ready_snapshot(snapshot, grace_seconds=10)
        )


if __name__ == "__main__":
    unittest.main()
