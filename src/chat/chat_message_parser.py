from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True, slots=True)
class ChatMessage:

    raw_line: str
    message: str
    speaker: str | None = None
    channel: str | None = None
    outgoing: bool = False


class ChatMessageParser:

    _SAY_PATTERNS = (
        re.compile(r"\bdit\s*:\s*(.+)$", re.IGNORECASE),
        re.compile(r"\bsays\s*:\s*(.+)$", re.IGNORECASE),
        re.compile(r"\bsagt\s*:\s*(.+)$", re.IGNORECASE),
        re.compile(r"\bdice\s*:\s*(.+)$", re.IGNORECASE),
        re.compile(r"\bschreibt\s*:\s*(.+)$", re.IGNORECASE),
        re.compile(r"\bwrites\s*:\s*(.+)$", re.IGNORECASE),
        re.compile(r"\bschrijft\s*:\s*(.+)$", re.IGNORECASE),
        re.compile(r"\bescribe\s*:\s*(.+)$", re.IGNORECASE),
        re.compile(r"\b(?:говорит|сказал|сказала)\s*:\s*(.+)$", re.IGNORECASE),
        re.compile(r"\b(?:言った|と言いました)\s*[:：]\s*(.+)$", re.IGNORECASE),
    )
    _WHISPER_PATTERNS = (
        re.compile(r"\bchuchote\s*:\s*(.+)$", re.IGNORECASE),
        re.compile(r"\bchuchot[eé]\s*:\s*(.+)$", re.IGNORECASE),
        re.compile(r"\bmurmure\s*:\s*(.+)$", re.IGNORECASE),
        re.compile(r"\bwhispers?\s*:\s*(.+)$", re.IGNORECASE),
        re.compile(r"\bfl[uü]stert\s*:\s*(.+)$", re.IGNORECASE),
        re.compile(r"\bsusurra\s*:\s*(.+)$", re.IGNORECASE),
    )
    _OUTGOING_WHISPER = re.compile(
        r"^(?:À|A|To|Vers)\s*\[(?:<[^>]+>\s*)?(?P<target>[^\]]+)\]\s*:\s*(?P<message>.+)$",
        re.IGNORECASE,
    )
    _D3_LINE = re.compile(
        r"^\[(?P<channel>[^\]]+)\]\s*:\s*\[(?:<[^>]+>\s*)?(?P<speaker>[^\]]+)\]\s*"
        r"(?:dit|says|sagt|dice|schreibt|writes|chuchote|whispers?)\s*:\s*(?P<message>.+)$",
        re.IGNORECASE,
    )
    _WHISPER_LINE = re.compile(
        r"^\[(?:<[^>]+>\s*)?(?P<speaker>[^\]]+)\]\s*"
        r"(?:chuchote|chuchot[eé]|murmure|whispers?|fl[uü]stert|susurra)\s*:\s*(?P<message>.+)$",
        re.IGNORECASE,
    )
    _NOISE_PREFIXES = (
        "moteur:",
        "cache:",
        "overlay:",
        "surveillance",
        "mode :",
        "traductions du chat",
        "parlez dans diablo",
        "ocr actif",
        "ocr :",
    )
    _SYSTEM_PATTERNS = (
        re.compile(r"\b(a forgé|has crafted|crafted|dropped|ramassé|picked up)\b", re.I),
        re.compile(r"\b(légendaire|legendary|set ancien|ancient|primordial)\b", re.I),
        re.compile(r"^\[\s*(powerleveling|trade|clan|party|global)\s*\]\s*$", re.I),
        re.compile(r"^\[\s*.+\s*\]\s*$"),
    )
    _CHAT_INPUT = re.compile(
        r"^\[(?:<[^>]+>\s*)?[^\]]+\]\s*\|?\s*$",
        re.IGNORECASE,
    )

    @classmethod
    def parse(cls, line: str) -> ChatMessage | None:
        cleaned = " ".join(line.split()).strip()
        if not cleaned:
            return None

        lowered = cleaned.lower()
        if any(lowered.startswith(prefix) for prefix in cls._NOISE_PREFIXES):
            return None

        if cls._CHAT_INPUT.match(cleaned):
            return None

        if cls._is_system_or_loot(cleaned):
            return None

        outgoing = cls._OUTGOING_WHISPER.match(cleaned)
        if outgoing:
            message = outgoing.group("message").strip()
            if cls._is_valid_message(message):
                return ChatMessage(
                    raw_line=cleaned,
                    message=message,
                    speaker=None,
                    outgoing=True,
                )

        whisper_match = cls._WHISPER_LINE.match(cleaned)
        if whisper_match:
            message = whisper_match.group("message").strip()
            if cls._is_valid_message(message):
                return ChatMessage(
                    raw_line=cleaned,
                    message=message,
                    speaker=whisper_match.group("speaker").strip(),
                    channel="whisper",
                )

        d3_match = cls._D3_LINE.match(cleaned)
        if d3_match:
            message = d3_match.group("message").strip()
            if cls._is_valid_message(message):
                return ChatMessage(
                    raw_line=cleaned,
                    message=message,
                    speaker=d3_match.group("speaker").strip(),
                    channel=d3_match.group("channel").strip(),
                )

        for pattern in cls._WHISPER_PATTERNS:
            match = pattern.search(cleaned)
            if match:
                message = match.group(1).strip()
                if cls._is_valid_message(message):
                    speaker = cls._extract_speaker(cleaned)
                    return ChatMessage(
                        raw_line=cleaned,
                        message=message,
                        speaker=speaker,
                        channel="whisper",
                    )

        for pattern in cls._SAY_PATTERNS:
            match = pattern.search(cleaned)
            if match:
                message = match.group(1).strip()
                if cls._is_valid_message(message):
                    speaker = cls._extract_speaker(cleaned)
                    return ChatMessage(
                        raw_line=cleaned,
                        message=message,
                        speaker=speaker,
                    )

        if "]" in cleaned and ":" in cleaned:
            tail = cleaned.rsplit(":", 1)[-1].strip()
            if cls._is_valid_message(tail) and not tail.startswith("["):
                return ChatMessage(raw_line=cleaned, message=tail)

        if cls._looks_like_player_message(cleaned):
            return ChatMessage(raw_line=cleaned, message=cleaned)

        return None

    @classmethod
    def extract_message(cls, line: str) -> str | None:
        parsed = cls.parse(line)
        return parsed.message if parsed else None

    @classmethod
    def _extract_speaker(cls, line: str) -> str | None:
        patterns = (
            r"\[(?:<[^>]+>\s*)?([^\]]+)\]\s*(?:dit|says|chuchote|whispers?)\s*:",
            r"^\[(?:<[^>]+>\s*)?([^\]]+)\]",
        )
        for pattern in patterns:
            match = re.search(pattern, line, re.I)
            if match:
                return match.group(1).strip()
        return None

    @classmethod
    def _is_system_or_loot(cls, line: str) -> bool:
        lowered = line.lower()
        if any(
            token in lowered
            for token in (" dit :", " says :", " chuchote :", " whisper :")
        ):
            return False
        for pattern in cls._SYSTEM_PATTERNS:
            if pattern.search(line):
                return True
        return False

    @classmethod
    def _looks_like_player_message(cls, line: str) -> bool:
        if len(line) < 3:
            return False
        if line.startswith("[") and "]" in line:
            return any(
                token in line.lower()
                for token in (" dit :", " says :", " chuchote :", " whisper :")
            )
        if re.search(r"[àâäéèêëïîôùûüç]", line, re.I):
            return True
        if re.search(r"[а-яё]", line, re.I):
            return True
        if re.search(r"[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]", line):
            return True
        return bool(re.search(r"[a-zA-Z]{3,}", line))

    @classmethod
    def _is_valid_message(cls, message: str) -> bool:
        cleaned = message.strip()
        if len(cleaned) < 2:
            return False
        if cleaned.startswith("[") and cleaned.endswith("]"):
            return False
        if cls._is_system_or_loot(cleaned):
            return False
        return True
