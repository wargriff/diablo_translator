from __future__ import annotations

__all__ = ["TranslationPipeline", "TranslationService"]


def __getattr__(name: str):
    if name == "TranslationPipeline":
        from src.translation.translation_pipeline import TranslationPipeline

        return TranslationPipeline
    if name == "TranslationService":
        from src.translation.translation_service import TranslationService

        return TranslationService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
