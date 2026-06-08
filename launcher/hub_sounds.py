from __future__ import annotations

import math
import struct
import sys
import wave
from pathlib import Path

from src.infrastructure.config_manager import ConfigManager
from src.infrastructure.paths import USER_DATA_DIR

SOUNDS_DIR = USER_DATA_DIR / "sounds"


def _write_tone(
    path: Path,
    frequency: float,
    duration: float,
    *,
    volume: float = 0.25,
    sample_rate: int = 22050,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sample_count = int(sample_rate * duration)
    with wave.open(str(path), "w") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        frames = bytearray()
        for index in range(sample_count):
            time = index / sample_rate
            envelope = math.exp(-4.5 * time / max(duration, 0.01))
            sample = int(volume * 32767 * envelope * math.sin(2 * math.pi * frequency * time))
            frames.extend(struct.pack("<h", sample))
        handle.writeframes(frames)


def ensure_sound_assets() -> dict[str, Path]:
    SOUNDS_DIR.mkdir(parents=True, exist_ok=True)
    files = {
        "open": SOUNDS_DIR / "sanctuary_open.wav",
        "launch": SOUNDS_DIR / "ritual_launch.wav",
        "success": SOUNDS_DIR / "ember_chime.wav",
    }
    if not files["open"].exists():
        _write_tone(files["open"], 146.0, 0.6, volume=0.2)
    if not files["launch"].exists():
        _write_tone(files["launch"], 220.0, 0.28, volume=0.22)
    if not files["success"].exists():
        _write_tone(files["success"], 587.0, 0.2, volume=0.18)
    return files


class HubSoundPlayer:
    def __init__(self) -> None:
        self._files = ensure_sound_assets()
        self._effect = None
        if sys.platform != "win32":
            try:
                from PyQt6.QtCore import QUrl
                from PyQt6.QtMultimedia import QSoundEffect

                self._effect = QSoundEffect()
                self._effect.setVolume(0.35)
                self._QUrl = QUrl
            except Exception:
                self._effect = None
                self._QUrl = None
        else:
            self._QUrl = None

    @property
    def enabled(self) -> bool:
        return ConfigManager.load().hub_sounds_enabled

    def set_enabled(self, value: bool) -> None:
        config = ConfigManager.load()
        config.hub_sounds_enabled = value
        ConfigManager.save(config)

    def play(self, key: str) -> None:
        if not self.enabled:
            return

        path = self._files.get(key)
        if path is None or not path.exists():
            return

        if sys.platform == "win32":
            import winsound

            winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
            return

        if self._effect is not None and self._QUrl is not None:
            self._effect.setSource(self._QUrl.fromLocalFile(str(path.resolve())))
            self._effect.play()
