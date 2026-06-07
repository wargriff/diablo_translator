from __future__ import annotations


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

    def display_name(self, language_code: str | None) -> str:
        if not language_code:
            return "Inconnue"
        return self._LANGUAGE_NAMES.get(language_code, language_code.upper())

    def is_same_language(self, detected: str | None, target: str) -> bool:
        if not detected:
            return False

        normalized_target = target.lower()
        normalized_detected = detected.lower()

        if normalized_detected == normalized_target:
            return True

        if normalized_target == "fr" and normalized_detected in {"fr", "fr-ca"}:
            return True

        if normalized_target.startswith("en") and normalized_detected.startswith("en"):
            return True

        return False
