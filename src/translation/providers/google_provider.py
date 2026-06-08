from __future__ import annotations

from src.translation.providers.retry import translate_with_retry


class GoogleTranslatorProvider:

    name = "google"

    def translate(
        self,
        text: str,
        *,
        source_language: str | None,
        target_language: str,
    ) -> str:
        from deep_translator import GoogleTranslator

        source = source_language or "auto"

        def _call() -> str:
            return GoogleTranslator(source=source, target=target_language).translate(text)

        return translate_with_retry(_call)
