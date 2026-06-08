import unittest
from unittest.mock import MagicMock, patch

from src.application.game_launch_orchestrator import GameLaunchOrchestrator
from src.application.game_readiness_service import GameReadinessService
from src.domain.models.game_session import GameLaunchPhase, GameSessionSnapshot
from src.game_detection.game_detection_service import GameDetectionStatus, SupportedGame


class GameLaunchOrchestratorTests(unittest.TestCase):

    def setUp(self) -> None:
        self.session = MagicMock()
        self.readiness = GameReadinessService()
        self.config_service = MagicMock()
        self.config_service.config.game_startup_grace_seconds = 5
        self.orchestrator = GameLaunchOrchestrator(
            self.session,
            self.readiness,
            self.config_service,
        )
        self.game = SupportedGame(
            key="d3",
            title="Diablo III",
            short_title="D3",
            process_names=("Diablo III64.exe",),
        )

    def test_idle_when_no_process(self) -> None:
        snapshot = GameSessionSnapshot(
            status=GameDetectionStatus([], {}),
            window=None,
            scanned_at=0.0,
        )
        self.session.snapshot.return_value = snapshot

        state = self.orchestrator.tick()

        self.assertEqual(state.phase, GameLaunchPhase.IDLE)

    @patch("src.application.game_readiness_service.time.time")
    def test_ready_after_grace(self, mock_time) -> None:
        window = MagicMock()
        window.client.width = 1920
        window.client.height = 1080
        snapshot = GameSessionSnapshot(
            status=GameDetectionStatus([self.game], {"d3": "Diablo III64.exe"}),
            window=window,
            scanned_at=0.0,
        )
        self.session.snapshot.return_value = snapshot

        mock_time.return_value = 100.0
        state = self.orchestrator.tick()
        self.assertEqual(state.phase, GameLaunchPhase.STABILIZING)

        mock_time.return_value = 106.0
        state = self.orchestrator.tick()
        self.assertEqual(state.phase, GameLaunchPhase.READY)
        self.assertEqual(state.hint, "")


if __name__ == "__main__":
    unittest.main()
