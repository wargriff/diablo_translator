from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TranslationResult:

    source_text: str
    translated_text: str
    source_language: str | None
    target_language: str
    provider: str
    skipped: bool = False
    preserved_mixed: bool = False
    outgoing: bool = False

    @property
    def display_text(self) -> str:
        if self.skipped:
            return self.source_text
        return self.translated_text
