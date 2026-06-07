from __future__ import annotations

from src.application.player_identity_service import PlayerIdentityService
from src.chat.chat_message_parser import ChatMessage
from src.infrastructure.config_manager import AppConfig
from src.translation.translation_pipeline import TranslationPipeline


class InGameChatRouter:

    def __init__(
        self,
        pipeline: TranslationPipeline,
        player_identity: PlayerIdentityService,
    ) -> None:
        self._pipeline = pipeline
        self._player_identity = player_identity

    def process_message(self, message: ChatMessage, config: AppConfig):
        if message.outgoing:
            return self._pipeline.process_text(message.message, origin="user")

        detected = self._pipeline.translator.detect_language(
            message.message,
            origin="chat",
        )
        self._player_identity.remember_from_message(
            message,
            config=config,
            home_language=config.language,
            detected_language=detected,
        )

        if self._player_identity.is_local_player(message, config):
            return self._pipeline.process_text(message.message, origin="user")

        return self._pipeline.process_text(message.message, origin="chat")
