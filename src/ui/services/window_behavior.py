from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget

from src.application.overlay_preset import apply_game_overlay_preset
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
        return

    @classmethod
    def apply(cls, window: QMainWindow, config: AppConfig) -> None:
        focused = QApplication.focusWidget()
        cls._apply_flags(window, config)
        cls._apply_opacity(window, config)
        cls._apply_geometry(window, config)
        cls._apply_tabs(window, config)
        cls._apply_click_through(window, config)
        cls._apply_focus_policy(window, config)
        window.show()

        if focused is not None and focused.isEnabled():
            focused.setFocus(Qt.FocusReason.OtherFocusReason)

    @staticmethod
    def _apply_focus_policy(window: QMainWindow, config: AppConfig) -> None:
        use_borderless = config.overlay_compact and config.overlay_borderless
        if config.overlay_compact and not use_borderless:
            window.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)
        elif config.overlay_compact:
            window.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        else:
            window.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)

    @staticmethod
    def _apply_flags(window: QMainWindow, config: AppConfig) -> None:
        flags = Qt.WindowType.Window
        flags |= Qt.WindowType.WindowMinimizeButtonHint
        flags |= Qt.WindowType.WindowMaximizeButtonHint
        flags |= Qt.WindowType.WindowCloseButtonHint

        use_top = config.always_on_top or config.overlay_compact
        if use_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint

        use_borderless = config.overlay_compact and config.overlay_borderless
        if use_borderless:
            flags |= Qt.WindowType.FramelessWindowHint
        else:
            flags &= ~Qt.WindowType.FramelessWindowHint

        flags &= ~Qt.WindowType.Tool
        window.setWindowFlags(flags)

    @staticmethod
    def _apply_opacity(window: QMainWindow, config: AppConfig) -> None:
        if config.overlay_enabled or config.overlay_compact:
            window.setWindowOpacity(max(0.55, min(config.overlay_opacity, 1.0)))
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
            if config.overlay_window_width > 0:
                width = config.overlay_window_width
            if config.overlay_window_height > 0:
                height = config.overlay_window_height

            if (
                config.overlay_remember_position
                and config.overlay_window_x >= 0
                and config.overlay_window_y >= 0
            ):
                window.setGeometry(
                    config.overlay_window_x,
                    config.overlay_window_y,
                    width,
                    height,
                )
            elif window.isVisible() and config.overlay_remember_position:
                return
            elif config.overlay_above_chat and config.overlay_position == "bottom_left":
                chat_top = area.top() + int(area.height() * 0.66)
                x = area.left() + margin
                y = max(area.top() + margin, chat_top - height - 6)
                window.setGeometry(x, y, width, height)
            else:
                position_fn = cls.POSITIONS.get(
                    config.overlay_position,
                    cls.POSITIONS["bottom_left"],
                )
                x, y = position_fn(area, width, height, margin)
                window.setGeometry(x, y, width, height)

            if config.overlay_borderless:
                window.setMinimumSize(280, 180)
                window.setMaximumSize(700, 420)
            else:
                window.setMinimumSize(320, 200)
                window.setMaximumSize(16777215, 16777215)
            return

        window.setMinimumSize(960, 640)
        window.setMaximumSize(16777215, 16777215)
        if window.width() < 960:
            window.resize(1480, 940)

    @staticmethod
    def save_geometry(window: QMainWindow, config: AppConfig) -> AppConfig:
        if not config.overlay_compact or not config.overlay_remember_position:
            return config

        geo = window.geometry()
        config.overlay_window_x = geo.x()
        config.overlay_window_y = geo.y()
        config.overlay_window_width = geo.width()
        config.overlay_window_height = geo.height()
        return config

    @staticmethod
    def _apply_tabs(window: QMainWindow, config: AppConfig) -> None:
        tabs = window.findChild(QTabWidget)
        if tabs is None:
            return

        tabs.tabBar().setVisible(not config.overlay_compact)

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

    @classmethod
    def apply_game_overlay_preset(cls, config: AppConfig) -> AppConfig:
        return apply_game_overlay_preset(config)

    @staticmethod
    def uses_custom_title_bar(config: AppConfig) -> bool:
        return config.overlay_compact and config.overlay_borderless
