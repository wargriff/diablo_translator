from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.game_detection import SUPPORTED_GAMES
from src.infrastructure.asset_manager import AssetManager
from src.infrastructure.container import Container
from src.ui.services.diagnostic_service import DiagnosticService


class LaunchTabWidget(QWidget):

    launch_requested = pyqtSignal(str)
    refresh_requested = pyqtSignal()
    open_settings_requested = pyqtSignal()

    def __init__(self, container: Container, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("LaunchTabRoot")
        self.container = container
        self._diagnostics = DiagnosticService.instance()
        self._cards: dict[str, dict[str, QWidget]] = {}

        title = QLabel("LAUNCHER DIABLO")
        title.setObjectName("AppTitle")
        title.setFont(AssetManager.ui_font(16, bold=True))

        subtitle = QLabel(
            "Lancez Diablo III, Diablo IV ou Diablo Immortal depuis leurs exe configurés."
        )
        subtitle.setObjectName("MutedText")
        subtitle.setWordWrap(True)

        self.hint_label = QLabel("")
        self.hint_label.setObjectName("MutedText")
        self.hint_label.setWordWrap(True)

        preferred = container.game_launcher.preferred_game_key()
        preferred_game = next(game for game in SUPPORTED_GAMES if game.key == preferred)

        self.hero_button = QPushButton(f" Lancer {preferred_game.title}")
        self.hero_button.setObjectName("LaunchDiabloButton")
        self.hero_button.setIcon(AssetManager.app_icon())
        self.hero_button.clicked.connect(self._launch_preferred)

        grid = QGridLayout()
        grid.setSpacing(10)
        for index, game in enumerate(SUPPORTED_GAMES):
            card = self._build_game_card(game.key, game.title, game.short_title)
            grid.addWidget(card, index // 2, index % 2)

        actions = QHBoxLayout()
        refresh_button = QPushButton(" Actualiser statut")
        refresh_button.setIcon(AssetManager.icon("play"))
        refresh_button.clicked.connect(self.refresh_status)

        settings_button = QPushButton(" Réglages exe")
        settings_button.setIcon(AssetManager.icon("settings"))
        settings_button.clicked.connect(self.open_settings_requested.emit)

        actions.addWidget(refresh_button)
        actions.addWidget(settings_button)
        actions.addStretch()

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.hint_label)
        layout.addWidget(self.hero_button, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addLayout(grid)
        layout.addLayout(actions)
        layout.addStretch()
        self.setLayout(layout)

        self.refresh_status()

    def _build_game_card(self, game_key: str, title: str, short_title: str) -> QFrame:
        card = QFrame()
        card.setObjectName("GameCard")

        title_label = QLabel(title)
        title_label.setObjectName("SectionTitle")

        status_label = QLabel("Hors ligne")
        status_label.setObjectName("StatusOffline")

        path_label = QLabel("Exe : non configuré")
        path_label.setObjectName("MutedText")
        path_label.setWordWrap(True)

        launch_button = QPushButton(f" Lancer {short_title}")
        launch_button.setObjectName("LaunchGameButton")
        launch_button.setIcon(AssetManager.icon("launch"))
        launch_button.clicked.connect(lambda _checked=False, key=game_key: self._launch(key))

        browse_button = QPushButton(" Exe…")
        browse_button.setObjectName("CompactOcrButton")
        browse_button.clicked.connect(lambda _checked=False, key=game_key: self._browse_exe(key))

        prefer_button = QPushButton(" Favori")
        prefer_button.setObjectName("CompactOcrButton")
        prefer_button.setToolTip("Utiliser ce jeu pour le bouton hero")
        prefer_button.clicked.connect(lambda _checked=False, key=game_key: self._set_preferred(key))

        row = QHBoxLayout()
        row.addWidget(launch_button)
        row.addWidget(browse_button)
        row.addWidget(prefer_button)

        card_layout = QVBoxLayout()
        card_layout.addWidget(title_label)
        card_layout.addWidget(status_label)
        card_layout.addWidget(path_label)
        card_layout.addLayout(row)
        card.setLayout(card_layout)

        self._cards[game_key] = {
            "card": card,
            "status": status_label,
            "path": path_label,
            "launch": launch_button,
        }
        return card

    def _browse_exe(self, game_key: str) -> None:
        current = self.container.game_launcher.resolve_path(game_key)
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir l’exe Diablo",
            current or "",
            "Executables (*.exe);;Tous (*.*)",
        )
        if not path:
            return

        self.container.game_launcher.save_path(game_key, path)
        self._diagnostics.record(
            "Launch",
            f"Chemin enregistré pour {game_key} : {path}",
            level="info",
        )
        self.refresh_status()

    def _set_preferred(self, game_key: str) -> None:
        self.container.game_launcher.set_preferred_game(game_key)
        game = next(item for item in SUPPORTED_GAMES if item.key == game_key)
        self.hero_button.setText(f" Lancer {game.title}")
        self._diagnostics.record(
            "Launch",
            f"Jeu favori : {game.title}",
            level="info",
        )

    def _launch_preferred(self) -> None:
        ok, message = self.container.game_launcher.launch_preferred()
        self._report_launch(message, ok=ok)
        if ok:
            self.refresh_requested.emit()

    def _launch(self, game_key: str) -> None:
        ok, message = self.container.game_launcher.launch(game_key)
        self._report_launch(message, ok=ok)
        if ok:
            self.launch_requested.emit(game_key)
            self.refresh_requested.emit()

    def _report_launch(self, message: str, *, ok: bool) -> None:
        level = "info" if ok else "error"
        self._diagnostics.record("Launch", message, level=level)
        self.hint_label.setText(message)

    def refresh_status(self) -> None:
        state = self.container.game_launch.tick(force=True)
        summary = state.snapshot.status.summary()
        self._diagnostics.set_game(
            "ON" if state.snapshot.status.is_any_running else "OFF"
        )

        for game in SUPPORTED_GAMES:
            info = self.container.game_launcher.game_status(game.key)
            widgets = self._cards[game.key]
            card = widgets["card"]
            status_label = widgets["status"]
            path_label = widgets["path"]

            running = bool(info["running"])
            card.setProperty("running", running)
            card.style().unpolish(card)
            card.style().polish(card)

            if running:
                status_label.setText(f"En ligne ({info['process']})")
                status_label.setObjectName("StatusOnline")
            else:
                status_label.setText("Hors ligne")
                status_label.setObjectName("StatusOffline")
            status_label.style().unpolish(status_label)
            status_label.style().polish(status_label)

            path = str(info["path"] or "")
            if not path:
                path_label.setText("Exe : non configuré — cliquez Exe…")
            elif info["path_valid"]:
                path_label.setText(f"Exe : {path}")
            else:
                path_label.setText(f"Exe invalide : {path}")

        preferred = self.container.game_launcher.preferred_game_key()
        preferred_game = next(game for game in SUPPORTED_GAMES if game.key == preferred)
        self.hero_button.setText(f" Lancer {preferred_game.title}")

        if state.hint:
            self.hint_label.setText(state.hint)
        elif state.snapshot.status.is_any_running:
            self.hint_label.setText(summary)
        else:
            self.hint_label.setText(
                "Choisissez un jeu ci-dessous ou configurez les chemins exe."
            )
