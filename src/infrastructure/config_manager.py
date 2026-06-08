import json
from dataclasses import asdict, dataclass

from src.infrastructure.paths import USER_DATA_DIR


@dataclass(slots=True)
class AppConfig:

    language: str = "fr"
    overlay_enabled: bool = True
    overlay_opacity: float = 0.93
    overlay_compact: bool = True
    overlay_position: str = "bottom_left"
    overlay_width: int = 400
    overlay_height: int = 280
    overlay_margin: int = 8
    overlay_borderless: bool = False
    overlay_click_through: bool = False
    overlay_above_chat: bool = True
    overlay_remember_position: bool = True
    overlay_window_x: int = -1
    overlay_window_y: int = -1
    overlay_window_width: int = 0
    overlay_window_height: int = 0
    always_on_top: bool = True
    show_only_gameplay_tab: bool = True
    auto_raise_on_game: bool = False
    auto_start_monitor: bool = True
    capture_fps: int = 1
    translator: str = "google"
    deepl_api_key: str = ""
    ocr_engine: str = "easyocr"
    ocr_languages: str = "en,fr,de,es,it,pt,ru,pl"
    ocr_confidence_min: float = 0.30
    ocr_preprocess: bool = True
    capture_from_game_window: bool = True
    capture_fullscreen_monitor: bool = True
    display_mode: str = "auto"
    resolution_profile: str = "1080p"
    ingame_only_mode: bool = False
    player_name: str = ""
    auto_detect_player: bool = True
    auto_copy_outgoing: bool = True
    auto_send_to_game: bool = True
    startup_delay_seconds: int = 0
    game_startup_grace_seconds: int = 8
    low_cpu_mode: bool = True
    auto_detect_language: bool = True
    bidirectional_mode: bool = True
    default_reply_language: str = "en"
    preserve_mixed_language: bool = True
    chat_monitor_enabled: bool = True
    chat_region_preset: str = "auto"
    voice_input_enabled: bool = False
    speak_translation: bool = False
    voice_language: str = "auto"
    ui_font_size: int = 10
    cache_max_entries: int = 2000
    min_text_length: int = 2
    d3_exe_path: str = ""
    d4_exe_path: str = ""
    immortal_exe_path: str = ""
    hub_sounds_enabled: bool = True
    preferred_launch_game: str = "d4"


class ConfigManager:

    CONFIG_PATH = USER_DATA_DIR / "settings.json"

    @classmethod
    def load(cls) -> AppConfig:
        if not cls.CONFIG_PATH.exists():
            cls.save(AppConfig())

        with open(cls.CONFIG_PATH, encoding="utf-8") as file:
            data = json.load(file)

        known_fields = {field.name for field in AppConfig.__dataclass_fields__.values()}
        filtered = {key: value for key, value in data.items() if key in known_fields}
        config = AppConfig(**filtered)

        version = data.get("_migration_version", 0)
        migrated = False

        if version < 2:
            config.overlay_position = "bottom_left"
            config.overlay_above_chat = True
            config.auto_raise_on_game = False
            config.overlay_compact = True
            config.always_on_top = True
            config.capture_fps = min(config.capture_fps, 1)
            config.low_cpu_mode = True
            config.translator = "google"
            version = 2
            migrated = True

        if version < 3:
            config.capture_from_game_window = True
            config.ocr_preprocess = True
            config.ocr_confidence_min = min(config.ocr_confidence_min, 0.30)
            config.ocr_languages = "en,fr,de,es,it,pt,ru,pl"
            version = 3
            migrated = True

        if version < 4:
            config.capture_fullscreen_monitor = True
            config.display_mode = "auto"
            version = 4
            migrated = True

        if version < 5:
            config.resolution_profile = "1080p"
            config.ingame_only_mode = True
            config.auto_detect_player = True
            config.auto_copy_outgoing = True
            config.chat_region_preset = "d3_1080p"
            if not config.player_name:
                config.player_name = ""
            version = 5
            migrated = True

        if version < 6:
            config.overlay_borderless = False
            config.overlay_remember_position = True
            version = 6
            migrated = True

        if version < 7:
            config.ingame_only_mode = False
            if config.overlay_height < 260:
                config.overlay_height = 280
            version = 7
            migrated = True

        if version < 8:
            config.auto_send_to_game = True
            config.startup_delay_seconds = 3
            version = 8
            migrated = True

        if version < 9:
            config.startup_delay_seconds = 1
            config.game_startup_grace_seconds = 12
            version = 9
            migrated = True

        if version < 10:
            config.startup_delay_seconds = 0
            config.game_startup_grace_seconds = min(config.game_startup_grace_seconds, 8)
            version = 10
            migrated = True

        if version < 11:
            config.d3_exe_path = getattr(config, "d3_exe_path", "") or ""
            config.d4_exe_path = getattr(config, "d4_exe_path", "") or ""
            config.immortal_exe_path = getattr(config, "immortal_exe_path", "") or ""
            config.preferred_launch_game = getattr(config, "preferred_launch_game", "d4") or "d4"
            version = 11
            migrated = True

        if migrated:
            with open(cls.CONFIG_PATH, "w", encoding="utf-8") as file:
                json.dump(
                    {**asdict(config), "_migration_version": version},
                    file,
                    indent=4,
                    ensure_ascii=False,
                )

        return config

    @classmethod
    def save(cls, config: AppConfig) -> None:
        cls.CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

        with open(cls.CONFIG_PATH, "w", encoding="utf-8") as file:
            json.dump(
                asdict(config),
                file,
                indent=4,
                ensure_ascii=False,
            )
