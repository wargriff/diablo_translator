from __future__ import annotations

import threading
import time
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from src.application.config_service import ConfigService
from src.domain.models.translation_result import TranslationResult
from src.voice.speech_service import SpeechOutputService

if TYPE_CHECKING:
    from src.application.live_chat_service import LiveChatService


class TranslationWorker:

    def __init__(
        self,
        live_chat: LiveChatService | Any,
        config_service: ConfigService,
        speech_output: SpeechOutputService | None = None,
        on_translation: Callable[[TranslationResult], None] | None = None,
    ) -> None:
        self._live_chat = live_chat
        self._config_service = config_service
        self._speech_output = speech_output
        self._on_translation = on_translation
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def set_translation_listener(
        self,
        callback: Callable[[TranslationResult], None] | None,
    ) -> None:
        self._on_translation = callback

    def attach_speech_output(self, speech_output: SpeechOutputService) -> None:
        self._speech_output = speech_output

    def start(self) -> None:
        if self.is_running:
            return

        self._live_chat.reset()
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
            name="LiveChatWorker",
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    def _run(self) -> None:
        try:
            self._live_chat.prewarm_ocr()
        except Exception:
            pass

        while not self._stop_event.is_set():
            config = self._config_service.config
            fps = max(config.capture_fps, 1)
            if config.low_cpu_mode:
                fps = min(fps, 1)
            delay = 1.0 / fps

            if not self._live_chat.is_game_running():
                time.sleep(1.0)
                continue

            if not self._live_chat.is_game_ready_for_ocr():
                self._live_chat.emit_wait_status()
                time.sleep(1.0)
                continue

            for result in self._live_chat.poll_chat():
                self._emit_result(result)

            time.sleep(delay)

    def _emit_result(self, result: TranslationResult) -> None:
        if not self._on_translation or not result.translated_text:
            return

        if result.skipped and not result.preserved_mixed:
            return

        self._on_translation(result)

        config = self._config_service.config
        if config.speak_translation and self._speech_output is not None:
            self._speech_output.speak(result.display_text)
