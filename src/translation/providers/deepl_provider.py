from __future__ import annotations

import os

from src.infrastructure.paths import PROJECT_ROOT


class DeepLTranslatorProvider:

    name = "deepl"

    def __init__(self, api_key: str | None = None) -> None:
        self._load_env()
        self._api_key = api_key or os.getenv("DEEPL_API_KEY", "").strip()

    @staticmethod
    def _load_env() -> None:
        try:
            from dotenv import load_dotenv

            load_dotenv(PROJECT_ROOT / ".env")
        except ModuleNotFoundError:
            return

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key)

    def translate(
        self,
        text: str,
        *,
        source_language: str | None,
        target_language: str,
    ) -> str:
        if not self.is_configured:
            raise RuntimeError(
                "Clé DeepL manquante. Ajoutez DEEPL_API_KEY dans .env ou les paramètres."
            )

        from deep_translator import DeeplTranslator

        source = source_language or "auto"
        target = self._map_target_language(target_language)
        return DeeplTranslator(
            api_key=self._api_key,
            source=source,
            target=target,
        ).translate(text)

    @staticmethod
    def _map_target_language(language: str) -> str:
        mapping = {
            "fr": "FR",
            "en": "EN-US",
            "de": "DE",
            "es": "ES",
            "it": "IT",
            "pt": "PT-PT",
            "ru": "RU",
            "ja": "JA",
            "zh-cn": "ZH",
        }
        return mapping.get(language.lower(), language.upper())
