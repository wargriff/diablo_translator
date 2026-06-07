from __future__ import annotations


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
        return GoogleTranslator(source=source, target=target_language).translate(text)
