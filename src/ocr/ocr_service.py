from __future__ import annotations

import os
from typing import Any

from src.infrastructure.paths import CACHE_OCR_DIR, MODELS_DIR, ensure_project_dirs
from src.ocr.chat_image_preprocessor import ChatImagePreprocessor
from src.ocr.easyocr_languages import split_easyocr_language_groups


class OCRService:

    def __init__(self, languages: tuple[str, ...] = ("en", "fr", "de")) -> None:
        ensure_project_dirs()
        self._languages = languages
        self._latin_langs, self._cyrillic_langs = split_easyocr_language_groups(languages)
        self._latin_reader: Any | None = None
        self._cyrillic_reader: Any | None = None
        os.environ.setdefault("EASYOCR_MODULE_PATH", str(MODELS_DIR))
        CACHE_OCR_DIR.mkdir(parents=True, exist_ok=True)

    def reload(self, languages: tuple[str, ...]) -> None:
        if languages == self._languages:
            return

        self._languages = languages
        self._latin_langs, self._cyrillic_langs = split_easyocr_language_groups(languages)
        self._latin_reader = None
        self._cyrillic_reader = None

    def _create_reader(self, lang_list: tuple[str, ...]) -> Any:
        import easyocr

        return easyocr.Reader(
            list(lang_list),
            gpu=False,
            model_storage_directory=str(MODELS_DIR),
        )

    def _get_latin_reader(self) -> Any:
        if self._latin_reader is None:
            self._latin_reader = self._create_reader(self._latin_langs)
        return self._latin_reader

    def _get_cyrillic_reader(self) -> Any | None:
        if not self._cyrillic_langs:
            return None
        if self._cyrillic_reader is None:
            self._cyrillic_reader = self._create_reader(self._cyrillic_langs)
        return self._cyrillic_reader

    def prewarm(self) -> None:
        self._get_latin_reader()
        reader = self._get_cyrillic_reader()
        if reader is not None:
            return

    def extract_text(self, image: Any) -> str:
        return self.extract_chat_text(image)

    def extract_chat_text(
        self,
        image: Any,
        *,
        min_confidence: float = 0.35,
        preprocess: bool = True,
    ) -> str:
        if image is None:
            return ""

        import numpy as np

        prepared = ChatImagePreprocessor.prepare(image, enabled=preprocess)
        array = np.asarray(prepared)

        results: list[tuple[Any, str, float]] = []
        results.extend(self._get_latin_reader().readtext(array))

        cyrillic_reader = self._get_cyrillic_reader()
        if cyrillic_reader is not None:
            results.extend(cyrillic_reader.readtext(array))

        lines = self._group_results(results, min_confidence=min_confidence)
        return "\n".join(lines).strip()

    @staticmethod
    def _group_results(
        results: list[tuple[Any, str, float]],
        *,
        min_confidence: float,
    ) -> list[str]:
        filtered = [
            (bbox, text.strip(), confidence)
            for bbox, text, confidence in results
            if text.strip() and confidence >= min_confidence
        ]
        if not filtered:
            return []

        filtered.sort(key=lambda item: (item[0][0][1], item[0][0][0]))

        lines: list[str] = []
        current_parts: list[str] = []
        last_y: float | None = None
        line_height = max(
            abs(filtered[0][0][2][1] - filtered[0][0][0][1]),
            12,
        )

        for bbox, text, _confidence in filtered:
            y = float(bbox[0][1])
            if last_y is not None and abs(y - last_y) > line_height * 0.65:
                if current_parts:
                    lines.append(" ".join(current_parts))
                current_parts = [text]
            else:
                current_parts.append(text)
            last_y = y

        if current_parts:
            lines.append(" ".join(current_parts))

        return lines
