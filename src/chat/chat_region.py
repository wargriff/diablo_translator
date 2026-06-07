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
    ChatRegionPreset("auto", "Auto (jeu + résolution)", 0.0, 0.74, 0.46, 0.24),
    ChatRegionPreset(
        "d3_1080p",
        "Diablo III — 1080p plein écran",
        0.0,
        0.62,
        0.36,
        0.32,
    ),
    ChatRegionPreset("d3", "Diablo III (générique)", 0.0, 0.73, 0.50, 0.25),
    ChatRegionPreset("d4", "Diablo IV", 0.0, 0.74, 0.46, 0.24),
    ChatRegionPreset("immortal", "Diablo Immortal", 0.0, 0.70, 0.50, 0.28),
)

GAME_TO_PRESET = {
    "d4": "d4",
    "d3": "d3",
    "immortal": "immortal",
}

RESOLUTION_PRESETS = {
    ("d3", "1080p"): "d3_1080p",
    ("d4", "1080p"): "d4",
    ("immortal", "1080p"): "immortal",
}


def get_preset(key: str) -> ChatRegionPreset:
    for preset in CHAT_REGION_PRESETS:
        if preset.key == key:
            return preset
    return CHAT_REGION_PRESETS[0]


def resolve_preset_key(game_key: str | None, config_preset: str, resolution_profile: str) -> str:
    if config_preset != "auto":
        return config_preset

    if game_key and resolution_profile:
        matched = RESOLUTION_PRESETS.get((game_key, resolution_profile))
        if matched:
            return matched

    if game_key:
        return GAME_TO_PRESET.get(game_key, "d3_1080p")

    return "d3_1080p"
