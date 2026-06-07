from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.chat.chat_region import CHAT_REGION_PRESETS
from src.infrastructure import AppConfig, ConfigManager
from src.translation.providers.registry import TranslatorRegistry


class SettingsDialog(QDialog):

    def __init__(self, config: AppConfig, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Paramètres — Diablo Translator")
        self.resize(560, 620)

        self._config = config
        self._build_fields()

        tabs = QTabWidget()
        tabs.addTab(self._build_general_tab(), "Général")
        tabs.addTab(self._build_overlay_tab(), "Overlay / Jeu")
        tabs.addTab(self._build_translation_tab(), "Traduction")
        tabs.addTab(self._build_ocr_tab(), "OCR & Chat")
        tabs.addTab(self._build_voice_tab(), "Voix & UI")

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(tabs)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def _build_fields(self) -> None:
        config = self._config

        self.language = QComboBox()
        self.language.addItems(["fr", "en", "de", "es", "it", "pt", "ru"])
        self.language.setCurrentText(config.language)

        self.translator = QComboBox()
        self.translator.addItems(TranslatorRegistry.available())
        self.translator.setCurrentText(config.translator)

        self.deepl_api_key = QLineEdit(config.deepl_api_key)
        self.deepl_api_key.setEchoMode(QLineEdit.EchoMode.Password)

        self.auto_detect_language = QCheckBox()
        self.auto_detect_language.setChecked(config.auto_detect_language)

        self.auto_start_monitor = QCheckBox()
        self.auto_start_monitor.setChecked(config.auto_start_monitor)

        self.always_on_top = QCheckBox()
        self.always_on_top.setChecked(config.always_on_top)

        self.overlay_enabled = QCheckBox()
        self.overlay_enabled.setChecked(config.overlay_enabled)

        self.overlay_compact = QCheckBox()
        self.overlay_compact.setChecked(config.overlay_compact)

        self.overlay_opacity = QDoubleSpinBox()
        self.overlay_opacity.setRange(0.25, 1.0)
        self.overlay_opacity.setSingleStep(0.05)
        self.overlay_opacity.setValue(config.overlay_opacity)

        self.overlay_position = QComboBox()
        self.overlay_position.addItem("Haut droite", "top_right")
        self.overlay_position.addItem("Haut gauche", "top_left")
        self.overlay_position.addItem("Bas droite", "bottom_right")
        self.overlay_position.addItem("Bas gauche", "bottom_left")
        self.overlay_position.addItem("Centre droite", "center_right")
        index = self.overlay_position.findData(config.overlay_position)
        if index >= 0:
            self.overlay_position.setCurrentIndex(index)

        self.overlay_width = QSpinBox()
        self.overlay_width.setRange(320, 900)
        self.overlay_width.setValue(config.overlay_width)

        self.overlay_height = QSpinBox()
        self.overlay_height.setRange(360, 1200)
        self.overlay_height.setValue(config.overlay_height)

        self.overlay_margin = QSpinBox()
        self.overlay_margin.setRange(0, 120)
        self.overlay_margin.setValue(config.overlay_margin)

        self.overlay_borderless = QCheckBox()
        self.overlay_borderless.setChecked(config.overlay_borderless)

        self.overlay_click_through = QCheckBox()
        self.overlay_click_through.setChecked(config.overlay_click_through)

        self.show_only_gameplay_tab = QCheckBox()
        self.show_only_gameplay_tab.setChecked(config.show_only_gameplay_tab)

        self.auto_raise_on_game = QCheckBox()
        self.auto_raise_on_game.setChecked(config.auto_raise_on_game)

        self.ocr_languages = QLineEdit(config.ocr_languages)
        self.ocr_confidence_min = QDoubleSpinBox()
        self.ocr_confidence_min.setRange(0.1, 0.95)
        self.ocr_confidence_min.setSingleStep(0.05)
        self.ocr_confidence_min.setValue(config.ocr_confidence_min)

        self.chat_region = QComboBox()
        for preset in CHAT_REGION_PRESETS:
            self.chat_region.addItem(preset.title, preset.key)
        region_index = self.chat_region.findData(config.chat_region_preset)
        if region_index >= 0:
            self.chat_region.setCurrentIndex(region_index)

        self.capture_fps = QSpinBox()
        self.capture_fps.setRange(1, 10)
        self.capture_fps.setValue(config.capture_fps)

        self.chat_monitor_enabled = QCheckBox()
        self.chat_monitor_enabled.setChecked(config.chat_monitor_enabled)

        self.min_text_length = QSpinBox()
        self.min_text_length.setRange(1, 20)
        self.min_text_length.setValue(config.min_text_length)

        self.low_cpu_mode = QCheckBox()
        self.low_cpu_mode.setChecked(config.low_cpu_mode)

        self.voice_input_enabled = QCheckBox()
        self.voice_input_enabled.setChecked(config.voice_input_enabled)

        self.speak_translation = QCheckBox()
        self.speak_translation.setChecked(config.speak_translation)

        self.voice_language = QComboBox()
        self.voice_language.addItem("Auto (langue cible)", "auto")
        self.voice_language.addItem("Français", "fr-FR")
        self.voice_language.addItem("English", "en-US")
        self.voice_language.addItem("Deutsch", "de-DE")
        self.voice_language.addItem("Español", "es-ES")
        voice_index = self.voice_language.findData(config.voice_language)
        if voice_index >= 0:
            self.voice_language.setCurrentIndex(voice_index)

        self.ui_font_size = QSpinBox()
        self.ui_font_size.setRange(8, 18)
        self.ui_font_size.setValue(config.ui_font_size)

        self.cache_max_entries = QSpinBox()
        self.cache_max_entries.setRange(500, 20000)
        self.cache_max_entries.setValue(config.cache_max_entries)

    def _build_general_tab(self) -> QWidget:
        form = QFormLayout()
        form.addRow("Langue cible", self.language)
        form.addRow("Démarrer surveillance auto", self.auto_start_monitor)
        form.addRow("Mode CPU réduit", self.low_cpu_mode)
        form.addRow("Taille police UI", self.ui_font_size)
        form.addRow("Entrées cache max", self.cache_max_entries)
        widget = QWidget()
        widget.setLayout(form)
        return widget

    def _build_overlay_tab(self) -> QWidget:
        form = QFormLayout()
        form.addRow("Toujours devant le jeu", self.always_on_top)
        form.addRow("Overlay activé", self.overlay_enabled)
        form.addRow("Mode compact (jeu)", self.overlay_compact)
        form.addRow("Opacité fenêtre", self.overlay_opacity)
        form.addRow("Position overlay", self.overlay_position)
        form.addRow("Largeur overlay", self.overlay_width)
        form.addRow("Hauteur overlay", self.overlay_height)
        form.addRow("Marge écran", self.overlay_margin)
        form.addRow("Sans bordure", self.overlay_borderless)
        form.addRow("Clics traversants", self.overlay_click_through)
        form.addRow("Onglet Gameplay seul", self.show_only_gameplay_tab)
        form.addRow("Remonter si jeu actif", self.auto_raise_on_game)
        widget = QWidget()
        widget.setLayout(form)
        return widget

    def _build_translation_tab(self) -> QWidget:
        form = QFormLayout()
        form.addRow("Moteur", self.translator)
        form.addRow("Clé API DeepL", self.deepl_api_key)
        form.addRow("Détection auto langue", self.auto_detect_language)
        widget = QWidget()
        widget.setLayout(form)
        return widget

    def _build_ocr_tab(self) -> QWidget:
        form = QFormLayout()
        form.addRow("Langues OCR", self.ocr_languages)
        form.addRow("Confiance OCR min.", self.ocr_confidence_min)
        form.addRow("Zone chat", self.chat_region)
        form.addRow("FPS capture chat", self.capture_fps)
        form.addRow("Surveiller chat live", self.chat_monitor_enabled)
        form.addRow("Longueur texte min.", self.min_text_length)
        widget = QWidget()
        widget.setLayout(form)
        return widget

    def _build_voice_tab(self) -> QWidget:
        form = QFormLayout()
        form.addRow("Entrée vocale", self.voice_input_enabled)
        form.addRow("Lire traductions", self.speak_translation)
        form.addRow("Langue micro", self.voice_language)
        widget = QWidget()
        widget.setLayout(form)
        return widget

    def build_config(self) -> AppConfig:
        return AppConfig(
            language=self.language.currentText(),
            overlay_enabled=self.overlay_enabled.isChecked(),
            overlay_opacity=self.overlay_opacity.value(),
            overlay_compact=self.overlay_compact.isChecked(),
            overlay_position=self.overlay_position.currentData(),
            overlay_width=self.overlay_width.value(),
            overlay_height=self.overlay_height.value(),
            overlay_margin=self.overlay_margin.value(),
            overlay_borderless=self.overlay_borderless.isChecked(),
            overlay_click_through=self.overlay_click_through.isChecked(),
            always_on_top=self.always_on_top.isChecked(),
            show_only_gameplay_tab=self.show_only_gameplay_tab.isChecked(),
            auto_raise_on_game=self.auto_raise_on_game.isChecked(),
            auto_start_monitor=self.auto_start_monitor.isChecked(),
            capture_fps=self.capture_fps.value(),
            translator=self.translator.currentText(),
            deepl_api_key=self.deepl_api_key.text().strip(),
            ocr_engine="easyocr",
            ocr_languages=self.ocr_languages.text().strip() or "en,fr,de,es",
            ocr_confidence_min=self.ocr_confidence_min.value(),
            low_cpu_mode=self.low_cpu_mode.isChecked(),
            auto_detect_language=self.auto_detect_language.isChecked(),
            chat_monitor_enabled=self.chat_monitor_enabled.isChecked(),
            chat_region_preset=self.chat_region.currentData(),
            voice_input_enabled=self.voice_input_enabled.isChecked(),
            speak_translation=self.speak_translation.isChecked(),
            voice_language=self.voice_language.currentData(),
            ui_font_size=self.ui_font_size.value(),
            cache_max_entries=self.cache_max_entries.value(),
            min_text_length=self.min_text_length.value(),
        )

    @classmethod
    def edit(cls, config: AppConfig, parent=None) -> AppConfig | None:
        dialog = cls(config, parent=parent)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None

        updated = dialog.build_config()
        ConfigManager.save(updated)
        return updated
