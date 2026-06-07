from __future__ import annotations

from typing import Any


class OCRService:

    def __init__(self) -> None:
        self._reader: Any | None = None

    def _get_reader(self) -> Any:
        if self._reader is None:
            import easyocr

            self._reader = easyocr.Reader(["en"], gpu=False)

        return self._reader

    def extract_text(self, image: Any) -> str:
        if image is None:
            return ""

        import numpy as np

        reader = self._get_reader()
        results = reader.readtext(np.asarray(image))
        return " ".join(text for _, text, _ in results).strip()
