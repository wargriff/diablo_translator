from __future__ import annotations

from src.infrastructure.config_manager import ConfigManager


class TranslationService:

    def __init__(self) -> None:
        config = ConfigManager.load()
        self._target_language = config.language

    def translate(self, source_text: str) -> str:
        if not source_text.strip():
            return ""

        from deep_translator import GoogleTranslator

        return GoogleTranslator(
            source="auto",
            target=self._target_language,
        ).translate(source_text)
