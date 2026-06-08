from __future__ import annotations

from dataclasses import asdict

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.application.config_profiles import PROFILE_CATALOG
from src.chat.chat_region import CHAT_REGION_PRESETS
from src.game_detection import SUPPORTED_GAMES
from src.infrastructure.asset_manager import AssetManager
from src.infrastructure.config_manager import AppConfig


class SettingsFormWidget(QWidget):

    config_changed = pyqtSignal()

    SIDEBAR_ITEMS = (
        ("profiles", "Profils Pro"),
        ("translation", "Traduction"),
        ("overlay", "Overlay"),
        ("ocr", "OCR Diablo"),
        ("games", "Jeux / Launch"),
        ("identity", "Identité Joueur"),
    )

    def __init__(self, config: AppConfig, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._config = AppConfig(**asdict(config))
        self._build_fields()
        self._build_ui()

    def _build_ui(self) -> None:
        self.summary_label = QLabel()
        self.summary_label.setObjectName("MutedText")
        self.summary_label.setWordWrap(True)
        self._refresh_summary()

        self.sidebar = QComboBox()
        for _, label in self.SIDEBAR_ITEMS:
            self.sidebar.addItem(label)
        self.sidebar.currentIndexChanged.connect(self._switch_page)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._wrap_scroll(self._build_profiles_page()))
        self.stack.addWidget(self._wrap_scroll(self._build_translation_page()))
        self.stack.addWidget(self._wrap_scroll(self._build_overlay_page()))
        self.stack.addWidget(self._wrap_scroll(self._build_ocr_page()))
        self.stack.addWidget(self._wrap_scroll(self._build_games_page()))
        self.stack.addWidget(self._wrap_scroll(self._build_identity_page()))

        nav_row = QHBoxLayout()
        nav_row.addWidget(QLabel("Section"))
        nav_row.addWidget(self.sidebar, stretch=1)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.addWidget(self.summary_label)
        layout.addLayout(nav_row)
        layout.addWidget(self.stack, stretch=1)
        self.setLayout(layout)

        self.sidebar.setCurrentIndex(0)

    @staticmethod
    def _wrap_scroll(page: QWidget) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(page)
        return scroll

    def _switch_page(self, index: int) -> None:
        if index >= 0:
            self.stack.setCurrentIndex(index)

    def _build_profiles_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout()

        intro = QLabel(
            "Profils pro pré-calibrés pour Diablo III / IV en plein écran 1080p."
        )
        intro.setObjectName("MutedText")
        intro.setWordWrap(True)
        layout.addWidget(intro)

        grid = QGridLayout()
        grid.setSpacing(12)
        for index, (key, meta) in enumerate(PROFILE_CATALOG.items()):
            card = self._profile_card(meta["title"], meta["subtitle"], key)
            grid.addWidget(card, index // 2, index % 2)
        layout.addLayout(grid)
        layout.addStretch()
        page.setLayout(layout)
        return page

    def _profile_card(self, title: str, subtitle: str, profile_key: str) -> QFrame:
        card = QFrame()
        card.setObjectName("Panel")

        title_label = QLabel(title)
        title_label.setObjectName("SectionTitle")

        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("MutedText")
        subtitle_label.setWordWrap(True)

        button = QPushButton(" Activer ce profil")
        button.setObjectName("PrimaryButton")
        button.setIcon(AssetManager.icon("settings"))
        button.clicked.connect(lambda: self._apply_profile(profile_key))

        card_layout = QVBoxLayout()
        card_layout.addWidget(title_label)
        card_layout.addWidget(subtitle_label)
        card_layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignLeft)
        card.setLayout(card_layout)
        return card

    def _apply_profile(self, profile_key: str) -> None:
        meta = PROFILE_CATALOG[profile_key]
        self._config = meta["apply"](self._config)
        self._sync_fields_from_config()
        self._refresh_summary()
        self.config_changed.emit()

    def _build_translation_page(self) -> QWidget:
        form = QFormLayout()
        form.addRow("Langue maison", self.language)
        form.addRow("Traduction bidirectionnelle", self.bidirectional_mode)
        form.addRow("Langue de réponse par défaut", self.default_reply_language)
        form.addRow("Détection automatique des langues", self.auto_detect_language)
        form.addRow("Conserver le mixte FR/EN (vos messages)", self.preserve_mixed_language)
        form.addRow("Copier auto vos traductions", self.auto_copy_outgoing)
        form.addRow("Envoyer auto dans le chat Diablo", self.auto_send_to_game)
        form.addRow("Délai démarrage OCR (sec)", self.startup_delay_seconds)
        form.addRow("Attente lancement Diablo (sec)", self.game_startup_grace_seconds)
        widget = QWidget()
        widget.setLayout(form)
        return widget

    def _build_overlay_page(self) -> QWidget:
        form = QFormLayout()
        form.addRow("Mode overlay sur le chat", self.overlay_compact)
        form.addRow("Masquer saisie manuelle (OCR seul)", self.ingame_only_mode)
        form.addRow("Barre Windows native (deplacer / fermer)", self.overlay_native_frame)
        form.addRow("Memoriser position fenetre", self.overlay_remember_position)
        form.addRow("Toujours devant", self.always_on_top)
        form.addRow("Opacité overlay", self.overlay_opacity)
        form.addRow("Largeur overlay", self.overlay_width)
        form.addRow("Hauteur overlay", self.overlay_height)
        form.addRow("Clics traversants (cliquer le jeu à travers)", self.overlay_click_through)
        widget = QWidget()
        widget.setLayout(form)
        return widget

    def _build_ocr_page(self) -> QWidget:
        form = QFormLayout()
        form.addRow("Profil résolution", self.resolution_profile)
        form.addRow("Zone OCR chat", self.chat_region)
        form.addRow("Mode affichage Diablo", self.display_mode)
        form.addRow("Capture fenêtre / moniteur jeu", self.capture_from_game_window)
        form.addRow("Plein écran → moniteur entier", self.capture_fullscreen_monitor)
        form.addRow("Boost OCR (contraste ×2)", self.ocr_preprocess)
        form.addRow("Confiance OCR minimum", self.ocr_confidence_min)
        form.addRow("Vitesse OCR (1 = stable)", self.capture_fps)
        form.addRow("Mode CPU réduit", self.low_cpu_mode)
        form.addRow("Surveillance auto au lancement", self.auto_start_monitor)
        widget = QWidget()
        widget.setLayout(form)
        return widget

    def _build_games_page(self) -> QWidget:
        form = QFormLayout()
        form.addRow("Jeu mis en avant (bouton hero)", self.preferred_launch_game)
        form.addRow("Diablo III (.exe)", self._exe_path_row(self.d3_exe_path, "d3"))
        form.addRow("Diablo IV (.exe)", self._exe_path_row(self.d4_exe_path, "d4"))
        form.addRow("Diablo Immortal (.exe)", self._exe_path_row(self.immortal_exe_path, "immortal"))

        hint = QLabel(
            "Indiquez le chemin complet vers l’exe du jeu. "
            "Le bouton Launch de l’onglet dédié utilisera ces chemins."
        )
        hint.setObjectName("MutedText")
        hint.setWordWrap(True)

        widget = QWidget()
        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(hint)
        widget.setLayout(layout)
        return widget

    def _exe_path_row(self, field: QLineEdit, game_key: str) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(field, stretch=1)

        browse = QPushButton(" Parcourir…")
        browse.setObjectName("CompactOcrButton")
        browse.clicked.connect(lambda: self._browse_exe(field))

        layout.addWidget(browse)
        row.setLayout(layout)
        return row

    def _browse_exe(self, field: QLineEdit) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir l’exe Diablo",
            field.text() or "",
            "Executables (*.exe);;Tous (*.*)",
        )
        if path:
            field.setText(path)
            self._refresh_summary()
            self.config_changed.emit()

    def _build_identity_page(self) -> QWidget:
        form = QFormLayout()
        form.addRow("Nom de personnage Diablo III", self.player_name)
        form.addRow("Détecter mon nom automatiquement", self.auto_detect_player)
        hint = QLabel(
            "Laisse vide pour auto-détection depuis le chat Diablo."
        )
        hint.setObjectName("MutedText")
        hint.setWordWrap(True)
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(hint)
        widget.setLayout(layout)
        return widget

    def _build_fields(self) -> None:
        config = self._config

        self.language = QComboBox()
        self.language.addItems(["fr", "en", "de", "es"])
        self.language.currentTextChanged.connect(self._on_field_changed)

        self.bidirectional_mode = QCheckBox()
        self.default_reply_language = QComboBox()
        self.default_reply_language.addItems(["en", "de", "es", "it", "pt", "ru", "pl"])
        self.auto_detect_language = QCheckBox()
        self.preserve_mixed_language = QCheckBox()
        self.auto_copy_outgoing = QCheckBox()
        self.auto_send_to_game = QCheckBox()
        self.startup_delay_seconds = QSpinBox()
        self.startup_delay_seconds.setRange(0, 15)
        self.game_startup_grace_seconds = QSpinBox()
        self.game_startup_grace_seconds.setRange(5, 60)

        self.overlay_compact = QCheckBox()
        self.ingame_only_mode = QCheckBox()
        self.overlay_native_frame = QCheckBox()
        self.overlay_remember_position = QCheckBox()
        self.always_on_top = QCheckBox()
        self.overlay_click_through = QCheckBox()

        self.overlay_opacity = QDoubleSpinBox()
        self.overlay_opacity.setRange(0.55, 1.0)
        self.overlay_opacity.setSingleStep(0.05)

        self.overlay_width = QSpinBox()
        self.overlay_width.setRange(280, 700)

        self.overlay_height = QSpinBox()
        self.overlay_height.setRange(160, 420)

        self.resolution_profile = QComboBox()
        self.resolution_profile.addItem("1920×1080 (Full HD)", "1080p")
        self.resolution_profile.addItem("2560×1440 (QHD)", "1440p")
        self.resolution_profile.addItem("Auto", "auto")

        self.chat_region = QComboBox()
        for preset in CHAT_REGION_PRESETS:
            self.chat_region.addItem(preset.title, preset.key)

        self.display_mode = QComboBox()
        self.display_mode.addItem("Auto (détecte plein écran)", "auto")
        self.display_mode.addItem("Plein écran forcé", "fullscreen")
        self.display_mode.addItem("Fenêtré", "windowed")

        self.capture_from_game_window = QCheckBox()
        self.capture_fullscreen_monitor = QCheckBox()
        self.ocr_preprocess = QCheckBox()
        self.ocr_confidence_min = QDoubleSpinBox()
        self.ocr_confidence_min.setRange(0.15, 0.90)
        self.ocr_confidence_min.setSingleStep(0.05)
        self.capture_fps = QSpinBox()
        self.capture_fps.setRange(1, 4)
        self.low_cpu_mode = QCheckBox()
        self.auto_start_monitor = QCheckBox()

        self.player_name = QLineEdit()
        self.auto_detect_player = QCheckBox()

        self.d3_exe_path = QLineEdit()
        self.d4_exe_path = QLineEdit()
        self.immortal_exe_path = QLineEdit()
        self.preferred_launch_game = QComboBox()
        for game in SUPPORTED_GAMES:
            self.preferred_launch_game.addItem(game.title, game.key)

        self._sync_fields_from_config()
        self._wire_change_signals()

    def _wire_change_signals(self) -> None:
        widgets = (
            self.language,
            self.bidirectional_mode,
            self.default_reply_language,
            self.auto_detect_language,
            self.preserve_mixed_language,
            self.auto_copy_outgoing,
            self.auto_send_to_game,
            self.startup_delay_seconds,
            self.game_startup_grace_seconds,
            self.overlay_compact,
            self.ingame_only_mode,
            self.overlay_native_frame,
            self.overlay_remember_position,
            self.always_on_top,
            self.overlay_click_through,
            self.overlay_opacity,
            self.overlay_width,
            self.overlay_height,
            self.resolution_profile,
            self.chat_region,
            self.display_mode,
            self.capture_from_game_window,
            self.capture_fullscreen_monitor,
            self.ocr_preprocess,
            self.ocr_confidence_min,
            self.capture_fps,
            self.low_cpu_mode,
            self.auto_start_monitor,
            self.player_name,
            self.auto_detect_player,
            self.d3_exe_path,
            self.d4_exe_path,
            self.immortal_exe_path,
            self.preferred_launch_game,
        )
        for widget in widgets:
            if isinstance(widget, QComboBox):
                widget.currentIndexChanged.connect(self._on_field_changed)
            elif isinstance(widget, QCheckBox):
                widget.toggled.connect(self._on_field_changed)
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                widget.valueChanged.connect(self._on_field_changed)
            elif isinstance(widget, QLineEdit):
                widget.textChanged.connect(self._on_field_changed)

    def _on_field_changed(self, *_args) -> None:
        self._refresh_summary()
        self.config_changed.emit()

    def _sync_fields_from_config(self) -> None:
        config = self._config
        self.language.setCurrentText(config.language)
        self.bidirectional_mode.setChecked(config.bidirectional_mode)
        self.default_reply_language.setCurrentText(config.default_reply_language)
        self.auto_detect_language.setChecked(config.auto_detect_language)
        self.preserve_mixed_language.setChecked(config.preserve_mixed_language)
        self.auto_copy_outgoing.setChecked(config.auto_copy_outgoing)
        self.auto_send_to_game.setChecked(config.auto_send_to_game)
        self.startup_delay_seconds.setValue(config.startup_delay_seconds)
        self.game_startup_grace_seconds.setValue(config.game_startup_grace_seconds)
        self.overlay_compact.setChecked(config.overlay_compact)
        self.ingame_only_mode.setChecked(config.ingame_only_mode)
        self.overlay_native_frame.setChecked(not config.overlay_borderless)
        self.overlay_remember_position.setChecked(config.overlay_remember_position)
        self.always_on_top.setChecked(config.always_on_top)
        self.overlay_opacity.setValue(config.overlay_opacity)
        self.overlay_width.setValue(config.overlay_width)
        self.overlay_height.setValue(config.overlay_height)
        self.overlay_click_through.setChecked(config.overlay_click_through)
        self._set_combo_data(self.resolution_profile, config.resolution_profile)
        self._set_combo_data(self.chat_region, config.chat_region_preset)
        self._set_combo_data(self.display_mode, config.display_mode)
        self.capture_from_game_window.setChecked(config.capture_from_game_window)
        self.capture_fullscreen_monitor.setChecked(config.capture_fullscreen_monitor)
        self.ocr_preprocess.setChecked(config.ocr_preprocess)
        self.ocr_confidence_min.setValue(config.ocr_confidence_min)
        self.capture_fps.setValue(config.capture_fps)
        self.low_cpu_mode.setChecked(config.low_cpu_mode)
        self.auto_start_monitor.setChecked(config.auto_start_monitor)
        self.player_name.setText(config.player_name)
        self.auto_detect_player.setChecked(config.auto_detect_player)
        self.d3_exe_path.setText(config.d3_exe_path)
        self.d4_exe_path.setText(config.d4_exe_path)
        self.immortal_exe_path.setText(config.immortal_exe_path)
        self._set_combo_data(self.preferred_launch_game, config.preferred_launch_game)

    @staticmethod
    def _set_combo_data(combo: QComboBox, value: str) -> None:
        index = combo.findData(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def _refresh_summary(self) -> None:
        player = self.player_name.text().strip() or "auto"
        self.summary_label.setText(
            f"Profil : {self.resolution_profile.currentText()} · "
            f"Zone {self.chat_region.currentText()} · "
            f"Joueur : {player} · "
            f"Launch : {self.preferred_launch_game.currentText()}"
        )

    def build_config(self) -> AppConfig:
        return AppConfig(
            language=self.language.currentText(),
            overlay_enabled=True,
            overlay_opacity=self.overlay_opacity.value(),
            overlay_compact=self.overlay_compact.isChecked(),
            overlay_position="bottom_left",
            overlay_width=self.overlay_width.value(),
            overlay_height=self.overlay_height.value(),
            overlay_margin=8,
            overlay_borderless=not self.overlay_native_frame.isChecked(),
            overlay_remember_position=self.overlay_remember_position.isChecked(),
            overlay_click_through=self.overlay_click_through.isChecked(),
            overlay_above_chat=True,
            always_on_top=self.always_on_top.isChecked(),
            show_only_gameplay_tab=True,
            auto_raise_on_game=False,
            auto_start_monitor=self.auto_start_monitor.isChecked(),
            capture_fps=self.capture_fps.value(),
            translator="google",
            deepl_api_key=self._config.deepl_api_key,
            ocr_engine="easyocr",
            ocr_languages="en,fr,de,es,it,pt,ru,pl",
            ocr_confidence_min=self.ocr_confidence_min.value(),
            ocr_preprocess=self.ocr_preprocess.isChecked(),
            capture_from_game_window=self.capture_from_game_window.isChecked(),
            capture_fullscreen_monitor=self.capture_fullscreen_monitor.isChecked(),
            display_mode=self.display_mode.currentData(),
            resolution_profile=self.resolution_profile.currentData(),
            ingame_only_mode=self.ingame_only_mode.isChecked(),
            player_name=self.player_name.text().strip(),
            auto_detect_player=self.auto_detect_player.isChecked(),
            auto_copy_outgoing=self.auto_copy_outgoing.isChecked(),
            auto_send_to_game=self.auto_send_to_game.isChecked(),
            startup_delay_seconds=self.startup_delay_seconds.value(),
            game_startup_grace_seconds=self.game_startup_grace_seconds.value(),
            low_cpu_mode=self.low_cpu_mode.isChecked(),
            auto_detect_language=self.auto_detect_language.isChecked(),
            bidirectional_mode=self.bidirectional_mode.isChecked(),
            default_reply_language=self.default_reply_language.currentText(),
            preserve_mixed_language=self.preserve_mixed_language.isChecked(),
            chat_monitor_enabled=True,
            chat_region_preset=self.chat_region.currentData(),
            voice_input_enabled=self._config.voice_input_enabled,
            speak_translation=self._config.speak_translation,
            voice_language=self._config.voice_language,
            ui_font_size=self._config.ui_font_size,
            cache_max_entries=self._config.cache_max_entries,
            min_text_length=self._config.min_text_length,
            d3_exe_path=self.d3_exe_path.text().strip(),
            d4_exe_path=self.d4_exe_path.text().strip(),
            immortal_exe_path=self.immortal_exe_path.text().strip(),
            preferred_launch_game=self.preferred_launch_game.currentData(),
        )

    def load_config(self, config: AppConfig) -> None:
        self._config = AppConfig(**asdict(config))
        self._sync_fields_from_config()
        self._refresh_summary()
