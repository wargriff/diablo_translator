from __future__ import annotations

import re


class ChatLineExtractor:

    _NOISE_PATTERN = re.compile(
        r"^(system|party|clan|whisper|trade|global)\s*:?",
        re.IGNORECASE,
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
            return self._filter_chat_lines(current_lines[-3:])

        new_lines: list[str] = []
        previous_set = set(previous_lines)

        for line in current_lines:
            if line not in previous_set:
                new_lines.append(line)

        if not new_lines and current_lines[-1] != previous_lines[-1]:
            new_lines = [current_lines[-1]]

        return self._filter_chat_lines(new_lines)

    def _normalize_lines(self, text: str) -> list[str]:
        lines = []
        for raw_line in text.splitlines():
            cleaned = " ".join(raw_line.split()).strip()
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
            filtered.append(line)

        return filtered

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
        )
        return any(token in lowered for token in noise_tokens)
