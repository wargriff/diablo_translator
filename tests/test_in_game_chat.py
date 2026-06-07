import unittest

from src.application.in_game_chat_router import InGameChatRouter
from src.application.player_identity_service import PlayerIdentityService
from src.chat.chat_message_parser import ChatMessageParser
from src.infrastructure.config_manager import AppConfig
from src.translation.conversation_context import ConversationContext
from src.translation.translation_pipeline import TranslationPipeline


class ChatMessageParserTests(unittest.TestCase):

    def test_parse_d3_line_with_speaker(self):
        line = "[PowerLeveling FR] : [<STMM> Wargriff] dit : hello la team"
        parsed = ChatMessageParser.parse(line)
        self.assertIsNotNone(parsed)
        assert parsed is not None
        self.assertEqual(parsed.speaker, "Wargriff")
        self.assertEqual(parsed.message, "hello la team")
        self.assertEqual(parsed.channel, "PowerLeveling FR")

    def test_parse_filters_loot(self):
        self.assertIsNone(
            ChatMessageParser.parse("Wargriff a forgé Lame du destin")
        )


class InGameChatRouterTests(unittest.TestCase):

    def setUp(self):
        self.config = AppConfig(player_name="Wargriff", language="fr")
        self.pipeline = TranslationPipeline(self.config, ConversationContext())
        self.identity = PlayerIdentityService()
        self.router = InGameChatRouter(self.pipeline, self.identity)

    def test_local_player_message_is_outgoing(self):
        message = ChatMessageParser.parse(
            "[Clan] : [<TAG> Wargriff] dit : salut tout le monde"
        )
        self.assertIsNotNone(message)
        result = self.router.process_message(message, self.config)
        self.assertTrue(result.outgoing)

    def test_foreign_player_message_is_incoming(self):
        message = ChatMessageParser.parse(
            "[Clan] : [<TAG> ForeignGuy] says : need help pls"
        )
        self.assertIsNotNone(message)
        result = self.router.process_message(message, self.config)
        self.assertFalse(result.outgoing)
        self.assertTrue(result.translated_text)

    def test_whisper_chuchote_is_incoming(self):
        message = ChatMessageParser.parse("[<CORS> Stiller] chuchote : Hey")
        self.assertIsNotNone(message)
        assert message is not None
        self.assertEqual(message.speaker, "Stiller")
        self.assertEqual(message.message, "Hey")
        result = self.router.process_message(message, self.config)
        self.assertFalse(result.outgoing)
        self.assertTrue(result.translated_text)
        self.assertNotEqual(result.translated_text.casefold(), "hey")


if __name__ == "__main__":
    unittest.main()
