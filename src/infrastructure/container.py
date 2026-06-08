from src.analytics.analytics_service import AnalyticsService
from src.application.game_readiness_service import GameReadinessService
from src.application.config_service import ConfigService
from src.application.game_session_service import GameSessionService
from src.application.live_chat_service import LiveChatService
from src.automation.translation_worker import TranslationWorker
from src.capture.capture_service import CaptureService
from src.chat.chat_monitor_service import ChatMonitorService
from src.export.export_service import ExportService
from src.game_detection.game_detection_service import GameDetectionService
from src.infrastructure.config_manager import AppConfig, ConfigManager
from src.infrastructure.database import Database
from src.translation.conversation_context import ConversationContext
from src.translation.translation_pipeline import TranslationPipeline
from src.ui.controllers.gameplay_controller import GameplayController
from src.voice.speech_service import SpeechInputService, SpeechOutputService

_CONTAINER: "Container | None" = None


class Container:

    def __init__(self) -> None:
        global _CONTAINER
        Database.initialize()

        self.config_service = ConfigService()
        self.conversation = ConversationContext()
        self.game_readiness = GameReadinessService()
        self.capture = CaptureService()
        self.pipeline = TranslationPipeline(self.config_service.config, self.conversation)
        self.cache = self.pipeline.cache
        self.game_detection = GameDetectionService()
        self.chat_monitor = ChatMonitorService()
        self.analytics = AnalyticsService()
        self.export = ExportService()
        self.speech_output = SpeechOutputService()
        self.speech_input = SpeechInputService(on_text=self._on_voice_text)

        self.live_chat = LiveChatService(
            self.chat_monitor,
            self.capture,
            self.game_detection,
            self.pipeline,
            self.config_service,
            game_readiness=self.game_readiness,
        )
        self.worker = TranslationWorker(
            self.live_chat,
            self.config_service,
            speech_output=self.speech_output,
        )
        self.live_chat.attach_worker(self.worker)

        self.game_session = GameSessionService(self.game_detection, self.config_service)
        self.gameplay_controller = GameplayController(
            self.live_chat,
            self.pipeline,
            self.game_detection,
            self.config_service,
            self.speech_input,
        )

        self._translation_listener = None
        self._voice_listener = None
        self._configure_speech_input()
        _CONTAINER = self

    @property
    def config(self) -> AppConfig:
        return self.config_service.config

    @property
    def worker(self) -> TranslationWorker:
        return self.live_chat.worker

    @worker.setter
    def worker(self, value: TranslationWorker) -> None:
        self.live_chat.attach_worker(value)

    def apply_config(self, config: AppConfig) -> None:
        self.config_service.replace(config)
        self.pipeline.reload(config)
        self.cache = self.pipeline.cache
        self._configure_speech_input()

    def set_translation_listener(self, callback) -> None:
        self._translation_listener = callback
        self.live_chat.set_translation_listener(callback)

    def set_status_listener(self, callback) -> None:
        self.live_chat.set_status_listener(callback)

    def set_voice_listener(self, callback) -> None:
        self._voice_listener = callback

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
        self.speech_input._language = speech_map.get(
            config.language,
            "fr-FR",
        )

    def _on_translation(self, result) -> None:
        if self._translation_listener:
            self._translation_listener(result)

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


def get_container() -> "Container | None":
    return _CONTAINER
