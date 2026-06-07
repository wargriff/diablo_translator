from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget

from src.infrastructure.config_manager import AppConfig


class WindowBehaviorService:

    POSITIONS = {
        "top_right": lambda screen, width, height, margin: (
            screen.right() - width - margin,
            screen.top() + margin,
        ),
        "top_left": lambda screen, width, height, margin: (
            screen.left() + margin,
            screen.top() + margin,
        ),
        "bottom_right": lambda screen, width, height, margin: (
            screen.right() - width - margin,
            screen.bottom() - height - margin,
        ),
        "bottom_left": lambda screen, width, height, margin: (
            screen.left() + margin,
            screen.bottom() - height - margin,
        ),
        "center_right": lambda screen, width, height, margin: (
            screen.right() - width - margin,
            screen.top() + (screen.height() - height) // 2,
        ),
    }

    @classmethod
    def raise_if_game_mode(cls, window: QMainWindow, config: AppConfig) -> None:
        if not config.auto_raise_on_game:
            return

        if not (config.always_on_top or config.overlay_compact):
            return

        window.raise_()

    @classmethod
    def apply(cls, window: QMainWindow, config: AppConfig) -> None:
        focused = QApplication.focusWidget()
        cls._apply_flags(window, config)
        cls._apply_opacity(window, config)
        cls._apply_geometry(window, config)
        cls._apply_tabs(window, config)
        cls._apply_click_through(window, config)
        window.show()

        if focused is not None and focused.isEnabled():
            focused.setFocus(Qt.FocusReason.OtherFocusReason)

    @staticmethod
    def _apply_flags(window: QMainWindow, config: AppConfig) -> None:
        flags = window.windowFlags()
        flags |= Qt.WindowType.Window

        if config.always_on_top or config.overlay_compact:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint

        if config.overlay_borderless and config.overlay_compact:
            flags |= Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        else:
            flags &= ~Qt.WindowType.FramelessWindowHint
            flags &= ~Qt.WindowType.Tool

        window.setWindowFlags(flags)

    @staticmethod
    def _apply_opacity(window: QMainWindow, config: AppConfig) -> None:
        if config.overlay_enabled:
            window.setWindowOpacity(max(0.25, min(config.overlay_opacity, 1.0)))
        else:
            window.setWindowOpacity(1.0)

    @classmethod
    def _apply_geometry(cls, window: QMainWindow, config: AppConfig) -> None:
        screen = QApplication.primaryScreen()
        if screen is None:
            return

        area = screen.availableGeometry()
        margin = config.overlay_margin

        if config.overlay_compact:
            width = config.overlay_width
            height = config.overlay_height
            position_fn = cls.POSITIONS.get(
                config.overlay_position,
                cls.POSITIONS["top_right"],
            )
            x, y = position_fn(area, width, height, margin)
            window.setGeometry(x, y, width, height)
            window.setMinimumSize(320, 360)
            window.setMaximumSize(900, 1200)
            return

        window.setMinimumSize(960, 640)
        window.setMaximumSize(16777215, 16777215)
        if window.width() < 960:
            window.resize(1480, 940)

    @staticmethod
    def _apply_tabs(window: QMainWindow, config: AppConfig) -> None:
        tabs = window.findChild(QTabWidget)
        if tabs is None:
            return

        for index in range(tabs.count()):
            visible = True
            if config.overlay_compact and config.show_only_gameplay_tab:
                visible = tabs.tabText(index).lower() == "gameplay"
            tabs.setTabVisible(index, visible)

        if config.overlay_compact and config.show_only_gameplay_tab:
            gameplay_index = next(
                (
                    index
                    for index in range(tabs.count())
                    if tabs.tabText(index).lower() == "gameplay"
                ),
                0,
            )
            tabs.setCurrentIndex(gameplay_index)

    @staticmethod
    def _apply_click_through(window: QMainWindow, config: AppConfig) -> None:
        if not config.overlay_click_through:
            WindowBehaviorService._set_click_through(window, False)
            return

        WindowBehaviorService._set_click_through(window, True)

    @staticmethod
    def _set_click_through(window: QMainWindow, enabled: bool) -> None:
        try:
            import ctypes

            hwnd = int(window.winId())
            gwl_exstyle = -20
            ws_ex_layered = 0x00080000
            ws_ex_transparent = 0x00000020

            style = ctypes.windll.user32.GetWindowLongW(hwnd, gwl_exstyle)
            if enabled:
                style |= ws_ex_layered | ws_ex_transparent
            else:
                style &= ~ws_ex_transparent

            ctypes.windll.user32.SetWindowLongW(hwnd, gwl_exstyle, style)
        except Exception:
            return
