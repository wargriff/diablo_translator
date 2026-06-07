from __future__ import annotations

from src.infrastructure.config_manager import AppConfig


def apply_game_overlay_preset(config: AppConfig) -> AppConfig:
    config.overlay_compact = True
    config.overlay_enabled = True
    config.overlay_borderless = False
    config.overlay_position = "bottom_left"
    config.overlay_above_chat = True
    config.overlay_width = 400
    config.overlay_height = 240
    config.overlay_opacity = 0.93
    config.always_on_top = True
    config.auto_raise_on_game = False
    config.show_only_gameplay_tab = True
    config.auto_start_monitor = True
    config.chat_monitor_enabled = True
    config.capture_from_game_window = True
    config.capture_fullscreen_monitor = True
    config.display_mode = "fullscreen"
    config.resolution_profile = "1080p"
    config.chat_region_preset = "d3_1080p"
    config.ingame_only_mode = True
    config.auto_detect_player = True
    config.auto_copy_outgoing = True
    config.overlay_width = 430
    config.overlay_height = 210
    return config
