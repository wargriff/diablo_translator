from __future__ import annotations

from src.domain.models.translation_result import TranslationResult
from src.infrastructure.config_manager import AppConfig, ConfigManager
from src.translation.conversation_context import ConversationContext, normalize_language
from src.translation.language_detection_service import LanguageDetectionService
from src.translation.providers.registry import TranslatorRegistry


class TranslationService:

    def __init__(
        self,
        config: AppConfig | None = None,
        conversation: ConversationContext | None = None,
    ) -> None:
        self._config = config or ConfigManager.load()
        self._conversation = conversation or ConversationContext()
        self._language_detector = LanguageDetectionService()
        self.reload(config)

    @property
    def conversation(self) -> ConversationContext:
        return self._conversation

    def reload(self, config: AppConfig | None = None) -> None:
        if config is not None:
            self._config = config
        self._provider = TranslatorRegistry.create(self._config)

    @property
    def provider_name(self) -> str:
        return self._provider.name

    def translate(
        self,
        source_text: str,
        *,
        origin: str = "chat",
        source_language: str | None = None,
        target_language: str | None = None,
    ) -> TranslationResult:
        cleaned = source_text.strip()
        home = normalize_language(self._config.language) or "fr"
        explicit_target = normalize_language(target_language) if target_language else None
        explicit_source = normalize_language(source_language) if source_language else None

        if not cleaned:
            return TranslationResult(
                source_text="",
                translated_text="",
                source_language=None,
                target_language=explicit_target or home,
                provider=self._provider.name,
            )

        if len(cleaned) < self._config.min_text_length:
            return TranslationResult(
                source_text=cleaned,
                translated_text=cleaned,
                source_language=explicit_source,
                target_language=explicit_target or home,
                provider=self._provider.name,
                skipped=True,
            )

        if (
            explicit_target is None
            and self._config.preserve_mixed_language
            and origin in {"user", "voice"}
            and self._language_detector.is_mixed_language(cleaned)
        ):
            return TranslationResult(
                source_text=cleaned,
                translated_text=cleaned,
                source_language=self.detect_language(cleaned, origin=origin),
                target_language=home,
                provider=self._provider.name,
                skipped=True,
                preserved_mixed=True,
            )

        detected_source = explicit_source
        if detected_source is None and self._config.auto_detect_language:
            detected_source = self.detect_language(cleaned, origin=origin)

        if origin == "chat" and not detected_source and cleaned.isascii():
            detected_source = self._config.default_reply_language

        resolved_target = explicit_target or self._resolve_target(detected_source, origin, home)

        if self._language_detector.is_same_language(detected_source, resolved_target):
            return TranslationResult(
                source_text=cleaned,
                translated_text=cleaned,
                source_language=detected_source,
                target_language=resolved_target,
                provider=self._provider.name,
                skipped=True,
            )

        if (
            explicit_target is None
            and not self._config.bidirectional_mode
            and self._config.auto_detect_language
            and self._language_detector.is_same_language(detected_source, home)
        ):
            return TranslationResult(
                source_text=cleaned,
                translated_text=cleaned,
                source_language=detected_source,
                target_language=home,
                provider=self._provider.name,
                skipped=True,
            )

        translated = self._provider.translate(
            cleaned,
            source_language=detected_source,
            target_language=resolved_target,
        )

        if origin == "chat" and not self.is_home_language(detected_source):
            self._conversation.remember_foreign(detected_source, home)

        return TranslationResult(
            source_text=cleaned,
            translated_text=translated,
            source_language=detected_source,
            target_language=resolved_target,
            provider=self._provider.name,
            outgoing=origin in {"user", "voice"},
            incoming=origin == "chat",
        )

    def _resolve_target(
        self,
        source_language: str | None,
        origin: str,
        home: str,
    ) -> str:
        if not self._config.bidirectional_mode:
            return home

        if origin in {"user", "voice"}:
            peer = normalize_language(
                self._conversation.last_foreign_language
                or self._config.default_reply_language
            ) or "en"
            if self._language_detector.is_same_language(source_language, home):
                return peer
            if self._language_detector.is_same_language(source_language, peer):
                return home
            return peer

        if self._language_detector.is_same_language(source_language, home):
            return home

        return home

    def detect_language(self, text: str, *, origin: str = "chat") -> str | None:
        home = normalize_language(self._config.language) or "fr"
        if origin == "chat":
            return self._language_detector.detect_for_chat(text, home)
        return self._language_detector.detect(text)

    def language_display_name(self, code: str | None) -> str:
        return self._language_detector.display_name(code)

    def is_home_language(self, language_code: str | None) -> bool:
        return self._language_detector.is_same_language(
            language_code,
            self._config.language,
        )

    def is_reply_language(self, language_code: str | None) -> bool:
        return self._language_detector.is_same_language(
            language_code,
            self.reply_language(),
        )

    def reply_language(self) -> str:
        peer = (
            self._conversation.last_foreign_language
            or self._config.default_reply_language
        )
        return normalize_language(peer) or "en"

    def reply_language_label(self) -> str:
        return self.language_display_name(self.reply_language())
