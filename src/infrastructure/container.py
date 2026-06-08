from __future__ import annotations

from collections.abc import Callable

from src.application.config_service import ConfigService
from src.application.game_launch_orchestrator import GameLaunchOrchestrator
from src.application.game_readiness_service import GameReadinessService
from src.application.game_session_service import GameSessionService
from src.application.live_chat_service import LiveChatService
from src.automation.translation_worker import TranslationWorker
from src.capture.capture_service import CaptureService
from src.chat.chat_monitor_service import ChatMonitorService
from src.export.export_service import ExportService
from src.game_detection.game_detection_service import GameDetectionService
from src.infrastructure.application_container import ApplicationContainer
from src.infrastructure.config_manager import AppConfig
from src.translation.conversation_context import ConversationContext
from src.translation.translation_pipeline import TranslationPipeline
from src.ui.controllers.gameplay_controller import GameplayController
from src.voice.speech_service import SpeechInputService, SpeechOutputService

_CONTAINER: Container | None = None


class Container:
    """Facade applicative : wiring DI + callbacks voix/UI + compatibilite existante."""

    def __init__(self) -> None:
        global _CONTAINER

        self._di = ApplicationContainer()
        self._di.init_resources()

        self._translation_listener: Callable | None = None
        self._voice_listener: Callable | None = None

        self.speech_input = SpeechInputService(on_text=self._on_voice_text)
        self._di.live_chat_service().attach_worker(self._di.translation_worker())
        self.gameplay_controller = GameplayController(
            self.live_chat,
            self.pipeline,
            self.game_detection,
            self.config_service,
            self.speech_input,
            self.game_session,
        )

        self._configure_speech_input()
        _CONTAINER = self

    @property
    def di(self) -> ApplicationContainer:
        return self._di

    @property
    def config_service(self) -> ConfigService:
        return self._di.config_service()

    @property
    def config(self) -> AppConfig:
        return self.config_service.config

    @property
    def conversation(self) -> ConversationContext:
        return self._di.conversation_context()

    @property
    def game_readiness(self) -> GameReadinessService:
        return self._di.game_readiness()

    @property
    def capture(self) -> CaptureService:
        return self._di.capture_service()

    @property
    def pipeline(self) -> TranslationPipeline:
        return self._di.translation_pipeline()

    @property
    def cache(self):
        return self.pipeline.cache

    @property
    def game_detection(self) -> GameDetectionService:
        return self._di.game_detection_service()

    @property
    def chat_monitor(self) -> ChatMonitorService:
        return self._di.chat_monitor_service()

    @property
    def analytics(self):
        return self._di.analytics_service()

    @property
    def export(self) -> ExportService:
        return self._di.export_service()

    @property
    def speech_output(self) -> SpeechOutputService:
        return self._di.speech_output_service()

    @property
    def live_chat(self) -> LiveChatService:
        return self._di.live_chat_service()

    @property
    def worker(self) -> TranslationWorker:
        return self._di.translation_worker()

    @worker.setter
    def worker(self, value: TranslationWorker) -> None:
        self.live_chat.attach_worker(value)

    @property
    def game_session(self) -> GameSessionService:
        return self._di.game_session_service()

    @property
    def game_launch(self) -> GameLaunchOrchestrator:
        return self._di.game_launch_orchestrator()

    def apply_config(self, config: AppConfig) -> None:
        self.config_service.replace(config)
        self.pipeline.reload(config)
        self._configure_speech_input()

    def set_translation_listener(self, callback: Callable | None) -> None:
        self._translation_listener = callback
        self.live_chat.set_translation_listener(callback)

    def set_status_listener(self, callback: Callable | None) -> None:
        self.live_chat.set_status_listener(callback)

    def set_voice_listener(self, callback: Callable | None) -> None:
        self._voice_listener = callback

    def shutdown(self) -> None:
        self.speech_input.stop()
        self.worker.stop()
        self._di.shutdown_resources()

    def _configure_speech_input(self) -> None:
        config = self.config_service.config
        if config.voice_language and config.voice_language != "auto":
            self.speech_input._language = config.voice_language
            return

        speech_map = {
            "fr": "fr-FR",
            "en": "en-US",
            "de": "de-DE",
            "es": "es-ES",
            "it": "it-IT",
        }
        self.speech_input._language = speech_map.get(config.language, "fr-FR")

    def _on_voice_text(self, text: str) -> None:
        if text.startswith("__ERROR__:"):
            if self._voice_listener:
                self._voice_listener(text)
            return

        result = self.pipeline.process_text(text, origin="voice")
        if self._voice_listener:
            self._voice_listener(result)

        if self.config.speak_translation and result.display_text:
            self.speech_output.speak(result.display_text)


def get_container() -> Container | None:
    return _CONTAINER
