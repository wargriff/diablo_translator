import json
from dataclasses import asdict, dataclass

from src.infrastructure.paths import USER_DATA_DIR


@dataclass(slots=True)
class AppConfig:

    language: str = "fr"
    overlay_enabled: bool = True
    overlay_opacity: float = 0.88
    overlay_compact: bool = True
    overlay_position: str = "top_right"
    overlay_width: int = 460
    overlay_height: int = 560
    overlay_margin: int = 16
    overlay_borderless: bool = False
    overlay_click_through: bool = False
    always_on_top: bool = True
    show_only_gameplay_tab: bool = True
    auto_raise_on_game: bool = True
    auto_start_monitor: bool = True
    capture_fps: int = 2
    translator: str = "google"
    deepl_api_key: str = ""
    ocr_engine: str = "easyocr"
    ocr_languages: str = "en,fr,de,es"
    ocr_confidence_min: float = 0.35
    low_cpu_mode: bool = False
    auto_detect_language: bool = True
    bidirectional_mode: bool = True
    default_reply_language: str = "en"
    preserve_mixed_language: bool = True
    chat_monitor_enabled: bool = True
    chat_region_preset: str = "auto"
    voice_input_enabled: bool = False
    speak_translation: bool = False
    voice_language: str = "auto"
    ui_font_size: int = 11
    cache_max_entries: int = 5000
    min_text_length: int = 2


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
        return AppConfig(**filtered)

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
