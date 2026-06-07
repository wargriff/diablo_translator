from __future__ import annotations

from src.domain.models.translation_result import TranslationResult
from src.infrastructure.config_manager import AppConfig, ConfigManager
from src.translation.language_detection_service import LanguageDetectionService
from src.translation.providers.registry import TranslatorRegistry


class TranslationService:

    def __init__(self, config: AppConfig | None = None) -> None:
        self._config = config or ConfigManager.load()
        self._language_detector = LanguageDetectionService()
        self.reload(config)

    def reload(self, config: AppConfig | None = None) -> None:
        if config is not None:
            self._config = config
        self._provider = TranslatorRegistry.create(self._config)

    @property
    def provider_name(self) -> str:
        return self._provider.name

    def translate(self, source_text: str) -> TranslationResult:
        cleaned = source_text.strip()
        if not cleaned:
            return TranslationResult(
                source_text="",
                translated_text="",
                source_language=None,
                target_language=self._config.language,
                provider=self._provider.name,
            )

        source_language = None
        if self._config.auto_detect_language:
            source_language = self._language_detector.detect(cleaned)

        if self._config.auto_detect_language and self._language_detector.is_same_language(
            source_language,
            self._config.language,
        ):
            return TranslationResult(
                source_text=cleaned,
                translated_text=cleaned,
                source_language=source_language,
                target_language=self._config.language,
                provider=self._provider.name,
                skipped=True,
            )

        translated = self._provider.translate(
            cleaned,
            source_language=source_language,
            target_language=self._config.language,
        )

        return TranslationResult(
            source_text=cleaned,
            translated_text=translated,
            source_language=source_language,
            target_language=self._config.language,
            provider=self._provider.name,
        )

    def detect_language(self, text: str) -> str | None:
        return self._language_detector.detect(text)

    def language_display_name(self, code: str | None) -> str:
        return self._language_detector.display_name(code)
