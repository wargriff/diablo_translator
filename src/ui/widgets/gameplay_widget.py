from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import QEvent, Qt, QTimer
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.domain.models.translation_result import TranslationResult
from src.infrastructure.asset_manager import AssetManager
from src.infrastructure.container import Container
from src.ui.widgets.game_status_panel import GameStatusPanel
from src.voice.speech_service import SpeechInputService


class GameplayWidget(QWidget):

    def __init__(
        self,
        container: Container,
        on_status_update=None,
    ) -> None:
        super().__init__()
        self.setObjectName("GameplayRoot")
        self.container = container
        self.worker = container.worker
        self._on_status_update = on_status_update

        self.game_status = GameStatusPanel(container)
        self.provider_label = QLabel()
        self.provider_label.setObjectName("MutedText")

        self.chat_log = QTextEdit()
        self.chat_log.setObjectName("ChatLog")
        self.chat_log.setReadOnly(True)
        self.chat_log.setMinimumHeight(260)
        self.chat_log.setFont(AssetManager.monospace_font(10))

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText(
            "Tapez un message… Ctrl+Entrée pour traduire (Entrée ne valide plus)"
        )
        self.chat_input.installEventFilter(self)

        self._voice_busy = False
        self._shortcuts: list[QShortcut] = []

        self.translate_button = QPushButton(" Traduire")
        self.translate_button.setObjectName("PrimaryButton")
        self.translate_button.setIcon(AssetManager.icon("translate"))
        self.translate_button.setToolTip("Traduire (Ctrl+Entrée)")
        self.translate_button.clicked.connect(self.translate_chat_message)

        self.voice_button = QPushButton(" Micro")
        self.voice_button.setIcon(AssetManager.icon("mic"))
        self.voice_button.setToolTip("Activer/désactiver le micro (Ctrl+Shift+M)")
        self.voice_button.clicked.connect(self.toggle_voice_input)

        self.start_button = QPushButton(" Surveiller chat")
        self.start_button.setIcon(AssetManager.icon("play"))
        self.start_button.setToolTip("Lire le chat Diablo en direct via OCR")
        self.stop_button = QPushButton(" Arrêter")
        self.stop_button.setIcon(AssetManager.icon("stop"))
        self.refresh_button = QPushButton(" Actualiser")
        self.refresh_button.setToolTip("Actualiser l'état des jeux (Ctrl+Shift+R)")

        self.last_translation_label = QLabel("Dernière traduction : en attente...")
        self.last_translation_label.setObjectName("MutedText")
        self.last_translation_label.setWordWrap(True)

        self.auto_status_label = QLabel("Surveillance chat : arrêtée")
        self.auto_status_label.setObjectName("MutedText")

        self.monitor_info_label = QLabel()
        self.monitor_info_label.setObjectName("MutedText")
        self.monitor_info_label.setWordWrap(True)

        self.start_button.clicked.connect(self.start_worker)
        self.stop_button.clicked.connect(self.stop_worker)
        self.refresh_button.clicked.connect(self.refresh_game_status)

        self._setup_shortcuts()

        input_row = QHBoxLayout()
        input_row.addWidget(self.chat_input, stretch=1)
        input_row.addWidget(self.translate_button)
        input_row.addWidget(self.voice_button)

        auto_row = QHBoxLayout()
        auto_row.addWidget(self.start_button)
        auto_row.addWidget(self.stop_button)
        auto_row.addWidget(self.refresh_button)
        auto_row.addStretch()

        chat_panel = QFrame()
        chat_panel.setObjectName("ChatPanel")
        chat_layout = QVBoxLayout()
        chat_layout.addWidget(self.chat_log)
        chat_panel.setLayout(chat_layout)

        layout = QVBoxLayout()
        layout.setSpacing(14)
        layout.addWidget(self.game_status)
        layout.addWidget(self.provider_label)
        layout.addWidget(self.monitor_info_label)
        layout.addWidget(self._section_title("CHAT — TEST & TRADUCTIONS LIVE"))
        layout.addWidget(chat_panel)
        layout.addLayout(input_row)
        layout.addWidget(self._section_title("SURVEILLANCE CHAT DIABLO (OCR)"))
        layout.addLayout(auto_row)
        layout.addWidget(self.auto_status_label)
        layout.addWidget(self.last_translation_label)
        self.setLayout(layout)

        self._timer = QTimer(self)
        self._timer.setInterval(2000)
        self._timer.timeout.connect(self.refresh_game_status)
        self._timer.start()

        self.refresh_game_status()
        self._refresh_provider_label()
        self._append_system_message(
            "Interface prête. Le chat du jeu est lu en direct via OCR "
            "sur la zone inférieure gauche."
        )

    def _setup_shortcuts(self) -> None:
        # Raccourcis actifs seulement hors champs de saisie (WidgetShortcut).
        translate_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        translate_shortcut.setContext(Qt.ShortcutContext.WidgetShortcut)
        translate_shortcut.activated.connect(self.translate_chat_message)
        self._shortcuts.append(translate_shortcut)

        voice_shortcut = QShortcut(QKeySequence("Ctrl+Shift+M"), self)
        voice_shortcut.setContext(Qt.ShortcutContext.WidgetShortcut)
        voice_shortcut.activated.connect(self.toggle_voice_input)
        self._shortcuts.append(voice_shortcut)

        refresh_shortcut = QShortcut(QKeySequence("Ctrl+Shift+R"), self)
        refresh_shortcut.setContext(Qt.ShortcutContext.WidgetShortcut)
        refresh_shortcut.activated.connect(self.refresh_game_status)
        self._shortcuts.append(refresh_shortcut)

    def eventFilter(self, obj, event) -> bool:
        if obj is self.chat_input and event.type() == QEvent.Type.KeyPress:
            key = event.key()
            modifiers = event.modifiers()

            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                if modifiers & Qt.KeyboardModifier.ControlModifier:
                    self.translate_chat_message()
                    return True
                return False

        return super().eventFilter(obj, event)

    @staticmethod
    def _section_title(text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("SectionTitle")
        return label

    def translate_chat_message(self) -> None:
        text = self.chat_input.text().strip()
        if not text:
            return

        self.chat_input.clear()

        try:
            result = self.container.pipeline.process_text(text, origin="user")
        except Exception as exc:
            self._append_chat_line("Erreur", str(exc), "#c0392b")
            return

        self.display_translation_result(result, speaker="Vous")
        self._notify_status_update()

    def toggle_voice_input(self) -> None:
        if self._voice_busy:
            return

        if self.container.speech_input.is_listening:
            self.container.speech_input.stop()
            self._reset_voice_button()
            self._append_system_message("Microphone désactivé.")
            return

        available, error = SpeechInputService.check_availability()
        if not available:
            self._reset_voice_button()
            self._append_chat_line("Erreur", error, "#c0392b")
            return

        self._voice_busy = True
        started = self.container.speech_input.start()
        self._voice_busy = False

        if not started or not self.container.speech_input.is_listening:
            self._reset_voice_button()
            return

        self.voice_button.setText(" Micro ON")
        self._append_system_message(
            "Microphone actif — parlez pour traduire automatiquement."
        )

    def _reset_voice_button(self) -> None:
        self.voice_button.setText(" Micro")

    def start_worker(self, *, auto: bool = False) -> None:
        if self.worker.is_running:
            return

        status = self.container.game_detection.scan()
        if not status.is_any_running:
            if not auto:
                self._append_system_message(
                    "Aucun jeu Diablo détecté. Lancez D3, D4 ou Immortal."
                )
            return

        if not self.container.config.chat_monitor_enabled:
            if not auto:
                self._append_system_message(
                    "Activez « Surveiller chat en direct » dans les paramètres."
                )
            return

        self.worker.start()
        self.auto_status_label.setText(
            f"Surveillance chat : active ({status.summary()})"
        )
        self._append_system_message(
            f"Surveillance OCR démarrée — {status.summary()}"
        )
        self._notify_status_update()

    def stop_worker(self) -> None:
        self.worker.stop()
        self.auto_status_label.setText("Surveillance chat : arrêtée")
        self._append_system_message("Surveillance chat arrêtée.")
        self._notify_status_update()

    def display_translation_result(
        self,
        result: TranslationResult,
        *,
        speaker: str = "Chat",
    ) -> None:
        source_lang = self.container.pipeline.translator.language_display_name(
            result.source_language
        )
        provider = result.provider.upper()

        self._append_chat_line(speaker, result.source_text, "#c9a24d")

        if result.preserved_mixed:
            self._append_chat_line(
                "Info",
                "Mixte FR/EN conservé tel quel",
                "#8a8278",
            )
        elif result.skipped:
            self._append_chat_line(
                "Info",
                f"Déjà en {source_lang} — traduction ignorée",
                "#8a8278",
            )
        else:
            source_name = self.container.pipeline.translator.language_display_name(
                result.source_language
            )
            target_name = self.container.pipeline.translator.language_display_name(
                result.target_language
            )
            label = "Réponse" if result.outgoing else "Traduction"
            self._append_chat_line(
                label,
                f"{result.translated_text} [{source_name} → {target_name} · {provider}]",
                "#7cb342" if not result.outgoing else "#64b5f6",
            )

        self.last_translation_label.setText(
            f"Dernière traduction : {result.source_text} → {result.display_text}"
        )

    def show_live_translation(self, result: TranslationResult) -> None:
        self.display_translation_result(result, speaker="Chat jeu")

    def handle_voice_result(self, payload) -> None:
        if isinstance(payload, str) and payload.startswith("__ERROR__:"):
            self._reset_voice_button()
            self.container.speech_input.stop()
            self._append_chat_line(
                "Erreur",
                payload.replace("__ERROR__:", ""),
                "#c0392b",
            )
            return

        if isinstance(payload, TranslationResult):
            self.display_translation_result(payload, speaker="Voix")

    def refresh_game_status(self) -> None:
        status = self.container.game_detection.scan()
        self.game_status.update_status(status)
        self._refresh_provider_label()

        monitor_mode = (
            "OCR zone chat (coin inférieur gauche)"
            if self.container.config.chat_monitor_enabled
            else "OCR plein écran"
        )
        self.monitor_info_label.setText(
            f"Mode : {monitor_mode} · Moteur : {self.container.config.translator.upper()} · "
            f"Détection langue : {'ON' if self.container.config.auto_detect_language else 'OFF'}"
        )

        if self.worker.is_running and status.is_any_running:
            self.auto_status_label.setText(
                f"Surveillance chat : active ({status.summary()})"
            )

        self._notify_status_update()

    def _refresh_provider_label(self) -> None:
        provider = self.container.pipeline.translator.provider_name.upper()
        target = self.container.config.language.upper()
        cache = self.container.pipeline.cache.stats
        peer = self.container.pipeline.conversation.last_foreign_language
        peer_text = (
            f" · Réponse auto : {peer.upper()}"
            if peer and self.container.config.bidirectional_mode
            else ""
        )
        self.provider_label.setText(
            f"Moteur : {provider} · Langue maison : {target}{peer_text} · "
            f"Cache disque : {cache.entries} entrées"
        )

    def _notify_status_update(self) -> None:
        if self._on_status_update:
            self._on_status_update()

    def _append_chat_line(self, speaker: str, message: str, color: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_log.append(
            f'<span style="color:#6b5f52;">[{timestamp}]</span> '
            f'<span style="color:{color}; font-weight:600;">[{speaker}]</span> '
            f'<span style="color:#e8dcc8;">{self._escape_html(message)}</span>'
        )

    def _append_system_message(self, message: str) -> None:
        self._append_chat_line("Système", message, "#8a8278")

    @staticmethod
    def _escape_html(value: str) -> str:
        return (
            value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    def shutdown(self) -> None:
        self.container.speech_input.stop()
        self.worker.stop()
