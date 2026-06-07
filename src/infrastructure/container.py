from src.analytics.analytics_service import AnalyticsService
from src.automation.translation_worker import TranslationWorker
from src.capture.capture_service import CaptureService
from src.chat.chat_monitor_service import ChatMonitorService
from src.export.export_service import ExportService
from src.game_detection.game_detection_service import GameDetectionService
from src.infrastructure.config_manager import AppConfig, ConfigManager
from src.infrastructure.database import Database
from src.translation.translation_pipeline import TranslationPipeline
from src.voice.speech_service import SpeechInputService, SpeechOutputService


class Container:

    def __init__(self) -> None:
        Database.initialize()

        self.config = ConfigManager.load()
        self.capture = CaptureService()
        self.pipeline = TranslationPipeline(self.config)
        self.game_detection = GameDetectionService()
        self.chat_monitor = ChatMonitorService()
        self.analytics = AnalyticsService()
        self.export = ExportService()
        self.speech_output = SpeechOutputService()
        self.speech_input = SpeechInputService(on_text=self._on_voice_text)
        self.worker = TranslationWorker(
            self,
            on_translation=self._on_translation,
        )
        self._translation_listener = None
        self._voice_listener = None
        self._configure_speech_input()

    def apply_config(self, config: AppConfig) -> None:
        self.config = config
        self.pipeline.reload(config)
        self._configure_speech_input()

    def set_translation_listener(self, callback) -> None:
        self._translation_listener = callback

    def set_voice_listener(self, callback) -> None:
        self._voice_listener = callback

    def _configure_speech_input(self) -> None:
        speech_map = {
            "fr": "fr-FR",
            "en": "en-US",
            "de": "de-DE",
            "es": "es-ES",
            "it": "it-IT",
        }
        self.speech_input._language = speech_map.get(
            self.config.language,
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

        result = self.pipeline.process_text(text)
        if self._voice_listener:
            self._voice_listener(result)

        if self.config.speak_translation and result.display_text:
            self.speech_output.speak(result.display_text)
