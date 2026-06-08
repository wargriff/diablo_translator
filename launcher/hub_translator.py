from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from launcher.hub_workers import HubTranslateWorker

HUB_LANGUAGES = (
    ("fr", "Français"),
    ("en", "English"),
    ("de", "Deutsch"),
    ("es", "Español"),
    ("it", "Italiano"),
    ("pt", "Português"),
    ("ru", "Русский"),
    ("pl", "Polski"),
)


class HubTranslatorPanel(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("HubTranslatorPanel")
        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.timeout.connect(self._run_translation)
        self._status_callback = None
        self._worker: HubTranslateWorker | None = None
        self._request_id = 0
        self._build_ui()
        self._load_defaults()

    def set_status_callback(self, callback) -> None:
        self._status_callback = callback

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("Traduction")
        title.setObjectName("AppTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle = QLabel("Comme DeepL — choisissez les langues et inversez avec ⇄")
        subtitle.setObjectName("MutedText")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        layout.addWidget(subtitle)

        lang_row = QHBoxLayout()
        lang_row.addStretch()
        self._source_lang = QComboBox()
        self._source_lang.setObjectName("HubLangCombo")
        self._swap = QPushButton("⇄")
        self._swap.setObjectName("HubSwapButton")
        self._swap.setFixedSize(44, 44)
        self._swap.clicked.connect(self._swap_languages)
        self._target_lang = QComboBox()
        self._target_lang.setObjectName("HubLangCombo")
        for code, label in HUB_LANGUAGES:
            self._source_lang.addItem(label, code)
            self._target_lang.addItem(label, code)
        lang_row.addWidget(self._source_lang)
        lang_row.addWidget(self._swap)
        lang_row.addWidget(self._target_lang)
        lang_row.addStretch()
        layout.addLayout(lang_row)

        texts = QHBoxLayout()
        self._source_text = QTextEdit()
        self._source_text.setObjectName("HubSourceEdit")
        self._source_text.setPlaceholderText("Tapez votre message…")
        self._source_text.setMinimumHeight(220)
        self._target_text = QTextEdit()
        self._target_text.setObjectName("HubTargetEdit")
        self._target_text.setPlaceholderText("Traduction…")
        self._target_text.setReadOnly(True)
        self._target_text.setMinimumHeight(220)
        texts.addWidget(self._source_text)
        texts.addWidget(self._target_text)
        layout.addLayout(texts)

        actions = QHBoxLayout()
        actions.addStretch()
        copy_btn = QPushButton("Copier")
        copy_btn.setObjectName("HubPillButton")
        copy_btn.clicked.connect(self._copy_result)
        save_btn = QPushButton("Enregistrer")
        save_btn.setObjectName("HubPrimaryPill")
        save_btn.clicked.connect(self._save_history)
        clear_btn = QPushButton("Effacer")
        clear_btn.setObjectName("HubPillButton")
        clear_btn.clicked.connect(self._clear)
        actions.addWidget(copy_btn)
        actions.addWidget(save_btn)
        actions.addWidget(clear_btn)
        actions.addStretch()
        layout.addLayout(actions)

        self._source_text.textChanged.connect(self._schedule_translation)
        self._source_lang.currentIndexChanged.connect(self._schedule_translation)
        self._target_lang.currentIndexChanged.connect(self._schedule_translation)

    def _load_defaults(self) -> None:
        try:
            from src.infrastructure.config_manager import ConfigManager

            config = ConfigManager.load()
            self._set_combo_code(self._source_lang, config.language)
            self._set_combo_code(self._target_lang, config.default_reply_language)
        except Exception:
            self._set_combo_code(self._source_lang, "fr")
            self._set_combo_code(self._target_lang, "en")

    @staticmethod
    def _set_combo_code(combo: QComboBox, code: str) -> None:
        index = combo.findData(code)
        if index >= 0:
            combo.setCurrentIndex(index)

    def _schedule_translation(self) -> None:
        self._debounce.start(350)

    def _run_translation(self) -> None:
        text = self._source_text.toPlainText().strip()
        if not text:
            self._target_text.clear()
            return

        if self._worker is not None and self._worker.isRunning():
            self._worker.requestInterruption()
            self._worker.wait(50)

        self._request_id += 1
        request_id = self._request_id
        source = str(self._source_lang.currentData())
        target = str(self._target_lang.currentData())

        worker = HubTranslateWorker(text, source, target, self)
        worker.finished.connect(
            lambda translated, rid=request_id: self._on_translated(rid, translated)
        )
        worker.failed.connect(
            lambda message, rid=request_id: self._on_translate_failed(rid, message)
        )
        worker.finished.connect(worker.deleteLater)
        worker.failed.connect(worker.deleteLater)
        self._worker = worker
        worker.start()

    def _on_translated(self, request_id: int, translated: str) -> None:
        if request_id != self._request_id:
            return
        self._target_text.setPlainText(translated)

    def _on_translate_failed(self, request_id: int, message: str) -> None:
        if request_id != self._request_id:
            return
        self._target_text.clear()
        self._emit_status(message)

    def _swap_languages(self) -> None:
        self._source_lang.blockSignals(True)
        self._target_lang.blockSignals(True)
        source_index = self._source_lang.currentIndex()
        target_index = self._target_lang.currentIndex()
        self._source_lang.setCurrentIndex(target_index)
        self._target_lang.setCurrentIndex(source_index)
        self._source_lang.blockSignals(False)
        self._target_lang.blockSignals(False)

        source_text = self._source_text.toPlainText()
        target_text = self._target_text.toPlainText()
        if target_text.strip():
            self._source_text.setPlainText(target_text)
            self._target_text.setPlainText(source_text)
        self._schedule_translation()

    def _copy_result(self) -> None:
        text = self._target_text.toPlainText().strip()
        if not text:
            return
        QGuiApplication.clipboard().setText(text)
        self._emit_status("Traduction copiée")

    def _save_history(self) -> None:
        if not self._source_text.toPlainText().strip():
            return
        self._run_translation()
        self._emit_status("Enregistré dans l'historique")

    def _clear(self) -> None:
        self._request_id += 1
        self._source_text.clear()
        self._target_text.clear()

    def _emit_status(self, message: str) -> None:
        if self._status_callback:
            self._status_callback(message)
