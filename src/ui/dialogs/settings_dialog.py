from __future__ import annotations

from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout

from src.infrastructure import AppConfig, ConfigManager
from src.infrastructure.asset_manager import AssetManager
from src.ui.widgets.settings_form_widget import SettingsFormWidget


class SettingsDialog(QDialog):

    def __init__(self, config: AppConfig, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Sanctuaire des Paramètres")
        self.resize(860, 620)
        self.setObjectName("SettingsDialog")
        AssetManager.apply_window_branding(self)

        header = QLabel("SANCTUAIRE DES PARAMÈTRES")
        header.setObjectName("AppTitle")
        header.setFont(AssetManager.ui_font(20, bold=True))

        subtitle = QLabel(
            "Profils calibrés · Overlay · OCR · Chemins exe Diablo"
        )
        subtitle.setObjectName("AppSubtitle")

        self.form = SettingsFormWidget(config, parent=self)

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
        layout.addWidget(self.form, stretch=1)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def build_config(self) -> AppConfig:
        return self.form.build_config()

    @classmethod
    def edit(cls, config: AppConfig, parent=None) -> AppConfig | None:
        dialog = cls(config, parent=parent)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None

        updated = dialog.build_config()
        ConfigManager.save(updated)
        return updated
