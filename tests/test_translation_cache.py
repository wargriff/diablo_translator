import unittest

from src.cache.translation_cache import TranslationCache
from src.infrastructure.paths import CACHE_TRANSLATIONS_DIR, ensure_project_dirs


class TranslationCacheTests(unittest.TestCase):

    def setUp(self) -> None:
        ensure_project_dirs()
        self.cache_path = CACHE_TRANSLATIONS_DIR / "cache_test.json"
        if self.cache_path.exists():
            self.cache_path.unlink()
        self.cache = TranslationCache(max_entries=10)
        self.cache._path = self.cache_path

    def tearDown(self) -> None:
        if self.cache_path.exists():
            self.cache_path.unlink()

    def test_set_and_get(self) -> None:
        self.cache.set(
            "hello",
            "bonjour",
            target_language="fr",
            provider="google",
            source_language="en",
        )
        value = self.cache.get("hello", "fr", "google")
        self.assertEqual(value, "bonjour")
        self.assertEqual(self.cache.stats.hits, 1)

    def test_miss_increments_stats(self) -> None:
        value = self.cache.get("missing", "fr", "google")
        self.assertIsNone(value)
        self.assertEqual(self.cache.stats.misses, 1)


if __name__ == "__main__":
    unittest.main()
