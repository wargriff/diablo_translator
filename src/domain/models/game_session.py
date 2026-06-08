from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.capture.game_window_service import GameWindowInfo
from src.game_detection.game_detection_service import GameDetectionStatus


@dataclass(frozen=True, slots=True)
class GameSessionSnapshot:

    status: GameDetectionStatus
    window: GameWindowInfo | None
    scanned_at: float


class GameLaunchPhase(str, Enum):

    IDLE = "idle"
    PROCESS = "process"
    WINDOW = "window"
    STABILIZING = "stabilizing"
    READY = "ready"
