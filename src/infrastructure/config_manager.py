import json
from dataclasses import asdict, dataclass

from src.infrastructure.paths import USER_DATA_DIR


@dataclass(slots=True)
class AppConfig:

    language: str = "fr"
    overlay_enabled: bool = True
    overlay_opacity: float = 0.85
    capture_fps: int = 2
    translator: str = "google"
    ocr_engine: str = "easyocr"
    low_cpu_mode: bool = False


class ConfigManager:

    CONFIG_PATH = USER_DATA_DIR / "settings.json"

    @classmethod
    def load(cls) -> AppConfig:
        if not cls.CONFIG_PATH.exists():
            cls.save(AppConfig())

        with open(cls.CONFIG_PATH, encoding="utf-8") as file:
            data = json.load(file)

        return AppConfig(**data)

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
