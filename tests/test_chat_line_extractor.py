import unittest

from src.chat.chat_line_extractor import ChatLineExtractor


class ChatLineExtractorTests(unittest.TestCase):

    def setUp(self) -> None:
        self.extractor = ChatLineExtractor()

    def test_detect_new_line(self) -> None:
        previous = "Player1: hello"
        current = "Player1: hello\nPlayer2: looking for group"
        new_lines = self.extractor.extract_new_lines(previous, current)
        self.assertIn("Player2: looking for group", new_lines)

    def test_ignore_empty(self) -> None:
        self.assertEqual(self.extractor.extract_new_lines("", ""), [])


if __name__ == "__main__":
    unittest.main()
