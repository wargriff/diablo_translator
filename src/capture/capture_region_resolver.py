from __future__ import annotations

from dataclasses import dataclass

from src.capture.display_service import DisplayService, MonitorInfo, ScreenRect
from src.capture.game_window_service import GameWindowService
from src.chat.chat_region import get_preset, resolve_preset_key
from src.infrastructure.config_manager import AppConfig


@dataclass(frozen=True, slots=True)
class ResolvedCaptureRegion:

    left: int
    top: int
    width: int
    height: int
    preset_key: str
    source: str
    display_mode: str
    monitor_index: int


class CaptureRegionResolver:

    @classmethod
    def resolve(
        cls,
        game_detection_service,
        config: AppConfig,
    ) -> ResolvedCaptureRegion:
        preset_key = cls._resolve_preset_key(game_detection_service, config)
        preset = get_preset(preset_key)

        if config.capture_from_game_window:
            window = GameWindowService.find_primary_game_info(game_detection_service)
            if window is not None:
                base_rect, source = cls._select_base_rect(window, config)
                region = cls._apply_preset(base_rect, preset)
                return ResolvedCaptureRegion(
                    left=region.left,
                    top=region.top,
                    width=region.width,
                    height=region.height,
                    preset_key=preset_key,
                    source=source,
                    display_mode=window.display_mode,
                    monitor_index=window.monitor_index,
                )

        monitor = DisplayService.primary_monitor()
        region = cls._apply_preset(cls._monitor_to_rect(monitor), preset)
        return ResolvedCaptureRegion(
            left=region.left,
            top=region.top,
            width=region.width,
            height=region.height,
            preset_key=preset_key,
            source="monitor_primary",
            display_mode="monitor",
            monitor_index=monitor.index,
        )

    @classmethod
    def _select_base_rect(cls, window, config: AppConfig) -> tuple[ScreenRect, str]:
        if config.display_mode == "fullscreen":
            return window.window, "game_fullscreen_forced"
        if config.display_mode == "windowed":
            return window.client, "game_client_forced"

        if window.is_fullscreen or window.display_mode in {"fullscreen", "borderless"}:
            if config.capture_fullscreen_monitor:
                monitor = DisplayService.monitor_for_rect(window.window)
                return cls._monitor_to_rect(monitor), "game_monitor_fullscreen"
            return window.window, "game_window_fullscreen"

        return window.client, "game_client"

    @staticmethod
    def _resolve_preset_key(game_detection_service, config: AppConfig) -> str:
        status = game_detection_service.scan()
        game_key = status.primary_game.key if status.primary_game else None
        return resolve_preset_key(
            game_key,
            config.chat_region_preset,
            config.resolution_profile,
        )

    @staticmethod
    def _monitor_to_rect(monitor: MonitorInfo) -> ScreenRect:
        return ScreenRect(
            left=monitor.left,
            top=monitor.top,
            width=monitor.width,
            height=monitor.height,
        )

    @staticmethod
    def _apply_preset(base: ScreenRect, preset) -> ScreenRect:
        return ScreenRect(
            left=base.left + int(base.width * preset.left_pct),
            top=base.top + int(base.height * preset.top_pct),
            width=max(120, int(base.width * preset.width_pct)),
            height=max(80, int(base.height * preset.height_pct)),
        )
