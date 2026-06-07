from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ChatRegionPreset:

    key: str
    title: str
    left_pct: float
    top_pct: float
    width_pct: float
    height_pct: float


CHAT_REGION_PRESETS: tuple[ChatRegionPreset, ...] = (
    ChatRegionPreset("auto", "Auto (jeu détecté)", 0.02, 0.72, 0.38, 0.26),
    ChatRegionPreset("d4", "Diablo IV", 0.02, 0.72, 0.38, 0.26),
    ChatRegionPreset("d3", "Diablo III", 0.02, 0.70, 0.40, 0.28),
    ChatRegionPreset(
        "immortal",
        "Diablo Immortal",
        0.02,
        0.68,
        0.42,
        0.30,
    ),
)

GAME_TO_PRESET = {
    "d4": "d4",
    "d3": "d3",
    "immortal": "immortal",
}


def get_preset(key: str) -> ChatRegionPreset:
    for preset in CHAT_REGION_PRESETS:
        if preset.key == key:
            return preset
    return CHAT_REGION_PRESETS[0]
