from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLineEdit,
    QSpinBox,
)

from src.chat.chat_region import CHAT_REGION_PRESETS
from src.infrastructure import AppConfig, ConfigManager
from src.translation.providers.registry import TranslatorRegistry


class SettingsDialog(QDialog):

    def __init__(self, config: AppConfig, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Paramètres — Diablo Translator")

        self.language = QComboBox()
        self.language.addItems(["fr", "en", "de", "es", "it"])
        self.language.setCurrentText(config.language)

        self.translator = QComboBox()
        self.translator.addItems(TranslatorRegistry.available())
        self.translator.setCurrentText(config.translator)

        self.deepl_api_key = QLineEdit(config.deepl_api_key)
        self.deepl_api_key.setPlaceholderText("Clé API DeepL (ou .env)")
        self.deepl_api_key.setEchoMode(QLineEdit.EchoMode.Password)

        self.ocr_languages = QLineEdit(config.ocr_languages)
        self.ocr_languages.setPlaceholderText("en,fr,de,es")

        self.capture_fps = QSpinBox()
        self.capture_fps.setRange(1, 10)
        self.capture_fps.setValue(config.capture_fps)

        self.chat_region = QComboBox()
        for preset in CHAT_REGION_PRESETS:
            self.chat_region.addItem(preset.title, preset.key)
        index = self.chat_region.findData(config.chat_region_preset)
        if index >= 0:
            self.chat_region.setCurrentIndex(index)

        self.auto_detect_language = QCheckBox()
        self.auto_detect_language.setChecked(config.auto_detect_language)

        self.chat_monitor_enabled = QCheckBox()
        self.chat_monitor_enabled.setChecked(config.chat_monitor_enabled)

        self.voice_input_enabled = QCheckBox()
        self.voice_input_enabled.setChecked(config.voice_input_enabled)

        self.speak_translation = QCheckBox()
        self.speak_translation.setChecked(config.speak_translation)

        self.overlay_enabled = QCheckBox()
        self.overlay_enabled.setChecked(config.overlay_enabled)

        self.overlay_opacity = QDoubleSpinBox()
        self.overlay_opacity.setRange(0.1, 1.0)
        self.overlay_opacity.setSingleStep(0.05)
        self.overlay_opacity.setValue(config.overlay_opacity)

        self.low_cpu_mode = QCheckBox()
        self.low_cpu_mode.setChecked(config.low_cpu_mode)

        form = QFormLayout()
        form.addRow("Langue cible", self.language)
        form.addRow("Moteur de traduction", self.translator)
        form.addRow("Clé API DeepL", self.deepl_api_key)
        form.addRow("Langues OCR", self.ocr_languages)
        form.addRow("Zone chat", self.chat_region)
        form.addRow("FPS capture chat", self.capture_fps)
        form.addRow("Détection auto langue", self.auto_detect_language)
        form.addRow("Surveiller chat en direct", self.chat_monitor_enabled)
        form.addRow("Entrée vocale", self.voice_input_enabled)
        form.addRow("Lire traduction à voix haute", self.speak_translation)
        form.addRow("Overlay activé", self.overlay_enabled)
        form.addRow("Opacité overlay", self.overlay_opacity)
        form.addRow("Mode CPU réduit", self.low_cpu_mode)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        form.addRow(buttons)
        self.setLayout(form)

    def build_config(self) -> AppConfig:
        return AppConfig(
            language=self.language.currentText(),
            overlay_enabled=self.overlay_enabled.isChecked(),
            overlay_opacity=self.overlay_opacity.value(),
            capture_fps=self.capture_fps.value(),
            translator=self.translator.currentText(),
            deepl_api_key=self.deepl_api_key.text().strip(),
            ocr_engine="easyocr",
            ocr_languages=self.ocr_languages.text().strip() or "en,fr,de,es",
            low_cpu_mode=self.low_cpu_mode.isChecked(),
            auto_detect_language=self.auto_detect_language.isChecked(),
            chat_monitor_enabled=self.chat_monitor_enabled.isChecked(),
            chat_region_preset=self.chat_region.currentData(),
            voice_input_enabled=self.voice_input_enabled.isChecked(),
            speak_translation=self.speak_translation.isChecked(),
        )

    @classmethod
    def edit(cls, config: AppConfig, parent=None) -> AppConfig | None:
        dialog = cls(config, parent=parent)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None

        updated = dialog.build_config()
        ConfigManager.save(updated)
        return updated
