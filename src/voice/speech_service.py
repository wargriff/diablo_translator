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

    def start(self) -> None:
        if self.is_listening:
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    def _listen_loop(self) -> None:
        try:
            import speech_recognition as sr
        except ModuleNotFoundError:
            if self._on_text:
                self._on_text("__ERROR__:speech_recognition non installé")
            return

        recognizer = sr.Recognizer()
        microphone = sr.Microphone()

        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.6)

        while not self._stop_event.is_set():
            try:
                with microphone as source:
                    audio = recognizer.listen(source, timeout=4, phrase_time_limit=8)

                text = recognizer.recognize_google(audio, language=self._language)
                if text.strip() and self._on_text:
                    self._on_text(text.strip())
            except Exception:
                continue


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
