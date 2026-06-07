from __future__ import annotations

import threading
import time
from collections.abc import Callable


class TranslationWorker:

    def __init__(
        self,
        container,
        on_translation: Callable[[str], None] | None = None,
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

            image = self._container.capture.capture_monitor()
            translated = self._container.pipeline.process_image(image)

            if translated and self._on_translation:
                self._on_translation(translated)

            time.sleep(delay)
