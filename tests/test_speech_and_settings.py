from __future__ import annotations

import os
import time
import unittest
from unittest.mock import MagicMock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from src.infrastructure.config_manager import AppConfig
from src.voice.speech_service import SpeechOutputService


class SpeechOutputServiceTests(unittest.TestCase):

    def test_speak_returns_without_blocking_on_engine(self) -> None:
        started = time.perf_counter()
        fake_engine = MagicMock()
        fake_engine.runAndWait.side_effect = lambda: time.sleep(0.4)
        fake_module = MagicMock()
        fake_module.init.return_value = fake_engine

        service = SpeechOutputService()
        with patch.dict("sys.modules", {"pyttsx3": fake_module}):
            service.speak("hello sanctuary")
            elapsed = time.perf_counter() - started
            if service._thread is not None:
                service._thread.join(timeout=2.0)

        self.assertLess(elapsed, 0.2)
        fake_engine.say.assert_called_once_with("hello sanctuary")
        fake_engine.runAndWait.assert_called_once()

    def test_speak_ignores_blank_text(self) -> None:
        service = SpeechOutputService()
        service.speak("   ")
        self.assertIsNone(service._thread)


class SettingsFormPreserveTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        from PyQt6.QtWidgets import QApplication

        cls.app = QApplication.instance() or QApplication([])

    def test_build_config_preserves_hidden_fields(self) -> None:
        from src.ui.widgets.settings_form_widget import SettingsFormWidget

        source = AppConfig(
            translator="deepl",
            deepl_api_key="secret-key",
            overlay_window_x=120,
            overlay_window_y=80,
            overlay_window_width=440,
            overlay_window_height=300,
            speak_translation=True,
            hub_sounds_enabled=False,
            chat_monitor_enabled=False,
        )
        form = SettingsFormWidget(source)
        built = form.build_config()

        self.assertEqual(built.translator, "deepl")
        self.assertEqual(built.deepl_api_key, "secret-key")
        self.assertEqual(built.overlay_window_x, 120)
        self.assertEqual(built.overlay_window_y, 80)
        self.assertEqual(built.overlay_window_width, 440)
        self.assertEqual(built.overlay_window_height, 300)
        self.assertTrue(built.speak_translation)
        self.assertFalse(built.hub_sounds_enabled)
        self.assertFalse(built.chat_monitor_enabled)


if __name__ == "__main__":
    unittest.main()
