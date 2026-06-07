from __future__ import annotations

from src.domain.interfaces.translator_provider import TranslatorProvider
from src.infrastructure.config_manager import AppConfig
from src.translation.providers.deepl_provider import DeepLTranslatorProvider
from src.translation.providers.google_provider import GoogleTranslatorProvider


class TranslatorRegistry:

    _PROVIDERS: dict[str, type] = {
        "google": GoogleTranslatorProvider,
        "deepl": DeepLTranslatorProvider,
    }

    @classmethod
    def available(cls) -> list[str]:
        return list(cls._PROVIDERS.keys())

    @classmethod
    def create(cls, config: AppConfig) -> TranslatorProvider:
        provider_name = config.translator.lower()
        provider_cls = cls._PROVIDERS.get(provider_name, GoogleTranslatorProvider)

        if provider_cls is DeepLTranslatorProvider:
            provider = DeepLTranslatorProvider(api_key=config.deepl_api_key or None)
            if not provider.is_configured:
                return GoogleTranslatorProvider()
            return provider

        return provider_cls()
