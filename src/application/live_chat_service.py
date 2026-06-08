from __future__ import annotations

from dataclasses import dataclass

from src.application.game_readiness_service import GameReadinessService
from src.application.config_service import ConfigService
from src.application.game_session_service import GameSessionService
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
    wait_hint: str = ""
    ocr_loading: bool = False


class LiveChatService:

    def __init__(
        self,
        chat_monitor: ChatMonitorService,
        capture: CaptureService,
        game_detection: GameDetectionService,
        pipeline: TranslationPipeline,
        config_service: ConfigService,
        game_session: GameSessionService | None = None,
        player_identity: PlayerIdentityService | None = None,
        chat_router: InGameChatRouter | None = None,
        game_readiness: GameReadinessService | None = None,
    ) -> None:
        self._chat_monitor = chat_monitor
        self._capture = capture
        self._game_detection = game_detection
        self._pipeline = pipeline
        self._config_service = config_service
        self._game_session = game_session
        self._player_identity = player_identity or PlayerIdentityService()
        self._chat_router = chat_router or InGameChatRouter(pipeline, self._player_identity)
        self._readiness = game_readiness or GameReadinessService()
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

    def _session_snapshot(self):
        if self._game_session is not None:
            return self._game_session.snapshot()
        from src.domain.models.game_session import GameSessionSnapshot
        import time

        from src.capture.game_window_service import GameWindowService

        status = self._game_detection.scan()
        window = None
        if status.is_any_running:
            window = GameWindowService.find_primary_game_info(
                self._game_detection,
                status=status,
            )
        return GameSessionSnapshot(status=status, window=window, scanned_at=time.time())

    def is_game_running(self) -> bool:
        return self._session_snapshot().status.is_any_running

    def set_translation_listener(self, callback) -> None:
        self._translation_listener = callback
        if self.worker is not None:
            self.worker.set_translation_listener(self._emit_translation)

    def reset(self) -> None:
        self._chat_monitor.reset()
        self._player_identity.reset()
        self._readiness.reset()
        if self._game_session is not None:
            self._game_session.invalidate()

    def is_game_ready_for_ocr(self) -> bool:
        config = self._config_service.config
        return self._readiness.is_ready_snapshot(
            self._session_snapshot(),
            grace_seconds=config.game_startup_grace_seconds,
        )

    def game_readiness_hint(self) -> str:
        config = self._config_service.config
        return self._readiness.evaluate_snapshot(
            self._session_snapshot(),
            grace_seconds=config.game_startup_grace_seconds,
        )

    def emit_wait_status(self) -> None:
        hint = self.game_readiness_hint()
        if not hint:
            return
        self._last_status = LiveChatStatus(
            capture_source=self._last_status.capture_source,
            display_mode=self._last_status.display_mode,
            monitor_index=self._last_status.monitor_index,
            preset_key=self._last_status.preset_key,
            wait_hint=hint,
            ocr_loading=self._last_status.ocr_loading,
        )
        self._emit_status()

    def emit_ocr_loading(self, loading: bool) -> None:
        self._last_status = LiveChatStatus(
            capture_source=self._last_status.capture_source,
            display_mode=self._last_status.display_mode,
            monitor_index=self._last_status.monitor_index,
            preset_key=self._last_status.preset_key,
            ocr_line_count=self._last_status.ocr_line_count,
            new_message_count=self._last_status.new_message_count,
            last_error=self._last_status.last_error,
            wait_hint=self._last_status.wait_hint,
            ocr_loading=loading,
        )
        self._emit_status()

    def emit_ocr_error(self, message: str) -> None:
        self._last_status = LiveChatStatus(
            capture_source=self._last_status.capture_source,
            display_mode=self._last_status.display_mode,
            monitor_index=self._last_status.monitor_index,
            preset_key=self._last_status.preset_key,
            last_error=message,
            ocr_loading=False,
        )
        self._emit_status()

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
            last_error="",
        )
        self._emit_status()

        results: list[TranslationResult] = []
        for message in capture.new_messages:
            try:
                result = self._chat_router.process_message(message, config)
            except Exception as exc:
                self._last_status = LiveChatStatus(
                    capture_source=capture.capture_source,
                    display_mode=capture.display_mode,
                    monitor_index=capture.monitor_index,
                    preset_key=capture.preset_key,
                    ocr_line_count=len(capture.raw_text.splitlines()) if capture.raw_text else 0,
                    new_message_count=0,
                    last_error=f"Traduction : {exc}",
                )
                self._emit_status()
                continue

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
