from __future__ import annotations

from typing import Protocol


class TranslatorProvider(Protocol):

    name: str

    def translate(
        self,
        text: str,
        *,
        source_language: str | None,
        target_language: str,
    ) -> str: ...
