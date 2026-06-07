from src.analytics.analytics_service import AnalyticsService
from src.automation.translation_worker import TranslationWorker
from src.capture.capture_service import CaptureService
from src.export.export_service import ExportService
from src.game_detection.game_detection_service import GameDetectionService
from src.infrastructure.config_manager import ConfigManager
from src.infrastructure.database import Database
from src.translation.translation_pipeline import TranslationPipeline


class Container:

    def __init__(self) -> None:
        Database.initialize()

        self.config = ConfigManager.load()
        self.capture = CaptureService()
        self.pipeline = TranslationPipeline()
        self.game_detection = GameDetectionService()
        self.analytics = AnalyticsService()
        self.export = ExportService()
        self.worker = TranslationWorker(
            self,
            on_translation=self._on_translation,
        )
        self._translation_listener = None

    def set_translation_listener(self, callback) -> None:
        self._translation_listener = callback

    def _on_translation(self, text: str) -> None:
        if self._translation_listener:
            self._translation_listener(text)
