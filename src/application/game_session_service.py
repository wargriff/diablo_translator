from __future__ import annotations

from src.application.config_service import ConfigService
from src.game_detection.game_detection_service import GameDetectionService


class GameSessionService:

    def __init__(
        self,
        game_detection: GameDetectionService,
        config_service: ConfigService,
    ) -> None:
        self._game_detection = game_detection
        self._config_service = config_service

    def scan(self):
        return self._game_detection.scan()

    def is_running(self) -> bool:
        return self._game_detection.is_running()

    def prepare_overlay_if_game_running(self) -> bool:
        if not self.is_running():
            return False

        self._config_service.apply_overlay_preset()
        return True

    def summary(self) -> str:
        return self.scan().summary()
