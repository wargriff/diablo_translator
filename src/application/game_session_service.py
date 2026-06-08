from __future__ import annotations

import time

from src.application.config_service import ConfigService
from src.capture.game_window_service import GameWindowService
from src.domain.models.game_session import GameSessionSnapshot
from src.game_detection.game_detection_service import GameDetectionService


class GameSessionService:

    TTL_SECONDS = 0.75

    def __init__(
        self,
        game_detection: GameDetectionService,
        config_service: ConfigService,
    ) -> None:
        self._game_detection = game_detection
        self._config_service = config_service
        self._cached: GameSessionSnapshot | None = None

    def snapshot(self, *, force: bool = False) -> GameSessionSnapshot:
        now = time.time()
        if (
            not force
            and self._cached is not None
            and now - self._cached.scanned_at < self.TTL_SECONDS
        ):
            return self._cached

        status = self._game_detection.scan(force=force)
        window = None
        if status.is_any_running:
            window = GameWindowService.find_primary_game_info(
                self._game_detection,
                status=status,
            )

        self._cached = GameSessionSnapshot(
            status=status,
            window=window,
            scanned_at=now,
        )
        return self._cached

    def invalidate(self) -> None:
        self._cached = None
        self._game_detection.invalidate_cache()

    def scan(self):
        return self.snapshot().status

    def is_running(self) -> bool:
        return self.snapshot().status.is_any_running

    def prepare_overlay_if_game_running(self) -> bool:
        if not self.is_running():
            return False

        self._config_service.apply_overlay_preset()
        return True

    def summary(self) -> str:
        return self.snapshot().status.summary()
