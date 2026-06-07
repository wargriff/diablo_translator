import unittest

from src.ocr.easyocr_languages import split_easyocr_language_groups


class EasyOcrLanguageGroupTests(unittest.TestCase):

    def test_splits_cyrillic_from_latin(self):
        latin, cyrillic = split_easyocr_language_groups(
            ("en", "fr", "de", "ru", "pl")
        )
        self.assertEqual(latin, ("en", "fr", "de", "pl"))
        self.assertEqual(cyrillic, ("en", "ru"))

    def test_latin_only(self):
        latin, cyrillic = split_easyocr_language_groups(("en", "fr", "de"))
        self.assertEqual(latin, ("en", "fr", "de"))
        self.assertIsNone(cyrillic)


if __name__ == "__main__":
    unittest.main()
