from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal


class UiThreadBridge(QObject):

    voice_text = pyqtSignal(str)
    translation_result = pyqtSignal(object)
    agent_log_payload = pyqtSignal(object)
