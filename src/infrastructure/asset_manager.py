from __future__ import annotations

from pathlib import Path

from PyQt6.QtGui import QFont, QFontDatabase, QIcon

from src.infrastructure.paths import (
    APP_ICON_ICO,
    APP_ICON_PNG,
    APP_ICON_SVG,
    DEFAULT_THEME,
    FONTS_DIR,
    ICONS_DIR,
    THEMES_DIR,
    ensure_project_dirs,
)


class AssetManager:

    _fonts_loaded = False

    @classmethod
    def prepare(cls) -> None:
        ensure_project_dirs()
        cls.load_fonts()

    @classmethod
    def load_fonts(cls) -> None:
        if cls._fonts_loaded:
            return

        for font_path in FONTS_DIR.glob("*.ttf"):
            QFontDatabase.addApplicationFont(str(font_path))
        for font_path in FONTS_DIR.glob("*.otf"):
            QFontDatabase.addApplicationFont(str(font_path))

        cls._fonts_loaded = True

    @classmethod
    def ui_font(cls, size: int = 10, bold: bool = False) -> QFont:
        families = QFontDatabase.families()
        for candidate in ("Cinzel", "Segoe UI", "Arial"):
            if candidate in families:
                font = QFont(candidate, size)
                font.setBold(bold)
                return font

        font = QFont("Segoe UI", size)
        font.setBold(bold)
        return font

    @classmethod
    def monospace_font(cls, size: int = 10) -> QFont:
        families = QFontDatabase.families()
        for candidate in ("Cascadia Mono", "Consolas", "Courier New"):
            if candidate in families:
                return QFont(candidate, size)

        font = QFont("Consolas", size)
        font.setStyleHint(QFont.StyleHint.Monospace)
        return font

    @classmethod
    def load_stylesheet(cls, theme_name: str = "diablo_dark") -> str:
        theme_path = THEMES_DIR / f"{theme_name}.qss"
        if theme_path.exists():
            return theme_path.read_text(encoding="utf-8")

        if DEFAULT_THEME.exists():
            return DEFAULT_THEME.read_text(encoding="utf-8")

        return ""

    @classmethod
    def icon(cls, name: str) -> QIcon:
        for extension in (".svg", ".png"):
            path = ICONS_DIR / f"{name}{extension}"
            if path.exists():
                return QIcon(str(path))
        return QIcon()

    @classmethod
    def app_icon(cls) -> QIcon:
        for path in (APP_ICON_ICO, APP_ICON_PNG, APP_ICON_SVG):
            if path.exists():
                return QIcon(str(path))
        return cls.icon("app")

    @classmethod
    def apply_window_branding(cls, window) -> None:
        stylesheet = cls.load_stylesheet()
        if stylesheet:
            window.setStyleSheet(stylesheet)

        icon = cls.app_icon()
        if not icon.isNull():
            window.setWindowIcon(icon)
