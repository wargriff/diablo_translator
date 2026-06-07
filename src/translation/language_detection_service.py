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
        " merci ",
        " salut ",
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
        " looking ",
        " group ",
        " party ",
        " join ",
        " need ",
        " help ",
    )

    _FRENCH_WORDS = re.compile(
        r"\b(je|tu|il|elle|nous|vous|les|des|une|pour|avec|pas|qui|est|dans|sur|"
        r"merci|bonjour|salut|oui|non|chez|fais|fait|veux|peux|peut|groupe|partie|"
        r"niveau|quoi|comment|bien|trop|aussi|mais|donc|chez|join|jai|j'ai)\b",
        re.I,
    )
    _ENGLISH_WORDS = re.compile(
        r"\b(the|and|for|you|your|need|looking|group|party|join|help|please|thanks|"
        r"hello|hi|yes|no|want|can|any|one|all|good|game|run|lvl|level|farm|trade|"
        r"wtb|wts|lfm|lfg|bro|team|ready|wait|go|stop|nice|well|done|anyone|someone)\b",
        re.I,
    )
    _GERMAN_WORDS = re.compile(
        r"\b(der|die|das|und|ich|wir|ihr|nicht|mit|für|auch|bin|suche|gruppe)\b",
        re.I,
    )
    _SPANISH_WORDS = re.compile(
        r"\b(el|la|los|las|que|por|para|con|grupo|busco|hola|si|no|puedo)\b",
        re.I,
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

    def detect_for_chat(self, text: str, home_language: str = "fr") -> str | None:
        cleaned = text.strip()
        if len(cleaned) < 2:
            return None

        if re.search(r"[àâäéèêëïîôùûüç]", cleaned, re.I):
            return "fr"

        heuristic = self._heuristic_language(cleaned)
        if heuristic:
            return heuristic

        detected = self.detect(cleaned)
        if detected:
            return detected

        if cleaned.isascii() and len(cleaned) >= 3:
            home = home_language.lower()
            if home != "en":
                return "en"

        return None

    def _heuristic_language(self, text: str) -> str | None:
        scores = {
            "fr": len(self._FRENCH_WORDS.findall(text)),
            "en": len(self._ENGLISH_WORDS.findall(text)),
            "de": len(self._GERMAN_WORDS.findall(text)),
            "es": len(self._SPANISH_WORDS.findall(text)),
        }
        best_lang, best_score = max(scores.items(), key=lambda item: item[1])
        if best_score == 0:
            return None

        sorted_scores = sorted(scores.values(), reverse=True)
        if len(sorted_scores) > 1 and sorted_scores[0] == sorted_scores[1]:
            padded = f" {text.lower()} "
            if any(marker in padded for marker self._FRENCH_MARKERS):
                return "fr"
            if any(marker in padded for marker in self._ENGLISH_MARKERS):
                return "en"

        return best_lang

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

        fr_score = len(self._FRENCH_WORDS.findall(cleaned))
        en_score = len(self._ENGLISH_WORDS.findall(cleaned))
        return fr_score >= 1 and en_score >= 1

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
