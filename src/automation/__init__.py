__all__ = ["TranslationWorker"]


def __getattr__(name: str):
    if name == "TranslationWorker":
        from src.automation.translation_worker import TranslationWorker

        return TranslationWorker
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
