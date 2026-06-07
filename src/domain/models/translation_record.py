from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class TranslationRecord:

    id: int
    source_text: str
    translated_text: str
    source_language: str | None
    target_language: str | None
    created_at: datetime
