from __future__ import annotations

from dataclasses import replace

from src.infrastructure.config_manager import AppConfig


def profile_ultimate_d3_1080p(config: AppConfig) -> AppConfig:
    return replace(
        config,
        language="fr",
        resolution_profile="1080p",
        chat_region_preset="d3_1080p",
        display_mode="fullscreen",
        capture_fullscreen_monitor=True,
        capture_from_game_window=True,
        ingame_only_mode=False,
        overlay_compact=True,
        overlay_enabled=True,
        overlay_borderless=True,
        overlay_position="bottom_left",
        overlay_above_chat=True,
        overlay_width=430,
        overlay_height=280,
        overlay_opacity=0.92,
        overlay_click_through=False,
        always_on_top=True,
        auto_raise_on_game=False,
        auto_start_monitor=True,
        chat_monitor_enabled=True,
        bidirectional_mode=True,
        auto_detect_player=True,
        auto_detect_language=True,
        ocr_preprocess=True,
        ocr_confidence_min=0.28,
        capture_fps=1,
        low_cpu_mode=True,
        preserve_mixed_language=True,
        default_reply_language="en",
        translator="google",
    )


def profile_performance(config: AppConfig) -> AppConfig:
    updated = profile_ultimate_d3_1080p(config)
    return replace(
        updated,
        capture_fps=1,
        low_cpu_mode=True,
        ocr_confidence_min=0.32,
        overlay_height=180,
    )


def profile_streamer(config: AppConfig) -> AppConfig:
    updated = profile_ultimate_d3_1080p(config)
    return replace(
        updated,
        overlay_opacity=0.88,
        overlay_width=500,
        overlay_height=240,
        overlay_click_through=True,
    )


PROFILE_CATALOG = {
    "ultimate_d3_1080p": {
        "title": "Ultimate D3 — 1080p Plein écran",
        "subtitle": "Profil pro recommandé · OCR calibré · Chat in-game only",
        "apply": profile_ultimate_d3_1080p,
    },
    "performance": {
        "title": "Performance",
        "subtitle": "CPU minimal · overlay compact",
        "apply": profile_performance,
    },
    "streamer": {
        "title": "Streamer",
        "subtitle": "Overlay large · clics traversants",
        "apply": profile_streamer,
    },
}
