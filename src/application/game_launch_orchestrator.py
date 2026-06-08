from __future__ import annotations

from dataclasses import dataclass

from src.application.config_service import ConfigService
from src.application.game_readiness_service import GameReadinessService
from src.application.game_session_service import GameSessionService
from src.domain.models.game_session import GameLaunchPhase, GameSessionSnapshot


@dataclass(frozen=True, slots=True)
class GameLaunchState:

    phase: GameLaunchPhase
    hint: str
    snapshot: GameSessionSnapshot


class GameLaunchOrchestrator:

    def __init__(
        self,
        game_session: GameSessionService,
        game_readiness: GameReadinessService,
        config_service: ConfigService,
    ) -> None:
        self._session = game_session
        self._readiness = game_readiness
        self._config_service = config_service

    def tick(self, *, force: bool = False) -> GameLaunchState:
        snapshot = self._session.snapshot(force=force)
        config = self._config_service.config
        hint = self._readiness.evaluate_snapshot(
            snapshot,
            grace_seconds=config.game_startup_grace_seconds,
        )
        phase = self._resolve_phase(snapshot, hint)
        return GameLaunchState(phase=phase, hint=hint, snapshot=snapshot)

    @staticmethod
    def _resolve_phase(snapshot: GameSessionSnapshot, hint: str) -> GameLaunchPhase:
        if not snapshot.status.is_any_running:
            return GameLaunchPhase.IDLE

        if snapshot.window is None:
            return GameLaunchPhase.PROCESS

        if hint and "chargement" in hint.casefold():
            return GameLaunchPhase.WINDOW

        if hint:
            return GameLaunchPhase.STABILIZING

        return GameLaunchPhase.READY
