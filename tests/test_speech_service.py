from __future__ import annotations

import threading
import unittest
from unittest.mock import MagicMock, patch

from src.voice.speech_service import SpeechInputService, SpeechOutputService


class SpeechInputServiceTests(unittest.TestCase):

    def test_stop_requests_sounddevice_abort(self) -> None:
        service = SpeechInputService()
        fake_thread = MagicMock()
        fake_thread.is_alive.return_value = True
        service._thread = fake_thread

        with patch.dict("sys.modules", {"sounddevice": MagicMock()}):
            import sounddevice as sd

            service.stop()
            sd.stop.assert_called_once()

        fake_thread.join.assert_called_once()
        self.assertIsNone(service._thread)


class SpeechOutputServiceTests(unittest.TestCase):

    def test_speak_returns_immediately_without_blocking(self) -> None:
        started = threading.Event()
        released = threading.Event()

        def fake_init():
            started.set()
            released.wait(timeout=1.0)
            return MagicMock()

        service = SpeechOutputService()
        with patch.dict("sys.modules", {"pyttsx3": MagicMock()}):
            import pyttsx3

            pyttsx3.init.side_effect = fake_init
            service.speak("bonjour")
            self.assertTrue(started.wait(timeout=1.0))
            released.set()


if __name__ == "__main__":
    unittest.main()
