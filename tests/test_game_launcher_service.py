from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.application.config_service import ConfigService
from src.application.game_launcher_service import GameLauncherService
from src.infrastructure.config_manager import AppConfig, ConfigManager


class GameLauncherServiceTests(unittest.TestCase):

    def _service(self, **overrides) -> GameLauncherService:
        config = AppConfig(**overrides)
        config_service = ConfigService()
        config_service.replace(config)
        return GameLauncherService(config_service)

    def test_validate_path_rejects_missing_config(self) -> None:
        service = self._service()
        ok, message = service.validate_path("d4")
        self.assertFalse(ok)
        self.assertIn("non configuré", message)

    def test_validate_path_accepts_existing_file(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as handle:
            path = handle.name

        try:
            service = self._service(d4_exe_path=path)
            ok, message = service.validate_path("d4")
            self.assertTrue(ok)
            self.assertEqual(message, "")
        finally:
            Path(path).unlink(missing_ok=True)

    def test_launch_calls_subprocess_with_exe_directory(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as handle:
            path = Path(handle.name)

        try:
            service = self._service(d4_exe_path=str(path))
            with patch("src.application.game_launcher_service.subprocess.Popen") as popen:
                popen.return_value = MagicMock()
                ok, message = service.launch("d4")

            self.assertTrue(ok)
            popen.assert_called_once_with(
                [str(path)],
                cwd=str(path.parent),
                shell=False,
            )
            self.assertIn("Diablo IV", message)
        finally:
            path.unlink(missing_ok=True)

    def test_launch_preferred_uses_config(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as handle:
            path = Path(handle.name)

        try:
            service = self._service(
                d3_exe_path=str(path),
                preferred_launch_game="d3",
            )
            with patch("src.application.game_launcher_service.subprocess.Popen") as popen:
                popen.return_value = MagicMock()
                ok, _ = service.launch_preferred()

            self.assertTrue(ok)
            popen.assert_called_once()
        finally:
            path.unlink(missing_ok=True)

    def test_set_preferred_game_updates_config(self) -> None:
        service = self._service(preferred_launch_game="d4")
        with patch.object(ConfigManager, "save"):
            service.set_preferred_game("d3")

        self.assertEqual(service.preferred_game_key(), "d3")

    def test_set_preferred_game_ignores_unknown_key(self) -> None:
        service = self._service(preferred_launch_game="d4")
        with patch.object(ConfigManager, "save") as save:
            service.set_preferred_game("unknown")

        self.assertEqual(service.preferred_game_key(), "d4")
        save.assert_not_called()

    def test_game_status_reuses_provided_detection(self) -> None:
        service = self._service()
        detection = MagicMock()
        detection.active_processes = {"d4": "Diablo IV.exe"}

        with patch(
            "src.game_detection.GameDetectionService.scan",
            side_effect=AssertionError("scan should not run"),
        ):
            info = service.game_status("d4", detection=detection)

        self.assertTrue(info["running"])
        self.assertEqual(info["process"], "Diablo IV.exe")


if __name__ == "__main__":
    unittest.main()
