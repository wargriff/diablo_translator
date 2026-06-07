from __future__ import annotations


class TranslationCache:

    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    def get(self, source_text: str) -> str | None:
        return self._store.get(source_text)

    def set(self, source_text: str, translated: str) -> None:
        self._store[source_text] = translated

    def clear(self) -> None:
        self._store.clear()
