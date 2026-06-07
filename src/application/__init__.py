from src.application.config_service import ConfigService
from src.application.game_session_service import GameSessionService
from src.application.overlay_preset import apply_game_overlay_preset

__all__ = [
    "ConfigService",
    "GameSessionService",
    "apply_game_overlay_preset",
]


def __getattr__(name: str):
    if name == "LiveChatService":
        from src.application.live_chat_service import LiveChatService

        return LiveChatService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
