from __future__ import annotations

import re


class ChatLineExtractor:

    _NOISE_PATTERN = re.compile(
        r"^(system|party|clan|whisper|trade|global)\s*:?",
        re.IGNORECASE,
    )
    _LOOT_PATTERN = re.compile(
        r"\b(a forgé|a obtenu le butin|has crafted|crafted|dropped|ramassé|picked up|"
        r"légendaire|legendary|primordial|set ancien)\b",
        re.I,
    )
    _CHAT_INPUT = re.compile(
        r"^\[(?:<[^>]+>\s*)?[^\]]+\]\s*\|?\s*$",
        re.I,
    )

    def extract_new_lines(
        self,
        previous_text: str,
        current_text: str,
    ) -> list[str]:
        previous_lines = self._normalize_lines(previous_text)
        current_lines = self._normalize_lines(current_text)

        if not current_lines:
            return []

        if not previous_lines:
            return self._filter_chat_lines(current_lines[-4:])

        new_lines: list[str] = []
        previous_set = {self._fingerprint(line) for line in previous_lines}

        for line in current_lines:
            fingerprint = self._fingerprint(line)
            if fingerprint not in previous_set:
                new_lines.append(line)

        if not new_lines and current_lines[-1] != previous_lines[-1]:
            new_lines = [current_lines[-1]]

        return self._filter_chat_lines(new_lines)

    def _normalize_lines(self, text: str) -> list[str]:
        lines = []
        for raw_line in text.splitlines():
            cleaned = " ".join(raw_line.split()).strip()
            cleaned = cleaned.replace("|", "l").replace("»", ":").replace("›", ":")
            if cleaned:
                lines.append(cleaned)
        return lines

    def _filter_chat_lines(self, lines: list[str]) -> list[str]:
        filtered: list[str] = []

        for line in lines:
            if len(line) < 2:
                continue
            if line.isdigit():
                continue
            if self._looks_like_ui_noise(line):
                continue
            if self._CHAT_INPUT.match(line):
                continue
            if self._LOOT_PATTERN.search(line) and not self._has_dialogue_marker(line):
                continue
            filtered.append(line)

        return filtered

    @staticmethod
    def _has_dialogue_marker(line: str) -> bool:
        lowered = line.lower()
        return any(
            token in lowered
            for token in (" dit :", " says :", " chuchote :", " whisper :")
        )

    @staticmethod
    def _fingerprint(line: str) -> str:
        normalized = re.sub(r"[^\w\s:]", "", line.lower())
        return " ".join(normalized.split())

    @staticmethod
    def _looks_like_ui_noise(line: str) -> bool:
        lowered = line.lower()
        noise_tokens = (
            "fps",
            "ping",
            "latency",
            "menu",
            "options",
            "settings",
            "inventaire",
            "inventory",
            "forger",
            "forge",
        )
        return any(token in lowered for token in noise_tokens)
