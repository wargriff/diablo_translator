from __future__ import annotations

import os
from typing import Any

from src.infrastructure.paths import CACHE_OCR_DIR, MODELS_DIR, ensure_project_dirs
from src.ocr.chat_image_preprocessor import ChatImagePreprocessor
from src.ocr.easyocr_languages import split_easyocr_language_groups
from src.ocr.easyocr_patch import apply_easyocr_corrupt_msg_patch


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
        apply_easyocr_corrupt_msg_patch()
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

        latin_results = self._get_latin_reader().readtext(array)
        merged_results = list(latin_results)

        cyrillic_reader = self._get_cyrillic_reader()
        if cyrillic_reader is not None:
            cyrillic_results = cyrillic_reader.readtext(array)
            merged_results = self._merge_reader_results(merged_results, cyrillic_results)

        lines = self._group_results(merged_results, min_confidence=min_confidence)
        normalized_lines = [
            self._normalize_ocr_line(line) for line in lines if line.strip()
        ]
        return "\n".join(normalized_lines).strip()

    @classmethod
    def _normalize_ocr_line(cls, line: str) -> str:
        from src.chat.chat_text_normalizer import ChatTextNormalizer

        return ChatTextNormalizer.normalize_line(line)

    @staticmethod
    def _merge_reader_results(
        primary: list[tuple[Any, str, float]],
        secondary: list[tuple[Any, str, float]],
    ) -> list[tuple[Any, str, float]]:
        merged = list(primary)
        for bbox, text, confidence in secondary:
            cleaned = text.strip()
            if not cleaned:
                continue
            if OCRService._is_latin_misread_as_cyrillic(cleaned):
                continue
            if OCRService._overlaps_existing(bbox, merged):
                continue
            if OCRService._is_duplicate_text(cleaned, merged):
                continue
            merged.append((bbox, cleaned, confidence))
        return merged

    @staticmethod
    def _bbox_area(bbox: Any) -> float:
        xs = [point[0] for point in bbox]
        ys = [point[1] for point in bbox]
        return max(max(xs) - min(xs), 1.0) * max(max(ys) - min(ys), 1.0)

    @classmethod
    def _overlaps_existing(
        cls,
        bbox: Any,
        existing: list[tuple[Any, str, float]],
        *,
        threshold: float = 0.45,
    ) -> bool:
        area = cls._bbox_area(bbox)
        if area <= 0:
            return False

        xs = [point[0] for point in bbox]
        ys = [point[1] for point in bbox]
        left, right = min(xs), max(xs)
        top, bottom = min(ys), max(ys)

        for other_bbox, _text, _confidence in existing:
            other_xs = [point[0] for point in other_bbox]
            other_ys = [point[1] for point in other_bbox]
            overlap_left = max(left, min(other_xs))
            overlap_right = min(right, max(other_xs))
            overlap_top = max(top, min(other_ys))
            overlap_bottom = min(bottom, max(other_ys))
            if overlap_right <= overlap_left or overlap_bottom <= overlap_top:
                continue
            overlap_area = (overlap_right - overlap_left) * (overlap_bottom - overlap_top)
            if overlap_area / area >= threshold:
                return True
        return False

    @staticmethod
    def _normalize_text_token(value: str) -> str:
        import re

        return re.sub(r"[^\w\s]", "", value.casefold()).strip()

    @classmethod
    def _is_duplicate_text(
        cls,
        text: str,
        existing: list[tuple[Any, str, float]],
    ) -> bool:
        token = cls._normalize_text_token(text)
        if not token:
            return True
        for _bbox, other_text, _confidence in existing:
            other_token = cls._normalize_text_token(other_text)
            if not other_token:
                continue
            if token == other_token:
                return True
            if token in other_token or other_token in token:
                shorter = min(len(token), len(other_token))
                longer = max(len(token), len(other_token))
                if shorter / longer >= 0.85:
                    return True
        return False

    @staticmethod
    def _is_latin_misread_as_cyrillic(text: str) -> bool:
        latin = sum(1 for char in text if char.isascii() and char.isalpha())
        cyrillic = sum(1 for char in text if "\u0400" <= char <= "\u04FF")
        if latin == 0:
            return False
        return cyrillic > 0 and latin >= cyrillic

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
