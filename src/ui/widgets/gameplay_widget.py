from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import QEvent, Qt, QTimer, pyqtSignal
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

    open_settings_requested = pyqtSignal()

    def __init__(
        self,
        container: Container,
        on_status_update=None,
    ) -> None:
        super().__init__()
        self.setObjectName("GameplayRoot")
        self.container = container
        self.controller = container.gameplay_controller
        self.worker = self.controller.worker
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
        self.chat_input.setObjectName("ChatInputLine")
        self.chat_input.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.chat_input.setPlaceholderText(
            "Tapez ici puis Entrée — envoi auto dans le chat Diablo"
        )
        self.chat_input.installEventFilter(self)

        self._voice_busy = False
        self._shortcuts: list[QShortcut] = []
        self._last_ocr_status_message = ""

        self.translate_button = QPushButton(" Traduire")
        self.translate_button.setObjectName("PrimaryButton")
        self.translate_button.setIcon(AssetManager.icon("translate"))
        self.translate_button.setToolTip("Traduire (Ctrl+Entrée)")
        self.translate_button.clicked.connect(self.translate_chat_message)

        self.copy_button = QPushButton(" Copier")
        self.copy_button.setObjectName("CompactOcrButton")
        self.copy_button.setIcon(AssetManager.icon("translate"))
        self.copy_button.setToolTip("Copier la dernière traduction sortante (Ctrl+C)")
        self.copy_button.clicked.connect(self.copy_last_outgoing_translation)
        self._last_outgoing_translation = ""

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

        self.compact_start_button = QPushButton(" OCR")
        self.compact_start_button.setObjectName("CompactOcrButton")
        self.compact_start_button.setIcon(AssetManager.icon("play"))
        self.compact_start_button.setToolTip("Lire le chat Diablo via OCR")
        self.compact_stop_button = QPushButton(" Stop")
        self.compact_stop_button.setObjectName("CompactOcrButton")
        self.compact_stop_button.setIcon(AssetManager.icon("stop"))
        self.compact_stop_button.setToolTip("Arrêter la surveillance OCR")
        self.compact_settings_button = QPushButton(" Réglages")
        self.compact_settings_button.setObjectName("CompactOcrButton")
        self.compact_settings_button.setIcon(AssetManager.icon("settings"))
        self.compact_settings_button.setToolTip("Ouvrir les paramètres")

        self.last_translation_label = QLabel("Dernière traduction : en attente...")
        self.last_translation_label.setObjectName("MutedText")
        self.last_translation_label.setWordWrap(True)

        self.auto_status_label = QLabel("Surveillance chat : arrêtée")
        self.auto_status_label.setObjectName("MutedText")

        self.monitor_info_label = QLabel()
        self.monitor_info_label.setObjectName("MutedText")
        self.monitor_info_label.setWordWrap(True)

        self._section_titles: list[QLabel] = []
        self._compact_hidden: list[QWidget] = []

        self.start_button.clicked.connect(self.start_worker)
        self.stop_button.clicked.connect(self.stop_worker)
        self.refresh_button.clicked.connect(self.refresh_game_status)
        self.compact_start_button.clicked.connect(self.start_worker)
        self.compact_stop_button.clicked.connect(self.stop_worker)
        self.compact_settings_button.clicked.connect(self.open_settings_requested.emit)

        self._setup_shortcuts()

        compact_ocr_row = QHBoxLayout()
        compact_ocr_row.setSpacing(6)
        compact_ocr_row.addWidget(self.compact_start_button)
        compact_ocr_row.addWidget(self.compact_stop_button)
        compact_ocr_row.addWidget(self.compact_settings_button)
        compact_ocr_row.addStretch()
        self.compact_ocr_bar = QWidget()
        self.compact_ocr_bar.setObjectName("CompactOcrBar")
        self.compact_ocr_bar.setLayout(compact_ocr_row)
        self.compact_ocr_bar.setVisible(False)

        input_row = QHBoxLayout()
        input_row.addWidget(self.chat_input, stretch=1)
        input_row.addWidget(self.translate_button)
        input_row.addWidget(self.copy_button)
        input_row.addWidget(self.voice_button)

        auto_row = QHBoxLayout()
        auto_row.addWidget(self.start_button)
        auto_row.addWidget(self.stop_button)
        auto_row.addWidget(self.refresh_button)
        auto_row.addStretch()

        self.monitor_panel = QWidget()
        monitor_panel_layout = QVBoxLayout()
        monitor_panel_layout.setContentsMargins(0, 0, 0, 0)
        monitor_panel_layout.setSpacing(8)
        monitor_panel_layout.addLayout(auto_row)
        monitor_panel_layout.addWidget(self.auto_status_label)
        monitor_panel_layout.addWidget(self.last_translation_label)
        self.monitor_panel.setLayout(monitor_panel_layout)

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

        chat_title = self._section_title("TRADUCTIONS LIVE")
        layout.addWidget(chat_title)
        layout.addWidget(chat_panel)
        layout.addWidget(self.compact_ocr_bar)
        layout.addLayout(input_row)

        monitor_title = self._section_title("SURVEILLANCE OCR")
        layout.addWidget(monitor_title)
        layout.addWidget(self.monitor_panel)
        self.setLayout(layout)

        self._section_titles = [chat_title, monitor_title]
        self._compact_hidden = [
            self.game_status,
            self.provider_label,
            self.monitor_info_label,
            self.monitor_panel,
            self.voice_button,
            *self._section_titles,
        ]

        self._timer = QTimer(self)
        self._timer.setInterval(2000)
        self._timer.timeout.connect(self.refresh_game_status)
        self._timer.start()

        self.refresh_game_status()
        self._refresh_provider_label()

    def set_compact_mode(self, enabled: bool) -> None:
        for widget in self._compact_hidden:
            widget.setVisible(not enabled)

        self.compact_ocr_bar.setVisible(enabled)
        self.chat_log.setMinimumHeight(120 if enabled else 260)
        self._apply_ingame_mode()
        self._apply_welcome_message(enabled)

    def _apply_ingame_mode(self) -> None:
        compact = self.controller.app_config.overlay_compact
        ingame = self.controller.app_config.ingame_only_mode
        hide_input = ingame and not compact

        self.chat_input.setVisible(not hide_input)
        self.translate_button.setVisible(not hide_input)

        if compact and not hide_input:
            self.chat_input.setPlaceholderText(
                "Tapez + Entrée → traduit et envoie dans Diablo"
            )
            self.translate_button.setText(" →")
        elif not hide_input:
            self.chat_input.setPlaceholderText(
                "Saisie manuelle — Entrée envoie dans le chat Diablo"
            )
            self.translate_button.setText(" Traduire")

        self.voice_button.setVisible(not hide_input and not ingame)

    def _apply_welcome_message(self, compact: bool) -> None:
        if not compact or self.chat_log.toPlainText().strip():
            return

        if self.controller.app_config.ingame_only_mode:
            self._append_chat_html(
                '<span style="color:#d4af37;font-weight:700;">Mode In-Game</span> '
                '<span style="color:#8a8278;">— OCR + saisie manuelle ci-dessous</span>'
            )
        else:
            self._append_chat_html(
                '<span style="color:#8a8278;">OCR du chat Diablo + saisie manuelle ci-dessous</span>'
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
                if self.controller.app_config.overlay_compact:
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

        original_text = text
        self.chat_input.clear()

        try:
            result = self.controller.translate_user_message(original_text)
        except Exception as exc:
            self._append_chat_line("Erreur", str(exc), "#c0392b")
            return

        self.display_translation_result(result, speaker="Vous", manual_input=True)

        if result.skipped and not result.preserved_mixed:
            text_to_send = original_text
        else:
            text_to_send = result.translated_text.strip()

        if text_to_send and self.controller.app_config.auto_send_to_game:
            overlay_hwnd = int(self.window().winId()) if self.window() else None
            ok, error = self.controller.send_to_game_chat(
                text_to_send,
                restore_hwnd=overlay_hwnd,
            )
            if ok:
                self._append_chat_line(
                    "Info",
                    "Message envoyé dans le chat Diablo.",
                    "#7cb342",
                )
            else:
                self._append_chat_line("Erreur", error, "#c0392b")

        self._notify_status_update()

    def copy_last_outgoing_translation(self) -> None:
        if not self._last_outgoing_translation:
            self._append_chat_line(
                "Info",
                "Aucune traduction sortante à copier pour l'instant.",
                "#8a8278",
            )
            return
        self._copy_to_clipboard(self._last_outgoing_translation)
        self._append_chat_line(
            "Info",
            "Traduction copiée — collez-la vous-même dans Diablo (Ctrl+V).",
            "#8a8278",
        )

    def toggle_voice_input(self) -> None:
        if self._voice_busy:
            return

        if self.controller.speech_input.is_listening:
            self.controller.speech_input.stop()
            self._reset_voice_button()
            self._append_system_message("Microphone désactivé.")
            return

        available, error = SpeechInputService.check_availability()
        if not available:
            self._reset_voice_button()
            self._append_chat_line("Erreur", error, "#c0392b")
            return

        self._voice_busy = True
        started = self.controller.speech_input.start()
        self._voice_busy = False

        if not started or not self.controller.speech_input.is_listening:
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

        error = self.controller.start_monitoring(auto=auto)
        if error:
            self._append_system_message(error)
            return

        status = self.controller.scan_games()
        self.auto_status_label.setText(
            f"Surveillance chat : active ({status.summary()})"
        )
        if not auto:
            self._append_system_message(
                f"Surveillance OCR démarrée — {status.summary()}"
            )
        elif self.controller.app_config.overlay_compact:
            self._append_overlay_status("OCR actif — lecture du chat Diablo…")
        self._notify_status_update()

    def stop_worker(self) -> None:
        self.controller.stop_monitoring()
        self.auto_status_label.setText("Surveillance chat : arrêtée")
        self._append_system_message("Surveillance chat arrêtée.")
        self._notify_status_update()

    def display_translation_result(
        self,
        result: TranslationResult,
        *,
        speaker: str = "Chat",
        manual_input: bool = False,
    ) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        translator = self.controller.pipeline.translator

        if result.preserved_mixed:
            self._append_chat_line(speaker, result.source_text, "#e8dcc8")
            return

        if result.skipped:
            if result.outgoing:
                source_lang = translator.language_display_name(result.source_language)
                self._append_chat_line(
                    "Info",
                    f"Déjà en {source_lang} — rien à traduire",
                    "#8a8278",
                )
            return

        if result.outgoing:
            target_label = translator.language_display_name(result.target_language)
            compact = self.controller.app_config.overlay_compact
            if compact:
                self._append_chat_html(
                    f'<span style="color:#64b5f6;font-weight:700;">Vous → {target_label}</span> '
                    f'<span style="color:#ffffff;font-size:108%;">'
                    f'{self._escape_html(result.translated_text)}</span><br/>'
                    f'<span style="color:#6b5f52;font-size:88%;">'
                    f'{self._escape_html(result.source_text)}</span>'
                )
            else:
                self._append_chat_html(
                    f'<span style="color:#6b5f52;">[{timestamp}]</span> '
                    f'<span style="color:#64b5f6;font-weight:700;">[Vous → {target_label}]</span> '
                    f'<span style="color:#ffffff;font-size:105%;">'
                    f'{self._escape_html(result.translated_text)}</span><br/>'
                    f'<span style="color:#6b5f52;font-size:92%;">'
                    f'{self._escape_html(result.source_text)}</span>'
                )
            if self.controller.app_config.auto_copy_outgoing and not manual_input:
                self._copy_to_clipboard(result.translated_text)
            self._last_outgoing_translation = result.translated_text
            self.last_translation_label.setText(
                f"Envoyé en {target_label} : {result.translated_text}"
                if manual_input and self.controller.app_config.auto_send_to_game
                else f"À coller en {target_label} : {result.translated_text}"
            )
            self._refresh_provider_label()
            return

        source_label = translator.language_display_name(result.source_language)
        show_source = self._should_show_source_reference(result)
        if self.controller.app_config.overlay_compact:
            if show_source:
                self._append_chat_html(
                    f'<span style="color:#ffffff;font-size:110%;">'
                    f'{self._escape_html(result.translated_text)}</span> '
                    f'<span style="color:#6b5f52;font-size:88%;">'
                    f'← {self._escape_html(result.source_text)}</span>'
                )
            else:
                self._append_chat_html(
                    f'<span style="color:#ffffff;font-size:110%;">'
                    f'{self._escape_html(result.translated_text)}</span>'
                )
        else:
            self._append_chat_html(
                f'<span style="color:#6b5f52;">[{timestamp}]</span> '
                f'<span style="color:#7cb342;font-weight:700;">[Chat FR]</span> '
                f'<span style="color:#ffffff;font-size:105%;">'
                f'{self._escape_html(result.translated_text)}</span><br/>'
                f'<span style="color:#6b5f52;font-size:92%;">'
                f'{self._escape_html(result.source_text)} '
                f'({source_label})</span>'
            )
        self.last_translation_label.setText(
            f"Dernier message : {result.source_text} → {result.translated_text}"
        )
        self._refresh_provider_label()

    def show_live_translation(self, result: TranslationResult) -> None:
        speaker = "Vous (Diablo)" if result.outgoing else "Chat jeu"
        self.display_translation_result(result, speaker=speaker)

    def update_ocr_status(self, status) -> None:
        if not self.worker.is_running:
            return

        if status.last_error:
            prefix = "Traduction" if status.last_error.startswith("Traduction") else "OCR"
            detail = status.last_error.removeprefix("Traduction : ").strip()
            message = (
                f"{prefix} : {detail}"
                if prefix == "Traduction"
                else f"OCR erreur : {detail}"
            )
            if message == self._last_ocr_status_message:
                return
            self._last_ocr_status_message = message
            self._append_overlay_status(message, error=True)
            return

        if not self.controller.app_config.overlay_compact:
            self.auto_status_label.setText(
                f"OCR : {status.ocr_line_count} lignes · "
                f"{status.new_message_count} nouveau(x) · preset {status.preset_key}"
            )
            return

        if status.new_message_count:
            return

        if status.ocr_line_count == 0:
            message = (
                "OCR : aucun texte lu — preset 1080p, fermez Contacts, "
                "1 seule instance ouverte"
            )
        else:
            message = (
                f"OCR actif ({status.ocr_line_count} lignes, preset {status.preset_key})"
            )

        if message == self._last_ocr_status_message:
            return
        self._last_ocr_status_message = message
        self._append_overlay_status(message, error=status.ocr_line_count == 0)

    def handle_voice_result(self, payload) -> None:
        if isinstance(payload, str) and payload.startswith("__ERROR__:"):
            self._reset_voice_button()
            self.controller.speech_input.stop()
            self._append_chat_line(
                "Erreur",
                payload.replace("__ERROR__:", ""),
                "#c0392b",
            )
            return

        if isinstance(payload, TranslationResult):
            self.display_translation_result(payload, speaker="Voix")

    def refresh_game_status(self) -> None:
        status = self.controller.scan_games()
        self.game_status.update_status(status)
        self._refresh_provider_label()

        monitor_mode = (
            "OCR zone chat (coin inférieur gauche)"
            if self.controller.app_config.chat_monitor_enabled
            else "OCR plein écran"
        )
        self.monitor_info_label.setText(
            f"Mode : {monitor_mode} · {self.controller.monitor_mode_label()} · "
            f"In-game : {'ON' if self.controller.app_config.ingame_only_mode else 'OFF'} · "
            f"Joueur : {self.controller.player_label()}"
        )

        if self.worker.is_running and status.is_any_running:
            self.auto_status_label.setText(
                f"Surveillance chat : active ({status.summary()})"
            )

        self._notify_status_update()

    def _refresh_provider_label(self) -> None:
        summary = self.controller.provider_summary()
        mode = summary.mode
        if summary.peer_label:
            mode += f" (dernier chat : {summary.peer_label})"
        self.provider_label.setText(
            f"{mode} · Moteur : {summary.provider} · Cache : {summary.cache_entries} entrées"
        )

    def _notify_status_update(self) -> None:
        if self._on_status_update:
            self._on_status_update()

    def _append_chat_line(self, speaker: str, message: str, color: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._append_chat_html(
            f'<span style="color:#6b5f52;">[{timestamp}]</span> '
            f'<span style="color:{color}; font-weight:600;">[{speaker}]</span> '
            f'<span style="color:#e8dcc8;">{self._escape_html(message)}</span>'
        )

    def _append_chat_html(self, html: str) -> None:
        self.chat_log.append(html)
        scrollbar = self.chat_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _copy_to_clipboard(self, text: str) -> None:
        try:
            import pyperclip

            pyperclip.copy(text)
        except Exception:
            pass

    def _append_system_message(self, message: str) -> None:
        if self.controller.app_config.overlay_compact:
            return
        self._append_chat_line("Système", message, "#8a8278")

    def _append_overlay_status(self, message: str, *, error: bool = False) -> None:
        if not self.controller.app_config.overlay_compact:
            return
        color = "#c0392b" if error else "#8a8278"
        self._append_chat_html(
            f'<span style="color:{color};font-size:90%;">[OCR] {self._escape_html(message)}</span>'
        )

    @staticmethod
    def _escape_html(value: str) -> str:
        return (
            value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    @staticmethod
    def _should_show_source_reference(result: TranslationResult) -> bool:
        from src.chat.chat_text_normalizer import ChatTextNormalizer

        source = ChatTextNormalizer.normalize_line(result.source_text)
        translated = ChatTextNormalizer.normalize_line(result.translated_text)
        if not source or not translated:
            return False
        return source.casefold() != translated.casefold()

    def keyPressEvent(self, event) -> None:
        if (
            not self.chat_input.hasFocus()
            and event.text()
            and event.text().isprintable()
            and not event.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            self.chat_input.setFocus(Qt.FocusReason.OtherFocusReason)
            self.chat_input.insert(event.text())
            event.accept()
            return
        super().keyPressEvent(event)

    def shutdown(self) -> None:
        self.controller.speech_input.stop()
        self.controller.stop_monitoring()
