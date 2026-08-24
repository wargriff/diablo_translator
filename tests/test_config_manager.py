from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.infrastructure.config_manager import (
    CURRENT_MIGRATION_VERSION,
    AppConfig,
    ConfigManager,
)


class ConfigManagerTests(unittest.TestCase):

    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory()
        self._path = Path(self._temp.name) / "settings.json"
        self._original = ConfigManager.CONFIG_PATH
        ConfigManager.CONFIG_PATH = self._path

    def tearDown(self) -> None:
        ConfigManager.CONFIG_PATH = self._original
        self._temp.cleanup()

    def test_save_persists_migration_version(self) -> None:
        ConfigManager.save(AppConfig(overlay_compact=False, translator="deepl"))

        data = json.loads(self._path.read_text(encoding="utf-8"))
        self.assertEqual(data["_migration_version"], CURRENT_MIGRATION_VERSION)
        self.assertFalse(data["overlay_compact"])
        self.assertEqual(data["translator"], "deepl")

    def test_load_after_save_does_not_reapply_migrations(self) -> None:
        ConfigManager.save(
            AppConfig(
                overlay_compact=False,
                always_on_top=False,
                translator="deepl",
                capture_fps=2,
                low_cpu_mode=False,
                chat_region_preset="auto",
            )
        )

        loaded = ConfigManager.load()

        self.assertFalse(loaded.overlay_compact)
        self.assertFalse(loaded.always_on_top)
        self.assertEqual(loaded.translator, "deepl")
        self.assertEqual(loaded.capture_fps, 2)
        self.assertFalse(loaded.low_cpu_mode)
        self.assertEqual(loaded.chat_region_preset, "auto")

    def test_legacy_file_without_version_is_migrated_once(self) -> None:
        self._path.write_text(
            json.dumps({"language": "fr", "overlay_compact": False}),
            encoding="utf-8",
        )

        loaded = ConfigManager.load()
        data = json.loads(self._path.read_text(encoding="utf-8"))

        self.assertEqual(data["_migration_version"], CURRENT_MIGRATION_VERSION)
        self.assertTrue(loaded.overlay_compact)


if __name__ == "__main__":
    unittest.main()
