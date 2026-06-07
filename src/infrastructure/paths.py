import sys
from pathlib import Path


def _resolve_project_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parents[2]


def _resolve_bundle_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", _resolve_project_root()))

    return _resolve_project_root()


PROJECT_ROOT = _resolve_project_root()
BUNDLE_ROOT = _resolve_bundle_root()

ASSETS_DIR = BUNDLE_ROOT / "assets"
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
APP_ICON_SVG = ICONS_DIR / "app.svg"
APP_ICON_ICO = ICONS_DIR / "app.ico"
APP_ICON_PNG = ICONS_DIR / "app.png"
APP_ICON = APP_ICON_ICO if APP_ICON_ICO.exists() else APP_ICON_SVG

PROJECT_DIRECTORIES = (
    CACHE_DIR,
    CACHE_TRANSLATIONS_DIR,
    CACHE_OCR_DIR,
    MODELS_DIR,
    USER_DATA_DIR,
    LOGS_DIR,
    EXPORTS_DIR,
)


def ensure_project_dirs() -> None:
    for directory in PROJECT_DIRECTORIES:
        directory.mkdir(parents=True, exist_ok=True)


__all__ = [
    "APP_ICON",
    "APP_ICON_ICO",
    "APP_ICON_PNG",
    "APP_ICON_SVG",
    "ASSETS_DIR",
    "BUNDLE_ROOT",
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
