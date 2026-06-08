from __future__ import annotations

from dependency_injector import containers, providers

from src.analytics.analytics_service import AnalyticsService
from src.application.config_service import ConfigService
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


class ApplicationContainer(containers.DeclarativeContainer):
    """Graphe DI declarative — services sans callbacks UI ni cycles worker/chat."""

    wiring_config = containers.WiringConfiguration(
        packages=[
            "src.ui",
            "src.application",
            "src.bootstrap",
            "src.programs",
        ],
    )

    database = providers.Resource(
        Database.initialize,
    )

    config_service = providers.Singleton(
        ConfigService,
    )

    conversation_context = providers.Singleton(
        ConversationContext,
    )

    game_readiness = providers.Singleton(
        GameReadinessService,
    )

    capture_service = providers.Singleton(
        CaptureService,
    )

    game_detection_service = providers.Singleton(
        GameDetectionService,
    )

    chat_monitor_service = providers.Singleton(
        ChatMonitorService,
    )

    analytics_service = providers.Singleton(
        AnalyticsService,
    )

    export_service = providers.Singleton(
        ExportService,
    )

    speech_output_service = providers.Singleton(
        SpeechOutputService,
    )

    translation_pipeline = providers.Singleton(
        TranslationPipeline,
        config=config_service.provided.config,
        conversation=conversation_context,
    )

    live_chat_service = providers.Singleton(
        LiveChatService,
        chat_monitor=chat_monitor_service,
        capture=capture_service,
        game_detection=game_detection_service,
        pipeline=translation_pipeline,
        config_service=config_service,
        game_readiness=game_readiness,
    )

    translation_worker = providers.Singleton(
        TranslationWorker,
        live_chat=live_chat_service,
        config_service=config_service,
        speech_output=speech_output_service,
    )

    game_session_service = providers.Singleton(
        GameSessionService,
        game_detection=game_detection_service,
        config_service=config_service,
    )
