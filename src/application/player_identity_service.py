from __future__ import annotations

from src.chat.chat_message_parser import ChatMessage
from src.infrastructure.config_manager import AppConfig
from src.translation.conversation_context import normalize_language


class PlayerIdentityService:

    def __init__(self) -> None:
        self._learned_name: str | None = None

    @property
    def learned_name(self) -> str | None:
        return self._learned_name

    def reset(self) -> None:
        self._learned_name = None

    def resolve_player_name(self, config: AppConfig) -> str | None:
        configured = (config.player_name or "").strip()
        if configured:
            return configured
        if config.auto_detect_player and self._learned_name:
            return self._learned_name
        return None

    def remember_from_message(
        self,
        message: ChatMessage,
        *,
        config: AppConfig,
        home_language: str,
        detected_language: str | None,
    ) -> None:
        if not config.auto_detect_player or not message.speaker:
            return
        if (config.player_name or "").strip():
            return

        home = normalize_language(home_language) or "fr"
        detected = normalize_language(detected_language) if detected_language else None
        if detected != home:
            return

        self._learned_name = message.speaker.strip()

    def is_local_player(self, message: ChatMessage, config: AppConfig) -> bool:
        player = self.resolve_player_name(config)
        if not player or not message.speaker:
            return False

        local = player.casefold()
        speaker = message.speaker.casefold()
        return local == speaker or local in speaker or speaker in local
