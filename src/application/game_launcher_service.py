from __future__ import annotations

import subprocess
from dataclasses import replace
from pathlib import Path

from src.application.config_service import ConfigService
from src.game_detection import SUPPORTED_GAMES
from src.infrastructure.config_manager import ConfigManager

_GAME_KEYS = {game.key for game in SUPPORTED_GAMES}


class GameLauncherService:

    def __init__(self, config_service: ConfigService) -> None:
        self._config_service = config_service

    def resolve_path(self, game_key: str) -> str:
        config = self._config_service.config
        mapping = {
            "d3": config.d3_exe_path,
            "d4": config.d4_exe_path,
            "immortal": config.immortal_exe_path,
        }
        return mapping.get(game_key, "").strip()

    def save_path(self, game_key: str, path: str) -> None:
        config = self._config_service.config
        cleaned = path.strip()
        if game_key == "d3":
            updated = replace(config, d3_exe_path=cleaned)
        elif game_key == "d4":
            updated = replace(config, d4_exe_path=cleaned)
        elif game_key == "immortal":
            updated = replace(config, immortal_exe_path=cleaned)
        else:
            raise ValueError(f"Jeu inconnu : {game_key}")

        self._config_service.replace(updated)
        ConfigManager.save(updated)

    def game_status(self, game_key: str) -> dict[str, str | bool]:
        from src.game_detection import GameDetectionService

        path = self.resolve_path(game_key)
        valid, error = self.validate_path(game_key, path) if path else (False, "")
        detection = GameDetectionService().scan()
        running = game_key in detection.active_processes

        return {
            "path": path,
            "path_valid": valid and bool(path),
            "path_error": error,
            "running": running,
            "process": detection.active_processes.get(game_key, ""),
        }

    def validate_path(self, game_key: str, path: str | None = None) -> tuple[bool, str]:
        if game_key not in _GAME_KEYS:
            return False, f"Jeu inconnu : {game_key}"

        raw = (path if path is not None else self.resolve_path(game_key)).strip()
        if not raw:
            return False, "Chemin exe non configuré."

        exe = Path(raw)
        if not exe.is_file():
            return False, f"Exe introuvable : {raw}"

        return True, ""

    def launch(self, game_key: str) -> tuple[bool, str]:
        ok, error = self.validate_path(game_key)
        if not ok:
            return False, error

        exe = Path(self.resolve_path(game_key))
        game = next(game for game in SUPPORTED_GAMES if game.key == game_key)

        try:
            subprocess.Popen(
                [str(exe)],
                cwd=str(exe.parent),
                shell=False,
            )
        except OSError as exc:
            return False, f"Impossible de lancer {game.title} : {exc}"

        return True, f"{game.title} lancé."

    def preferred_game_key(self) -> str:
        key = self._config_service.config.preferred_launch_game
        if key in _GAME_KEYS:
            return key
        return "d4"

    def set_preferred_game(self, game_key: str) -> None:
        if game_key not in _GAME_KEYS:
            return
        updated = replace(config, preferred_launch_game=game_key)
        self._config_service.replace(updated)
        ConfigManager.save(updated)

    def launch_preferred(self) -> tuple[bool, str]:
        return self.launch(self.preferred_game_key())
