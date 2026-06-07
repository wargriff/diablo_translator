from __future__ import annotations

from src.application.overlay_preset import apply_game_overlay_preset
from src.infrastructure.config_manager import AppConfig, ConfigManager


class ConfigService:

    def __init__(self) -> None:
        self._config = ConfigManager.load()

    @property
    def config(self) -> AppConfig:
        return self._config

    def replace(self, config: AppConfig, *, persist: bool = True) -> None:
        self._config = config
        if persist:
            ConfigManager.save(config)

    def apply_overlay_preset(self) -> AppConfig:
        config = apply_game_overlay_preset(self._config)
        self.replace(config)
        return config
