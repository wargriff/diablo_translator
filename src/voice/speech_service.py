from __future__ import annotations

import threading
from collections.abc import Callable

from src.domain.models.translation_result import TranslationResult
from src.infrastructure.agent_debug_log import agent_log


class SpeechInputService:

    SAMPLE_RATE = 16_000
    CHANNELS = 1
    SAMPLE_WIDTH = 2

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
                "SpeechRecognition manquant — pip install SpeechRecognition sounddevice",
            )

        try:
            import sounddevice  # noqa: F401
        except ModuleNotFoundError:
            return (
                False,
                "SoundDevice manquant — pip install sounddevice (remplace PyAudio sur Python 3.14)",
            )

        return True, ""

    def start(self) -> bool:
        if self.is_listening:
            return True

        # #region agent log
        agent_log(
            "speech_service.py:start",
            "Demarrage micro",
            hypothesis_id="C",
            data={"language": self._language},
        )
        # #endregion

        available, error = self.check_availability()
        if not available:
            # #region agent log
            agent_log(
                "speech_service.py:start",
                "Micro indisponible",
                hypothesis_id="C",
                data={"error": error},
            )
            # #endregion
            if self._on_text:
                self._on_text(f"__ERROR__:{error}")
            return False

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._listen_loop,
            daemon=True,
            name="SpeechInput",
        )
        self._thread.start()
        # #region agent log
        agent_log(
            "speech_service.py:start",
            "Thread micro demarre",
            hypothesis_id="B",
            data={"alive": self._thread.is_alive()},
        )
        # #endregion
        return True

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.5)
        self._thread = None

    def _listen_loop(self) -> None:
        import sounddevice as sd
        import speech_recognition as sr

        # #region agent log
        agent_log(
            "speech_service.py:_listen_loop",
            "Boucle micro entree",
            hypothesis_id="B",
            data={"threadId": threading.get_ident()},
        )
        # #endregion

        recognizer = sr.Recognizer()
        recognizer.dynamic_energy_threshold = True

        while not self._stop_event.is_set():
            try:
                # #region agent log
                agent_log(
                    "speech_service.py:_listen_loop",
                    "Avant sd.rec",
                    hypothesis_id="B",
                )
                # #endregion
                recording = sd.rec(
                    int(4 * self.SAMPLE_RATE),
                    samplerate=self.SAMPLE_RATE,
                    channels=self.CHANNELS,
                    dtype="int16",
                )
                sd.wait()
                # #region agent log
                agent_log(
                    "speech_service.py:_listen_loop",
                    "Apres sd.rec",
                    hypothesis_id="B",
                    data={"samples": int(recording.shape[0]) if hasattr(recording, "shape") else 0},
                )
                # #endregion

                if self._stop_event.is_set():
                    break

                audio_data = sr.AudioData(
                    recording.tobytes(),
                    self.SAMPLE_RATE,
                    self.SAMPLE_WIDTH,
                )
                text = recognizer.recognize_google(audio_data, language=self._language)
                if text.strip() and self._on_text:
                    self._on_text(text.strip())
            except sr.UnknownValueError:
                continue
            except sr.RequestError as exc:
                if self._on_text:
                    self._on_text(f"__ERROR__:Service vocal indisponible ({exc})")
                break
            except Exception as exc:
                # #region agent log
                agent_log(
                    "speech_service.py:_listen_loop",
                    "Erreur micro",
                    hypothesis_id="B",
                    data={"error": str(exc), "type": type(exc).__name__},
                )
                # #endregion
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
