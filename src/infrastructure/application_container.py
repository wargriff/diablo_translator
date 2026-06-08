from __future__ import annotations

from src.analytics.analytics_service import AnalyticsService
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
from src.infrastructure.database import Database
from src.translation.conversation_context import ConversationContext
from src.translation.translation_pipeline import TranslationPipeline
from src.voice.speech_service import SpeechOutputService


class ApplicationContainer:
    """Graphe de services — wiring manuel compatible PyInstaller (sans dependency-injector)."""

    def __init__(self) -> None:
        self._config_service: ConfigService | None = None
        self._conversation_context: ConversationContext | None = None
        self._game_readiness: GameReadinessService | None = None
        self._capture_service: CaptureService | None = None
        self._game_detection_service: GameDetectionService | None = None
        self._chat_monitor_service: ChatMonitorService | None = None
        self._analytics_service: AnalyticsService | None = None
        self._export_service: ExportService | None = None
        self._speech_output_service: SpeechOutputService | None = None
        self._translation_pipeline: TranslationPipeline | None = None
        self._game_session_service: GameSessionService | None = None
        self._live_chat_service: LiveChatService | None = None
        self._translation_worker: TranslationWorker | None = None
        self._game_launch_orchestrator: GameLaunchOrchestrator | None = None

    def init_resources(self) -> None:
        Database.initialize()

    def config_service(self) -> ConfigService:
        if self._config_service is None:
            self._config_service = ConfigService()
        return self._config_service

    def conversation_context(self) -> ConversationContext:
        if self._conversation_context is None:
            self._conversation_context = ConversationContext()
        return self._conversation_context

    def game_readiness(self) -> GameReadinessService:
        if self._game_readiness is None:
            self._game_readiness = GameReadinessService()
        return self._game_readiness

    def capture_service(self) -> CaptureService:
        if self._capture_service is None:
            self._capture_service = CaptureService()
        return self._capture_service

    def game_detection_service(self) -> GameDetectionService:
        if self._game_detection_service is None:
            self._game_detection_service = GameDetectionService()
        return self._game_detection_service

    def chat_monitor_service(self) -> ChatMonitorService:
        if self._chat_monitor_service is None:
            self._chat_monitor_service = ChatMonitorService()
        return self._chat_monitor_service

    def analytics_service(self) -> AnalyticsService:
        if self._analytics_service is None:
            self._analytics_service = AnalyticsService()
        return self._analytics_service

    def export_service(self) -> ExportService:
        if self._export_service is None:
            self._export_service = ExportService()
        return self._export_service

    def speech_output_service(self) -> SpeechOutputService:
        if self._speech_output_service is None:
            self._speech_output_service = SpeechOutputService()
        return self._speech_output_service

    def translation_pipeline(self) -> TranslationPipeline:
        if self._translation_pipeline is None:
            self._translation_pipeline = TranslationPipeline(
                config=self.config_service().config,
                conversation=self.conversation_context(),
            )
        return self._translation_pipeline

    def game_session_service(self) -> GameSessionService:
        if self._game_session_service is None:
            self._game_session_service = GameSessionService(
                game_detection=self.game_detection_service(),
                config_service=self.config_service(),
            )
        return self._game_session_service

    def live_chat_service(self) -> LiveChatService:
        if self._live_chat_service is None:
            self._live_chat_service = LiveChatService(
                chat_monitor=self.chat_monitor_service(),
                capture=self.capture_service(),
                game_detection=self.game_detection_service(),
                pipeline=self.translation_pipeline(),
                config_service=self.config_service(),
                game_session=self.game_session_service(),
                game_readiness=self.game_readiness(),
            )
        return self._live_chat_service

    def translation_worker(self) -> TranslationWorker:
        if self._translation_worker is None:
            self._translation_worker = TranslationWorker(
                live_chat=self.live_chat_service(),
                config_service=self.config_service(),
                speech_output=self.speech_output_service(),
            )
        return self._translation_worker

    def game_launch_orchestrator(self) -> GameLaunchOrchestrator:
        if self._game_launch_orchestrator is None:
            self._game_launch_orchestrator = GameLaunchOrchestrator(
                game_session=self.game_session_service(),
                game_readiness=self.game_readiness(),
                config_service=self.config_service(),
            )
        return self._game_launch_orchestrator

    def shutdown_resources(self) -> None:
        if self._capture_service is not None:
            self._capture_service.close()
