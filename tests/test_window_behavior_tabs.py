from __future__ import annotations

import unittest
from unittest.mock import MagicMock

from src.ui.services.window_behavior import WindowBehaviorService


class WindowBehaviorTabTests(unittest.TestCase):

    def test_identifies_ocr_tab_by_object_name(self) -> None:
        widget = MagicMock()
        widget.objectName.return_value = "GameplayRoot"
        tabs = MagicMock()
        tabs.widget.return_value = widget
        tabs.tabText.return_value = ""
        self.assertTrue(WindowBehaviorService._is_gameplay_tab(tabs, 0))

    def test_identifies_ocr_tab_by_label(self) -> None:
        widget = MagicMock()
        widget.objectName.return_value = "LaunchTabRoot"
        tabs = MagicMock()
        tabs.widget.return_value = widget
        tabs.tabText.return_value = "OCR"
        self.assertTrue(WindowBehaviorService._is_gameplay_tab(tabs, 0))

    def test_rejects_launcher_tab(self) -> None:
        widget = MagicMock()
        widget.objectName.return_value = "LaunchTabRoot"
        tabs = MagicMock()
        tabs.widget.return_value = widget
        tabs.tabText.return_value = "Launcher"
        self.assertFalse(WindowBehaviorService._is_gameplay_tab(tabs, 1))


if __name__ == "__main__":
    unittest.main()
