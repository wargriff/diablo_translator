from __future__ import annotations

from typing import Any, Protocol


class OCRPort(Protocol):

    def extract_chat_text(
        self,
        image: Any,
        *,
        min_confidence: float = 0.30,
        preprocess: bool = True,
    ) -> str: ...
