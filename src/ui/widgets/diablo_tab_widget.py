from __future__ import annotations

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QTabWidget, QWidget

from src.infrastructure.asset_manager import AssetManager


class DiabloTabWidget(QTabWidget):

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("DiabloIconTabWidget")
        self.setDocumentMode(True)
        tab_bar = self.tabBar()
        tab_bar.setExpanding(False)
        tab_bar.setDrawBase(False)
        tab_bar.setIconSize(QSize(22, 22))

    def add_icon_tab(self, widget: QWidget, icon_name: str, tooltip: str) -> int:
        index = self.addTab(widget, AssetManager.icon(icon_name), "")
        self.setTabToolTip(index, tooltip)
        return index
