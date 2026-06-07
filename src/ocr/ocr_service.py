from __future__ import annotations

import os
from typing import Any

from src.infrastructure.paths import CACHE_OCR_DIR, MODELS_DIR, ensure_project_dirs


class OCRService:

    def __init__(self, languages: tuple[str, ...] = ("en", "fr", "de")) -> None:
        ensure_project_dirs()
        self._languages = languages
        self._reader: Any | None = None
        os.environ.setdefault("EASYOCR_MODULE_PATH", str(MODELS_DIR))
        CACHE_OCR_DIR.mkdir(parents=True, exist_ok=True)

    def reload(self, languages: tuple[str, ...]) -> None:
        if languages != self._languages:
            self._languages = languages
            self._reader = None

    def _get_reader(self) -> Any:
        if self._reader is None:
            import easyocr

            self._reader = easyocr.Reader(
                list(self._languages),
                gpu=False,
                model_storage_directory=str(MODELS_DIR),
            )

        return self._reader

    def extract_text(self, image: Any) -> str:
        if image is None:
            return ""

        import numpy as np

        reader = self._get_reader()
        results = reader.readtext(np.asarray(image))
        return " ".join(text for _, text, _ in results).strip()
