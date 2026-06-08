from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from dataclasses import asdict

from src.application.config_profiles import PROFILE_CATALOG
from src.chat.chat_region import CHAT_REGION_PRESETS
from src.infrastructure import AppConfig, ConfigManager
from src.infrastructure.asset_manager import AssetManager


class SettingsDialog(QDialog):

    SIDEBAR_ITEMS = (
        ("profiles", "Profils Pro"),
        ("translation", "Traduction"),
        ("overlay", "Overlay"),
        ("ocr", "OCR Diablo"),
        ("identity", "Identité Joueur"),
    )

    def __init__(self, config: AppConfig, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Sanctuaire des Paramètres")
        self.resize(860, 620)
        self.setObjectName("SettingsDialog")
        AssetManager.apply_window_branding(self)

        self._config = AppConfig(**asdict(config))
        self._build_fields()
        self._build_ui()

    def _build_ui(self) -> None:
        header = QLabel("SANCTUAIRE DES PARAMÈTRES")
        header.setObjectName("AppTitle")
        header.setFont(AssetManager.ui_font(20, bold=True))

        subtitle = QLabel(
            "Profils calibrés · 1080p plein écran · Traduction 100% depuis Diablo III"
        )
        subtitle.setObjectName("AppSubtitle")

        self.summary_label = QLabel()
        self.summary_label.setObjectName("MutedText")
        self.summary_label.setWordWrap(True)
        self._refresh_summary()

        self.sidebar = QListWidget()
        self.sidebar.setObjectName("SettingsSidebar")
        self.sidebar.setFixedWidth(190)
        for key, label in self.SIDEBAR_ITEMS:
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, key)
            self.sidebar.addItem(item)
        self.sidebar.currentRowChanged.connect(self._switch_page)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._wrap_scroll(self._build_profiles_page()))
        self.stack.addWidget(self._wrap_scroll(self._build_translation_page()))
        self.stack.addWidget(self._wrap_scroll(self._build_overlay_page()))
        self.stack.addWidget(self._wrap_scroll(self._build_ocr_page()))
        self.stack.addWidget(self._wrap_scroll(self._build_identity_page()))

        body = QHBoxLayout()
        body.addWidget(self.sidebar)
        body.addWidget(self.stack, stretch=1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.addWidget(header)
        layout.addWidget(subtitle)
        layout.addWidget(self.summary_label)
        layout.addLayout(body)
        layout.addWidget(buttons)
        self.setLayout(layout)

        self.sidebar.setCurrentRow(0)

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
            "Choisis un profil pro pré-calibré. Le profil Ultimate D3 1080p est "
            "optimisé pour Diablo III en plein écran 1920×1080 : OCR chat, overlay, "
            "traduction automatique depuis le jeu (sans taper dans l'appli)."
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
        title_label.setFont(AssetManager.ui_font(12, bold=True))

        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("MutedText")
        subtitle_label.setWordWrap(True)

        button = QPushButton(" Activer ce profil")
        button.setObjectName("PrimaryButton")
        button.setIcon(AssetManager.icon("settings"))
        button.clicked.connect(lambda: self._apply_profile(profile_key))

        layout = QVBoxLayout()
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignLeft)
        card.setLayout(layout)
        return card

    def _apply_profile(self, profile_key: str) -> None:
        meta = PROFILE_CATALOG[profile_key]
        self._config = meta["apply"](self._config)
        self._sync_fields_from_config()
        self._refresh_summary()

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

    def _build_identity_page(self) -> QWidget:
        form = QFormLayout()
        form.addRow("Nom de personnage Diablo III", self.player_name)
        form.addRow("Détecter mon nom automatiquement", self.auto_detect_player)
        hint = QLabel(
            "Laisse vide pour auto-détection : quand tu écris en français dans le chat "
            "Diablo, l'appli apprend ton pseudo et traduit tes messages automatiquement."
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
        self.language.currentTextChanged.connect(self._refresh_summary)

        self.bidirectional_mode = QCheckBox()
        self.default_reply_language = QComboBox()
        self.default_reply_language.addItems(["en", "de", "es", "it", "pt", "ru", "pl"])
        self.auto_detect_language = QCheckBox()
        self.preserve_mixed_language = QCheckBox()
        self.auto_copy_outgoing = QCheckBox()
        self.auto_send_to_game = QCheckBox()
        self.startup_delay_seconds = QSpinBox()
        self.startup_delay_seconds.setRange(1, 15)

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

        self._sync_fields_from_config()

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

    @staticmethod
    def _set_combo_data(combo: QComboBox, value: str) -> None:
        index = combo.findData(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def _refresh_summary(self) -> None:
        player = self.player_name.text().strip() or "auto"
        self.summary_label.setText(
            f"Profil actif : {self.resolution_profile.currentText()} · "
            f"Zone {self.chat_region.currentText()} · "
            f"Joueur : {player} · "
            f"Mode in-game : {'ON' if self.ingame_only_mode.isChecked() else 'OFF'}"
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
            low_cpu_mode=self.low_cpu_mode.isChecked(),
            auto_detect_language=self.auto_detect_language.isChecked(),
            bidirectional_mode=self.bidirectional_mode.isChecked(),
            default_reply_language=self.default_reply_language.currentText(),
            preserve_mixed_language=self.preserve_mixed_language.isChecked(),
            chat_monitor_enabled=True,
            chat_region_preset=self.chat_region.currentData(),
            voice_input_enabled=False,
            speak_translation=False,
            voice_language="auto",
            ui_font_size=10,
            cache_max_entries=2000,
            min_text_length=2,
        )

    @classmethod
    def edit(cls, config: AppConfig, parent=None) -> AppConfig | None:
        dialog = cls(config, parent=parent)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None

        updated = dialog.build_config()
        ConfigManager.save(updated)
        return updated
