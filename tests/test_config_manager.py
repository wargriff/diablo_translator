from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.infrastructure.config_manager import AppConfig, ConfigManager


class ConfigManagerTests(unittest.TestCase):

    def test_save_persists_migration_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            with patch.object(ConfigManager, "CONFIG_PATH", path):
                config = AppConfig(
                    overlay_compact=False,
                    always_on_top=False,
                    translator="deepl",
                    capture_fps=2,
                )
                ConfigManager.save(config)
                data = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(
                    data["_migration_version"],
                    ConfigManager.CURRENT_MIGRATION_VERSION,
                )

                loaded = ConfigManager.load()
                self.assertFalse(loaded.overlay_compact)
                self.assertFalse(loaded.always_on_top)
                self.assertEqual(loaded.translator, "deepl")
                self.assertEqual(loaded.capture_fps, 2)


if __name__ == "__main__":
    unittest.main()
