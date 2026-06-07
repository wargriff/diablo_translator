from __future__ import annotations

from dataclasses import dataclass

from src.capture.capture_region_resolver import CaptureRegionResolver
from src.chat.chat_line_extractor import ChatLineExtractor
from src.chat.chat_message_parser import ChatMessage, ChatMessageParser
from src.infrastructure.config_manager import AppConfig


@dataclass(slots=True)
class ChatCaptureResult:

    raw_text: str
    new_messages: list[ChatMessage]
    preset_key: str
    capture_source: str
    display_mode: str
    monitor_index: int


class ChatMonitorService:

    def __init__(self) -> None:
        self._extractor = ChatLineExtractor()
        self._previous_text = ""

    def reset(self) -> None:
        self._previous_text = ""

    def capture_chat(
        self,
        capture_service,
        game_detection_service,
        config: AppConfig,
        ocr_service,
    ) -> ChatCaptureResult:
        resolved = CaptureRegionResolver.resolve(game_detection_service, config)
        region = {
            "left": resolved.left,
            "top": resolved.top,
            "width": resolved.width,
            "height": resolved.height,
        }

        image = capture_service.capture_region(region)
        raw_text = ocr_service.extract_chat_text(
            image,
            min_confidence=config.ocr_confidence_min,
            preprocess=config.ocr_preprocess,
        )
        raw_lines = self._extractor.extract_new_lines(self._previous_text, raw_text)
        new_messages: list[ChatMessage] = []
        for line in raw_lines:
            parsed = ChatMessageParser.parse(line)
            if parsed:
                new_messages.append(parsed)
        self._previous_text = raw_text

        return ChatCaptureResult(
            raw_text=raw_text,
            new_messages=new_messages,
            preset_key=resolved.preset_key,
            capture_source=resolved.source,
            display_mode=resolved.display_mode,
            monitor_index=resolved.monitor_index,
        )
