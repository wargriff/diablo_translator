import unittest

from src.chat.chat_text_normalizer import ChatTextNormalizer
from src.chat.chat_message_parser import ChatMessageParser
from src.infrastructure.config_manager import AppConfig
from src.translation.conversation_context import ConversationContext
from src.translation.translation_service import TranslationService


class ChatTextNormalizerTests(unittest.TestCase):

    def test_dedupe_repeated_words(self):
        text = "Subjugateur ! Subjugateur !"
        self.assertEqual(
            ChatTextNormalizer.dedupe_repeated_content(text),
            "Subjugateur !",
        )

    def test_extract_message_after_duplicate_dit(self):
        line = "wargriff dit wargriff dit Meurs ! Meurs !"
        message = ChatTextNormalizer.extract_chat_message(line)
        self.assertEqual(message, "Meurs !")

    def test_filters_garbage_mixed_script(self):
        self.assertTrue(ChatTextNormalizer.is_likely_garbage("nchuatcu cych"))
        self.assertTrue(ChatTextNormalizer.is_likely_garbage("chparop uipler"))

    def test_parser_uses_deduped_message(self):
        parsed = ChatMessageParser.parse(
            "wargriff dit wargriff dit Mes coups vont t'achever Mes coups vont t'achever"
        )
        self.assertIsNotNone(parsed)
        assert parsed is not None
        self.assertEqual(parsed.message, "Mes coups vont t'achever")


class TranslationDirectionTests(unittest.TestCase):

    def test_manual_french_targets_peer_language(self):
        config = AppConfig(language="fr", bidirectional_mode=True, default_reply_language="en")
        service = TranslationService(config, ConversationContext())
        target = service._resolve_target("fr", "user", "fr")
        self.assertEqual(target, "en")

    def test_manual_english_targets_home_language(self):
        config = AppConfig(language="fr", bidirectional_mode=True, default_reply_language="en")
        service = TranslationService(config, ConversationContext())
        target = service._resolve_target("en", "user", "fr")
        self.assertEqual(target, "fr")


if __name__ == "__main__":
    unittest.main()
