from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256

from src.infrastructure.paths import CACHE_TRANSLATIONS_DIR, ensure_project_dirs


@dataclass(slots=True)
class CacheStats:

    hits: int = 0
    misses: int = 0
    entries: int = 0


class TranslationCache:

    def __init__(self, max_entries: int = 5000) -> None:
        ensure_project_dirs()
        self._max_entries = max_entries
        self._path = CACHE_TRANSLATIONS_DIR / "cache.json"
        self._store: dict[str, dict[str, str]] = self._load()
        self.stats = CacheStats(entries=len(self._store))

    def get(self, source_text: str, target_language: str, provider: str) -> str | None:
        key = self._make_key(source_text, target_language, provider)
        entry = self._store.get(key)
        if not entry:
            self.stats.misses += 1
            return None

        self.stats.hits += 1
        return entry["translated"]

    def set(
        self,
        source_text: str,
        translated: str,
        *,
        target_language: str,
        provider: str,
        source_language: str | None = None,
    ) -> None:
        key = self._make_key(source_text, target_language, provider)
        self._store[key] = {
            "source": source_text,
            "translated": translated,
            "target": target_language,
            "provider": provider,
            "source_language": source_language or "",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self._trim()
        self.stats.entries = len(self._store)
        self._save()

    def clear(self) -> None:
        self._store.clear()
        self.stats = CacheStats()
        self._save()

    def _make_key(self, source_text: str, target_language: str, provider: str) -> str:
        raw = f"{provider}|{target_language}|{source_text.strip().casefold()}"
        return sha256(raw.encode("utf-8")).hexdigest()

    def _trim(self) -> None:
        if len(self._store) <= self._max_entries:
            return

        sorted_items = sorted(
            self._store.items(),
            key=lambda item: item[1].get("updated_at", ""),
        )
        overflow = len(self._store) - self._max_entries
        for key, _ in sorted_items[:overflow]:
            del self._store[key]

    def _load(self) -> dict[str, dict[str, str]]:
        if not self._path.exists():
            return {}

        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

        if isinstance(data, dict):
            return data
        return {}

    def _save(self) -> None:
        self._path.write_text(
            json.dumps(self._store, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
