from __future__ import annotations

from dataclasses import dataclass

from src.application.config_service import ConfigService
from src.application.in_game_chat_router import InGameChatRouter
from src.application.player_identity_service import PlayerIdentityService
from src.automation.translation_worker import TranslationWorker
from src.capture.capture_service import CaptureService
from src.chat.chat_monitor_service import ChatMonitorService
from src.domain.models.translation_result import TranslationResult
from src.game_detection.game_detection_service import GameDetectionService
from src.translation.translation_pipeline import TranslationPipeline


@dataclass(frozen=True, slots=True)
class LiveChatStatus:

    capture_source: str
    display_mode: str
    monitor_index: int
    preset_key: str
    ocr_line_count: int = 0
    new_message_count: int = 0
    last_error: str = ""


class LiveChatService:

    def __init__(
        self,
        chat_monitor: ChatMonitorService,
        capture: CaptureService,
        game_detection: GameDetectionService,
        pipeline: TranslationPipeline,
        config_service: ConfigService,
        player_identity: PlayerIdentityService | None = None,
        chat_router: InGameChatRouter | None = None,
    ) -> None:
        self._chat_monitor = chat_monitor
        self._capture = capture
        self._game_detection = game_detection
        self._pipeline = pipeline
        self._config_service = config_service
        self._player_identity = player_identity or PlayerIdentityService()
        self._chat_router = chat_router or InGameChatRouter(pipeline, self._player_identity)
        self._translation_listener = None
        self._last_status = LiveChatStatus("idle", "unknown", 1, "d3_1080p")
        self.worker: TranslationWorker | None = None
        self._status_listener = None

    def set_status_listener(self, callback) -> None:
        self._status_listener = callback

    @property
    def last_status(self) -> LiveChatStatus:
        return self._last_status

    @property
    def player_identity(self) -> PlayerIdentityService:
        return self._player_identity

    def attach_worker(self, worker: TranslationWorker) -> None:
        self.worker = worker
        worker.set_translation_listener(self._emit_translation)

    def is_game_running(self) -> bool:
        return self._game_detection.is_running()

    def set_translation_listener(self, callback) -> None:
        self._translation_listener = callback
        if self.worker is not None:
            self.worker.set_translation_listener(self._emit_translation)

    def reset(self) -> None:
        self._chat_monitor.reset()
        self._player_identity.reset()

    def prewarm_ocr(self) -> None:
        self._pipeline.ocr.prewarm()

    def poll_chat(self) -> list[TranslationResult]:
        config = self._config_service.config
        if not config.chat_monitor_enabled:
            return []

        try:
            capture = self._chat_monitor.capture_chat(
                self._capture,
                self._game_detection,
                config,
                self._pipeline.ocr,
            )
        except Exception as exc:
            self._last_status = LiveChatStatus(
                capture_source=self._last_status.capture_source,
                display_mode=self._last_status.display_mode,
                monitor_index=self._last_status.monitor_index,
                preset_key=self._last_status.preset_key,
                last_error=str(exc),
            )
            self._emit_status()
            return []

        self._last_status = LiveChatStatus(
            capture_source=capture.capture_source,
            display_mode=capture.display_mode,
            monitor_index=capture.monitor_index,
            preset_key=capture.preset_key,
            ocr_line_count=len(capture.raw_text.splitlines()) if capture.raw_text else 0,
            new_message_count=len(capture.new_messages),
        )
        self._emit_status()

        results: list[TranslationResult] = []
        for message in capture.new_messages:
            result = self._chat_router.process_message(message, config)
            if result.translated_text and (not result.skipped or result.preserved_mixed):
                results.append(result)
        return results

    def translate_user_text(self, text: str) -> TranslationResult:
        return self._pipeline.process_text(text, origin="user")

    def _emit_translation(self, result: TranslationResult) -> None:
        if self._translation_listener:
            self._translation_listener(result)

    def _emit_status(self) -> None:
        if self._status_listener:
            self._status_listener(self._last_status)
