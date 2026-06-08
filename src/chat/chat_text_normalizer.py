from __future__ import annotations

import re


class ChatTextNormalizer:

    _DIT_MESSAGE = re.compile(
        r"(?:dit|says|sagt|dice|schreibt|writes|chuchote|whispers?)\s*:?\s*",
        re.IGNORECASE,
    )
    _CYRILLIC = re.compile(r"[\u0400-\u04FF]")
    _LATIN = re.compile(r"[A-Za-zÀ-ÿ]")
    _KNOWN_WORD = re.compile(
        r"\b(dit|says|wargriff|monde|guide|mes|mon|les|the|team|chat|whisper|chuchote|"
        r"retourne|ville|coups|subjugateur|champion|bul-kathos)\b",
        re.IGNORECASE,
    )

    @classmethod
    def normalize_line(cls, line: str) -> str:
        cleaned = " ".join(line.split()).strip()
        if not cleaned:
            return cleaned
        return cls.dedupe_repeated_content(cleaned)

    @classmethod
    def extract_chat_message(cls, line: str) -> str:
        normalized = cls.normalize_line(line)
        matches = list(cls._DIT_MESSAGE.finditer(normalized))
        if matches:
            message = normalized[matches[-1].end() :].strip()
            return cls.dedupe_repeated_content(message)
        return normalized

    @classmethod
    def dedupe_repeated_content(cls, text: str) -> str:
        cleaned = " ".join(text.split()).strip()
        if len(cleaned) < 4:
            return cleaned

        words = cleaned.split()
        if len(words) >= 2 and len(words) % 2 == 0:
            mid = len(words) // 2
            first = " ".join(words[:mid])
            second = " ".join(words[mid:])
            if cls._similar(first, second):
                return first

        if len(cleaned) >= 8:
            mid = len(cleaned) // 2
            first = cleaned[:mid].strip()
            second = cleaned[mid:].strip()
            if cls._similar(first, second):
                return first

        return cleaned

    @classmethod
    def is_likely_garbage(cls, text: str) -> bool:
        cleaned = text.strip()
        if len(cleaned) < 4:
            return False

        letters = [char for char in cleaned if char.isalpha()]
        if not letters:
            return True

        latin_count = len(cls._LATIN.findall(cleaned))
        cyrillic_count = len(cls._CYRILLIC.findall(cleaned))
        if latin_count >= 3 and cyrillic_count >= 3 and len(cleaned) < 48:
            return True

        lowered = cleaned.lower()
        if re.fullmatch(r"[\W\d_]+", cleaned):
            return True

        vowels = sum(
            1
            for char in lowered
            if char in "aeiouyàâäéèêëïîôùûüöäü"
        )
        if len(letters) >= 6 and vowels / len(letters) < 0.22:
            return True

        if len(cleaned) <= 14 and not re.search(r"[.!?:;]", cleaned):
            if latin_count and cyrillic_count:
                return True

        if len(cleaned) <= 24 and not cls._KNOWN_WORD.search(cleaned):
            words = re.findall(r"[a-zàâäéèêëïîôùûü]+", lowered)
            long_words = [word for word in words if len(word) >= 5]
            if long_words and len(words) <= 3:
                return True

        return False

    @classmethod
    def _similar(cls, left: str, right: str) -> bool:
        left_norm = cls._normalize_for_compare(left)
        right_norm = cls._normalize_for_compare(right)
        if not left_norm or not right_norm:
            return False
        if left_norm == right_norm:
            return True
        if left_norm in right_norm or right_norm in left_norm:
            shorter = min(len(left_norm), len(right_norm))
            longer = max(len(left_norm), len(right_norm))
            return shorter / longer >= 0.85
        return False

    @staticmethod
    def _normalize_for_compare(value: str) -> str:
        lowered = value.casefold()
        return re.sub(r"[^\w\s]", "", lowered).strip()
