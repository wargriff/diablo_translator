from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SupportedGame:

    key: str
    title: str
    short_title: str
    process_names: tuple[str, ...]


SUPPORTED_GAMES: tuple[SupportedGame, ...] = (
    SupportedGame(
        key="d3",
        title="Diablo III",
        short_title="D3",
        process_names=("Diablo III64.exe", "Diablo III.exe"),
    ),
    SupportedGame(
        key="d4",
        title="Diablo IV",
        short_title="D4",
        process_names=("Diablo IV.exe", "DiabloIV.exe"),
    ),
    SupportedGame(
        key="immortal",
        title="Diablo Immortal",
        short_title="Immortal",
        process_names=("DiabloImmortal.exe", "Diablo Immortal.exe"),
    ),
)


@dataclass(slots=True)
class GameDetectionStatus:

    running_games: list[SupportedGame]
    active_processes: dict[str, str]

    @property
    def is_any_running(self) -> bool:
        return bool(self.running_games)

    @property
    def primary_game(self) -> SupportedGame | None:
        if not self.running_games:
            return None
        return self.running_games[0]

    def summary(self) -> str:
        if not self.running_games:
            return "Aucun jeu Diablo détecté"

        names = ", ".join(game.title for game in self.running_games)
        return f"Jeux actifs : {names}"


class GameDetectionService:

    CACHE_TTL_SECONDS = 0.75

    def __init__(self) -> None:
        self._cache: GameDetectionStatus | None = None
        self._cache_at = 0.0

    def scan(self, *, force: bool = False) -> GameDetectionStatus:
        import psutil
        import time

        now = time.time()
        if (
            not force
            and self._cache is not None
            and now - self._cache_at < self.CACHE_TTL_SECONDS
        ):
            return self._cache

        running: list[SupportedGame] = []
        active_processes: dict[str, str] = {}
        process_index = self._build_process_index(psutil)

        for game in SUPPORTED_GAMES:
            matched = self._match_game(game, process_index)
            if matched:
                running.append(game)
                active_processes[game.key] = matched

        self._cache = GameDetectionStatus(
            running_games=running,
            active_processes=active_processes,
        )
        self._cache_at = now
        return self._cache

    def invalidate_cache(self) -> None:
        self._cache = None
        self._cache_at = 0.0

    def is_running(self) -> bool:
        return self.scan().is_any_running

    def is_game_running(self, game_key: str) -> bool:
        return any(game.key == game_key for game in self.scan().running_games)

    @staticmethod
    def _build_process_index(psutil_module) -> dict[str, str]:
        index: dict[str, str] = {}

        for process in psutil_module.process_iter(["name"]):
            name = process.info.get("name")
            if not name:
                continue
            index[name.casefold()] = name

        return index

    @staticmethod
    def _match_game(
        game: SupportedGame,
        process_index: dict[str, str],
    ) -> str | None:
        for process_name in game.process_names:
            matched = process_index.get(process_name.casefold())
            if matched:
                return matched

        return None
