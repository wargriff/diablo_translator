from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from src.infrastructure.config_manager import ConfigManager
from src.infrastructure.container import Container
from src.ui.services.diagnostic_service import DiagnosticService
from src.ui.widgets.settings_form_widget import SettingsFormWidget


class SettingsTabWidget(QWidget):

    settings_applied = pyqtSignal()

    def __init__(self, container: Container, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("SettingsTabRoot")
        self.container = container
        self._diagnostics = DiagnosticService.instance()

        self.form = SettingsFormWidget(container.config, parent=self)

        self.save_button = QPushButton(" Enregistrer")
        self.save_button.setObjectName("PrimaryButton")
        self.save_button.clicked.connect(self._save)

        self.reload_button = QPushButton(" Recharger")
        self.reload_button.clicked.connect(self._reload)

        actions = QHBoxLayout()
        actions.addWidget(self.save_button)
        actions.addWidget(self.reload_button)
        actions.addStretch()

        layout = QVBoxLayout()
        layout.addWidget(self.form, stretch=1)
        layout.addLayout(actions)
        self.setLayout(layout)

    def _save(self) -> None:
        updated = self.form.build_config()
        self.container.apply_config(updated)
        ConfigManager.save(updated)
        self._diagnostics.record("Réglages", "Paramètres enregistrés", level="info")
        self.settings_applied.emit()

    def _reload(self) -> None:
        self.form.load_config(self.container.config)

    def reload_from_container(self) -> None:
        self._reload()
