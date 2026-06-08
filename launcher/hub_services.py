from __future__ import annotations

from src.translation.translation_pipeline import TranslationPipeline

_pipeline: TranslationPipeline | None = None


def get_hub_pipeline() -> TranslationPipeline:
    global _pipeline
    if _pipeline is None:
        from src.infrastructure.database import Database

        Database.initialize()
        _pipeline = TranslationPipeline()
    return _pipeline
