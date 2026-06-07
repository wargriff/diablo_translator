from __future__ import annotations

import re


class LanguageDetectionService:

    _LANGUAGE_NAMES = {
        "fr": "Français",
        "en": "Anglais",
        "de": "Allemand",
        "es": "Espagnol",
        "it": "Italien",
        "pt": "Portugais",
        "ru": "Russe",
        "zh-cn": "Chinois",
        "ja": "Japonais",
        "ko": "Coréen",
    }

    _FRENCH_MARKERS = (
        " la ",
        " le ",
        " les ",
        " des ",
        " une ",
        " gars ",
        " monde ",
        " stp ",
        " mdr ",
        " bg ",
        " ouf ",
        " chez ",
    )
    _ENGLISH_MARKERS = (
        " the ",
        " yo ",
        " hello ",
        " hi ",
        " team ",
        " bro ",
        " gg ",
        " wp ",
        " ok ",
        " pls ",
        " thx ",
    )

    def detect(self, text: str) -> str | None:
        cleaned = text.strip()
        if len(cleaned) < 2:
            return None

        try:
            from langdetect import DetectorFactory, detect

            DetectorFactory.seed = 0
            return detect(cleaned)
        except Exception:
            return None

    def is_mixed_language(self, text: str) -> bool:
        cleaned = text.strip()
        if len(cleaned) < 4:
            return False

        try:
            from langdetect import DetectorFactory, detect_langs

            DetectorFactory.seed = 0
            probabilities = detect_langs(cleaned)
            if len(probabilities) >= 2 and probabilities[1].prob >= 0.12:
                return True
        except Exception:
            pass

        padded = f" {cleaned.lower()} "
        has_french = any(marker in padded for marker in self._FRENCH_MARKERS)
        has_english = any(marker in padded for marker in self._ENGLISH_MARKERS)
        if has_french and has_english:
            return True

        if re.search(r"\b(yo|hello|hi|gg|wp)\b", cleaned, re.I) and re.search(
            r"\b(la|les|gars|monde|team)\b",
            cleaned,
            re.I,
        ):
            return True

        return False

    def display_name(self, language_code: str | None) -> str:
        if not language_code:
            return "Inconnue"

        from src.translation.conversation_context import normalize_language

        normalized = normalize_language(language_code) or language_code
        return self._LANGUAGE_NAMES.get(normalized, normalized.upper())

    def is_same_language(self, detected: str | None, target: str) -> bool:
        if not detected:
            return False

        from src.translation.conversation_context import normalize_language

        normalized_target = normalize_language(target)
        normalized_detected = normalize_language(detected)

        if not normalized_target or not normalized_detected:
            return False

        return normalized_detected == normalized_target
