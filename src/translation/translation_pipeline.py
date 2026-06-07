from __future__ import annotations

from typing import Any

from src.cache import TranslationCache
from src.domain.models.translation_result import TranslationResult
from src.infrastructure.config_manager import AppConfig, ConfigManager
from src.ocr import OCRService
from src.services.history_service import HistoryService
from src.translation.translation_service import TranslationService


class TranslationPipeline:

    def __init__(self, config: AppConfig | None = None) -> None:
        self._config = config or ConfigManager.load()
        self.ocr = OCRService(self._parse_ocr_languages(self._config.ocr_languages))
        self.translator = TranslationService(self._config)
        self.cache = TranslationCache()
        self.history = HistoryService()

    def reload(self, config: AppConfig) -> None:
        self._config = config
        self.ocr.reload(self._parse_ocr_languages(config.ocr_languages))
        self.translator.reload(config)

    def process_text(self, source_text: str) -> TranslationResult:
        provider = self.translator.provider_name
        target = self._config.language

        cached = self.cache.get(source_text, target, provider)
        if cached:
            return TranslationResult(
                source_text=source_text,
                translated_text=cached,
                source_language=self.translator.detect_language(source_text),
                target_language=target,
                provider=provider,
            )

        result = self.translator.translate(source_text)
        if result.translated_text and not result.skipped:
            self.cache.set(
                source_text,
                result.translated_text,
                target_language=target,
                provider=provider,
                source_language=result.source_language,
            )

        if result.translated_text:
            self.history.add(
                result.source_text,
                result.translated_text,
                result.source_language,
                result.target_language,
            )

        return result

    def process_image(self, image: Any) -> TranslationResult:
        source_text = self.ocr.extract_text(image)
        if not source_text:
            return TranslationResult(
                source_text="",
                translated_text="",
                source_language=None,
                target_language=self._config.language,
                provider=self.translator.provider_name,
            )

        return self.process_text(source_text)

    @staticmethod
    def _parse_ocr_languages(raw: str) -> tuple[str, ...]:
        languages = tuple(
            language.strip()
            for language in raw.split(",")
            if language.strip()
        )
        return languages or ("en", "fr", "de")
