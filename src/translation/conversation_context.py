from __future__ import annotations

import threading


class ConversationContext:

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._last_foreign_language: str | None = None

    @property
    def last_foreign_language(self) -> str | None:
        with self._lock:
            return self._last_foreign_language

    def remember_foreign(self, language: str | None, home_language: str) -> None:
        normalized = normalize_language(language)
        if not normalized or normalize_language(home_language) == normalized:
            return

        with self._lock:
            self._last_foreign_language = normalized

    def reset(self) -> None:
        with self._lock:
            self._last_foreign_language = None


def normalize_language(code: str | None) -> str | None:
    if not code:
        return None

    lowered = code.lower().strip()
    if lowered.startswith("en"):
        return "en"
    if lowered.startswith("fr"):
        return "fr"
    if lowered.startswith("de"):
        return "de"
    if lowered.startswith("es"):
        return "es"
    if lowered.startswith("it"):
        return "it"
    if lowered.startswith("pt"):
        return "pt"
    if lowered.startswith("ru"):
        return "ru"

    return lowered.split("-")[0]
