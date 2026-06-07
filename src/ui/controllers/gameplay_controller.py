from __future__ import annotations

from dataclasses import dataclass

from src.application.config_service import ConfigService
from src.application.live_chat_service import LiveChatService
from src.domain.models.translation_result import TranslationResult
from src.game_detection.game_detection_service import GameDetectionService
from src.translation.translation_pipeline import TranslationPipeline
from src.voice.speech_service import SpeechInputService


@dataclass(frozen=True, slots=True)
class ProviderSummary:

    mode: str
    provider: str
    cache_entries: int
    reply_label: str
    peer_label: str | None


class GameplayController:

    def __init__(
        self,
        live_chat: LiveChatService,
        pipeline: TranslationPipeline,
        game_detection: GameDetectionService,
        config_service: ConfigService,
        speech_input: SpeechInputService,
    ) -> None:
        self.live_chat = live_chat
        self.pipeline = pipeline
        self.game_detection = game_detection
        self.config = config_service
        self.speech_input = speech_input
        self.worker = live_chat.worker

    @property
    def app_config(self):
        return self.config.config

    def translate_user_message(self, text: str) -> TranslationResult:
        return self.live_chat.translate_user_text(text)

    def start_monitoring(self, *, auto: bool = False) -> str | None:
        status = self.game_detection.scan()
        if not status.is_any_running:
            if auto:
                return None
            return "Aucun jeu Diablo détecté. Lancez D3, D4 ou Immortal."

        if not self.app_config.chat_monitor_enabled:
            if auto:
                return None
            return "Activez la surveillance chat dans les paramètres."

        self.worker.start()
        return None

    def stop_monitoring(self) -> None:
        self.worker.stop()

    def scan_games(self):
        return self.game_detection.scan()

    def provider_summary(self) -> ProviderSummary:
        config = self.app_config
        translator = self.pipeline.translator
        cache = self.pipeline.cache.stats
        reply_label = translator.reply_language_label()
        peer = self.pipeline.conversation.last_foreign_language
        mode = (
            f"Chat → FR · Vous → {reply_label}"
            if config.bidirectional_mode
            else f"Langue cible : {config.language.upper()}"
        )
        peer_label = (
            translator.language_display_name(peer)
            if peer
            else None
        )
        return ProviderSummary(
            mode=mode,
            provider=translator.provider_name.upper(),
            cache_entries=cache.entries,
            reply_label=reply_label,
            peer_label=peer_label,
        )

    def player_label(self) -> str:
        config = self.app_config
        if config.player_name.strip():
            return config.player_name.strip()
        learned = self.live_chat.player_identity.learned_name
        if learned:
            return f"{learned} (auto)"
        return "auto"

    def monitor_mode_label(self) -> str:
        status = self.live_chat.last_status
        display = {
            "fullscreen": "Plein écran",
            "borderless": "Borderless",
            "windowed": "Fenêtré",
            "monitor": "Moniteur",
        }.get(status.display_mode, status.display_mode)

        source = {
            "game_monitor_fullscreen": "moniteur jeu plein écran",
            "game_window_fullscreen": "fenêtre plein écran",
            "game_client": "fenêtre jeu",
            "game_client_forced": "client jeu",
            "game_fullscreen_forced": "plein écran forcé",
            "monitor_primary": "moniteur principal",
        }.get(status.capture_source, status.capture_source)

        return f"{display} · {source} · moniteur {status.monitor_index}"
