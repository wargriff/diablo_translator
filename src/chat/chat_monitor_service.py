from __future__ import annotations

from dataclasses import dataclass

from src.chat.chat_line_extractor import ChatLineExtractor
from src.chat.chat_region import GAME_TO_PRESET, get_preset


@dataclass(slots=True)
class ChatCaptureResult:

    raw_text: str
    new_lines: list[str]
    preset_key: str


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
        chat_region_preset: str,
        ocr_service,
    ) -> ChatCaptureResult:
        preset_key = self._resolve_preset(game_detection_service, chat_region_preset)
        preset = get_preset(preset_key)
        region = self._build_region(preset)

        image = capture_service.capture_region(region)
        raw_text = ocr_service.extract_text(image)
        new_lines = self._extractor.extract_new_lines(self._previous_text, raw_text)
        self._previous_text = raw_text

        return ChatCaptureResult(
            raw_text=raw_text,
            new_lines=new_lines,
            preset_key=preset_key,
        )

    @staticmethod
    def _resolve_preset(game_detection_service, preset_key: str) -> str:
        if preset_key != "auto":
            return preset_key

        status = game_detection_service.scan()
        if status.primary_game:
            return GAME_TO_PRESET.get(status.primary_game.key, "d4")

        return "d4"

    @staticmethod
    def _build_region(preset) -> dict[str, int]:
        import mss

        with mss.mss() as screen:
            monitor = screen.monitors[1]
            left = monitor["left"] + int(monitor["width"] * preset.left_pct)
            top = monitor["top"] + int(monitor["height"] * preset.top_pct)
            width = int(monitor["width"] * preset.width_pct)
            height = int(monitor["height"] * preset.height_pct)

        return {
            "left": left,
            "top": top,
            "width": width,
            "height": height,
        }
