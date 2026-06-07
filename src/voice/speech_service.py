from __future__ import annotations

import threading
from collections.abc import Callable

from src.domain.models.translation_result import TranslationResult


class SpeechInputService:

    def __init__(
        self,
        on_text: Callable[[str], None] | None = None,
        language: str = "fr-FR",
    ) -> None:
        self._on_text = on_text
        self._language = language
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    @property
    def is_listening(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    @classmethod
    def check_availability(cls) -> tuple[bool, str]:
        try:
            import speech_recognition  # noqa: F401
        except ModuleNotFoundError:
            return (
                False,
                "SpeechRecognition manquant — lancez : pip install SpeechRecognition pyaudio",
            )

        try:
            import pyaudio  # noqa: F401
        except ModuleNotFoundError:
            return (
                False,
                "PyAudio manquant — lancez : pip install pyaudio",
            )

        return True, ""

    def start(self) -> bool:
        if self.is_listening:
            return True

        available, error = self.check_availability()
        if not available:
            if self._on_text:
                self._on_text(f"__ERROR__:{error}")
            return False

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        return True

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.5)
        self._thread = None

    def _listen_loop(self) -> None:
        import speech_recognition as sr

        recognizer = sr.Recognizer()
        try:
            microphone = sr.Microphone()
        except Exception as exc:
            if self._on_text:
                self._on_text(f"__ERROR__:Microphone indisponible ({exc})")
            return

        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.6)

        while not self._stop_event.is_set():
            try:
                with microphone as source:
                    audio = recognizer.listen(source, timeout=4, phrase_time_limit=8)

                text = recognizer.recognize_google(audio, language=self._language)
                if text.strip() and self._on_text:
                    self._on_text(text.strip())
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except Exception as exc:
                if self._on_text:
                    self._on_text(f"__ERROR__:Erreur micro ({exc})")
                break


class SpeechOutputService:

    def speak(self, text: str) -> None:
        cleaned = text.strip()
        if not cleaned:
            return

        try:
            import pyttsx3
        except ModuleNotFoundError:
            return

        engine = pyttsx3.init()
        engine.say(cleaned)
        engine.runAndWait()
