from src.infrastructure.database import Database
from src.infrastructure.config_manager import ConfigManager

from src.capture.capture_service import CaptureService
from src.services.translation_pipeline import (
    TranslationPipeline
)
from src.game_detection.game_detection_service import (
    GameDetectionService
)


class Container:

    def __init__(self):

        Database.initialize()

        self.config = (
            ConfigManager.load()
        )

        self.capture = (
            CaptureService()
        )

        self.pipeline = (
            TranslationPipeline()
        )

        self.game_detection = (
            GameDetectionService()
        )