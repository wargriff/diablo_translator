from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.infrastructure.config_manager import (
    CURRENT_MIGRATION_VERSION,
    AppConfig,
    ConfigManager,
)


class ConfigManagerSaveTests(unittest.TestCase):

    def test_save_persists_migration_version_and_user_choices(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            with patch.object(ConfigManager, "CONFIG_PATH", path):
                ConfigManager.save(
                    AppConfig(
                        low_cpu_mode=False,
                        capture_fps=2,
                        translator="deepl",
                        overlay_opacity=0.85,
                    )
                )
                loaded = ConfigManager.load()
                payload = json.loads(path.read_text(encoding="utf-8"))

        self.assertFalse(loaded.low_cpu_mode)
        self.assertEqual(loaded.capture_fps, 2)
        self.assertEqual(loaded.translator, "deepl")
        self.assertAlmostEqual(loaded.overlay_opacity, 0.85)
        self.assertEqual(payload["_migration_version"], CURRENT_MIGRATION_VERSION)


if __name__ == "__main__":
    unittest.main()
