from __future__ import annotations

import time

from src.capture.game_window_service import GameWindowService
from src.game_detection.game_detection_service import GameDetectionService


class GameReadinessService:

    MIN_CLIENT_WIDTH = 1024
    MIN_CLIENT_HEIGHT = 600

    def __init__(self) -> None:
        self._stable_since: float | None = None
        self._last_hint = ""

    @property
    def last_hint(self) -> str:
        return self._last_hint

    def reset(self) -> None:
        self._stable_since = None
        self._last_hint = ""

    def is_ready(
        self,
        game_detection: GameDetectionService,
        *,
        grace_seconds: int,
    ) -> bool:
        hint = self.evaluate(game_detection, grace_seconds=grace_seconds)
        self._last_hint = hint
        return not hint

    def evaluate(
        self,
        game_detection: GameDetectionService,
        *,
        grace_seconds: int,
    ) -> str:
        if not game_detection.is_running():
            self._stable_since = None
            return "Jeu Diablo non détecté"

        window = GameWindowService.find_primary_game_info(game_detection)
        if window is None:
            self._stable_since = None
            return "Fenêtre Diablo introuvable — lancement en cours…"

        if (
            window.client.width < self.MIN_CLIENT_WIDTH
            or window.client.height < self.MIN_CLIENT_HEIGHT
        ):
            self._stable_since = None
            return "Diablo en chargement — OCR en pause…"

        if self._stable_since is None:
            self._stable_since = time.time()
            return "Stabilisation fenêtre Diablo…"

        remaining = grace_seconds - (time.time() - self._stable_since)
        if remaining > 0:
            return f"Attente menu Diablo ({max(1, int(remaining))} s)…"

        return ""
