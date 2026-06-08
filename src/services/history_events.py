from __future__ import annotations

from collections.abc import Callable

from src.domain.models import TranslationRecord

_listeners: list[Callable[[TranslationRecord], None]] = []


def on_translation_added(callback: Callable[[TranslationRecord], None]) -> None:
    _listeners.append(callback)


def emit_translation_added(record: TranslationRecord) -> None:
    for callback in list(_listeners):
        try:
            callback(record)
        except Exception:
            pass
