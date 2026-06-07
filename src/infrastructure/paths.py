from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ASSETS_DIR = PROJECT_ROOT / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
ICONS_DIR = ASSETS_DIR / "icons"
THEMES_DIR = ASSETS_DIR / "themes"

CACHE_DIR = PROJECT_ROOT / "cache"
CACHE_TRANSLATIONS_DIR = CACHE_DIR / "translations"
CACHE_OCR_DIR = CACHE_DIR / "ocr"

MODELS_DIR = PROJECT_ROOT / "models"
BUILD_DIR = PROJECT_ROOT / "build"
TESTS_DIR = PROJECT_ROOT / "tests"

USER_DATA_DIR = PROJECT_ROOT / "user_data"
LOGS_DIR = PROJECT_ROOT / "logs"
EXPORTS_DIR = USER_DATA_DIR / "exports"

DEFAULT_THEME = THEMES_DIR / "diablo_dark.qss"
APP_ICON = ICONS_DIR / "app.svg"

PROJECT_DIRECTORIES = (
    CACHE_DIR,
    CACHE_TRANSLATIONS_DIR,
    CACHE_OCR_DIR,
    MODELS_DIR,
    BUILD_DIR,
    FONTS_DIR,
    ICONS_DIR,
    THEMES_DIR,
    USER_DATA_DIR,
    LOGS_DIR,
    EXPORTS_DIR,
)


def ensure_project_dirs() -> None:
    for directory in PROJECT_DIRECTORIES:
        directory.mkdir(parents=True, exist_ok=True)


__all__ = [
    "APP_ICON",
    "ASSETS_DIR",
    "BUILD_DIR",
    "CACHE_DIR",
    "CACHE_OCR_DIR",
    "CACHE_TRANSLATIONS_DIR",
    "DEFAULT_THEME",
    "EXPORTS_DIR",
    "FONTS_DIR",
    "ICONS_DIR",
    "LOGS_DIR",
    "MODELS_DIR",
    "PROJECT_DIRECTORIES",
    "PROJECT_ROOT",
    "TESTS_DIR",
    "THEMES_DIR",
    "USER_DATA_DIR",
    "ensure_project_dirs",
]
