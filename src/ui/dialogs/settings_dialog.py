from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QSpinBox,
)

from src.infrastructure import AppConfig, ConfigManager


class SettingsDialog(QDialog):

    def __init__(self, config: AppConfig, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Paramètres — Diablo Translator")

        self.language = QComboBox()
        self.language.addItems(["fr", "en", "de", "es", "it"])
        self.language.setCurrentText(config.language)

        self.capture_fps = QSpinBox()
        self.capture_fps.setRange(1, 10)
        self.capture_fps.setValue(config.capture_fps)

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
        form.addRow("FPS capture", self.capture_fps)
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
            translator="google",
            ocr_engine="easyocr",
            low_cpu_mode=self.low_cpu_mode.isChecked(),
        )

    @classmethod
    def edit(cls, config: AppConfig, parent=None) -> AppConfig | None:
        dialog = cls(config, parent=parent)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None

        updated = dialog.build_config()
        ConfigManager.save(updated)
        return updated
