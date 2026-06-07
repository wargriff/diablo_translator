from __future__ import annotations

import threading
import time
from collections.abc import Callable

from src.domain.models.translation_result import TranslationResult


class TranslationWorker:

    def __init__(
        self,
        container,
        on_translation: Callable[[TranslationResult], None] | None = None,
    ) -> None:
        self._container = container
        self._on_translation = on_translation
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> None:
        if self.is_running:
            return

        self._container.chat_monitor.reset()
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    def _run(self) -> None:
        fps = max(self._container.config.capture_fps, 1)
        delay = 1.0 / fps

        while not self._stop_event.is_set():
            if not self._container.game_detection.is_running():
                time.sleep(1.0)
                continue

            if self._container.config.chat_monitor_enabled:
                self._run_chat_monitor()
            else:
                self._run_full_screen()

            time.sleep(delay)

    def _run_chat_monitor(self) -> None:
        capture = self._container.chat_monitor.capture_chat(
            self._container.capture,
            self._container.game_detection,
            self._container.config.chat_region_preset,
            self._container.pipeline.ocr,
        )

        for line in capture.new_lines:
            result = self._container.pipeline.process_text(line, origin="chat")
            self._emit_result(result)

    def _run_full_screen(self) -> None:
        image = self._container.capture.capture_monitor()
        result = self._container.pipeline.process_image(image)

        if result.translated_text:
            self._emit_result(result)

    def _emit_result(self, result: TranslationResult) -> None:
        if not self._on_translation or not result.translated_text:
            return

        if result.skipped and not result.preserved_mixed:
            return

        self._on_translation(result)

        if self._container.config.speak_translation:
            self._container.speech_output.speak(result.display_text)
