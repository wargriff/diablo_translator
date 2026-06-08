from __future__ import annotations

from typing import Any

from src.cache import TranslationCache
from src.domain.models.translation_result import TranslationResult
from src.infrastructure.config_manager import AppConfig, ConfigManager
from src.ocr import OCRService
from src.services.history_service import HistoryService
from src.translation.conversation_context import ConversationContext
from src.translation.translation_service import TranslationService


class TranslationPipeline:

    def __init__(
        self,
        config: AppConfig | None = None,
        conversation: ConversationContext | None = None,
    ) -> None:
        self._config = config or ConfigManager.load()
        self.conversation = conversation or ConversationContext()
        self._ocr_languages = self._parse_ocr_languages(self._config.ocr_languages)
        self._ocr: OCRService | None = None
        self.translator = TranslationService(self._config, self.conversation)
        self.cache = TranslationCache(max_entries=self._config.cache_max_entries)
        self.history = HistoryService()

    @property
    def ocr(self) -> OCRService:
        if self._ocr is None:
            self._ocr = OCRService(self._ocr_languages)
        return self._ocr

    def reload(self, config: AppConfig) -> None:
        self._config = config
        languages = self._parse_ocr_languages(config.ocr_languages)
        self._ocr_languages = languages
        if self._ocr is not None:
            self._ocr.reload(languages)
        self.translator.reload(config)
        self.cache = TranslationCache(max_entries=config.cache_max_entries)

    def process_text(
        self,
        source_text: str,
        *,
        origin: str = "chat",
        source_language: str | None = None,
        target_language: str | None = None,
    ) -> TranslationResult:
        provider = self.translator.provider_name
        preview_target = target_language or self._preview_target(source_text, origin)

        cached = self.cache.get(source_text, preview_target, provider)
        if cached:
            detected = self.translator.detect_language(source_text, origin=origin)
            if origin == "chat" and detected and not self.translator.is_home_language(detected):
                self.conversation.remember_foreign(
                    detected,
                    self._config.language,
                )
            return TranslationResult(
                source_text=source_text,
                translated_text=cached,
                source_language=detected,
                target_language=preview_target,
                provider=provider,
                outgoing=origin in {"user", "voice"},
                incoming=origin == "chat",
            )

        result = self.translator.translate(
            source_text,
            origin=origin,
            source_language=source_language,
            target_language=target_language,
        )
        if result.translated_text and not result.skipped:
            self.cache.set(
                source_text,
                result.translated_text,
                target_language=result.target_language,
                provider=provider,
                source_language=result.source_language,
            )

        if result.translated_text and not result.skipped:
            self.history.add(
                result.source_text,
                result.translated_text,
                result.source_language,
                result.target_language,
            )

        return result

    def process_image(self, image: Any, *, origin: str = "chat") -> TranslationResult:
        source_text = self.ocr.extract_text(image)
        if not source_text:
            return TranslationResult(
                source_text="",
                translated_text="",
                source_language=None,
                target_language=self._config.language,
                provider=self.translator.provider_name,
            )

        return self.process_text(source_text, origin=origin)

    def _preview_target(self, source_text: str, origin: str) -> str:
        home = self._config.language
        if not self._config.bidirectional_mode:
            return home

        if origin in {"user", "voice"}:
            detected = self.translator.detect_language(source_text, origin=origin)
            peer = self.translator.reply_language()
            if self.translator.is_home_language(detected):
                return peer
            if self.translator.is_reply_language(detected):
                return home
            return peer

        return home

    @staticmethod
    def _parse_ocr_languages(raw: str) -> tuple[str, ...]:
        languages = tuple(
            language.strip()
            for language in raw.split(",")
            if language.strip()
        )
        return languages or ("en", "fr", "de")
