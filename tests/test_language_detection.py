import unittest

from src.translation.language_detection_service import LanguageDetectionService


class LanguageDetectionTests(unittest.TestCase):

    def setUp(self) -> None:
        self.service = LanguageDetectionService()

    def test_same_language_fr(self) -> None:
        self.assertTrue(self.service.is_same_language("fr", "fr"))

    def test_short_text_returns_none(self) -> None:
        self.assertIsNone(self.service.detect("a"))


if __name__ == "__main__":
    unittest.main()
