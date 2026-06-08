from __future__ import annotations

from pydantic import BaseModel, Field


class TranslateRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
    origin: str = "user"
    source_language: str | None = None
    target_language: str | None = None


class TranslateResponse(BaseModel):
    source_text: str
    translated_text: str
    source_language: str | None = None
    target_language: str
    provider: str


class MessageItem(BaseModel):
    id: int
    source_text: str
    translated_text: str
    source_language: str | None = None
    target_language: str | None = None
    created_at: str


class ComposeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=500)
    source_language: str | None = None
    target_language: str | None = None


class ComposeResponse(BaseModel):
    source_text: str
    translated_text: str
    character_count: int
    source_language: str | None = None
    target_language: str | None = None


class QuickReplyItem(BaseModel):
    key: str
    label: str
    translated_text: str


class SettingsResponse(BaseModel):
    language: str
    translator: str
    bidirectional_mode: bool
    auto_detect_language: bool
    default_reply_language: str
    capture_fps: int
    chat_monitor_enabled: bool
    voice_input_enabled: bool
    speak_translation: bool
    hub_sounds_enabled: bool = True
    preferred_launch_game: str
    ocr_languages: str
    deepl_api_key_set: bool


class SettingsUpdateRequest(BaseModel):
    language: str | None = None
    translator: str | None = None
    bidirectional_mode: bool | None = None
    auto_detect_language: bool | None = None
    default_reply_language: str | None = None
    capture_fps: int | None = Field(default=None, ge=1, le=5)
    chat_monitor_enabled: bool | None = None
    voice_input_enabled: bool | None = None
    speak_translation: bool | None = None
    hub_sounds_enabled: bool | None = None
    preferred_launch_game: str | None = None
    ocr_languages: str | None = None
    deepl_api_key: str | None = None


class GameStatusResponse(BaseModel):
    running: bool
    summary: str
    games: list[dict[str, str]]


class StatsResponse(BaseModel):
    message_count: int
    recent_count: int
    translator: str
    language: str
    translations_today: int = 0
    unique_sources: int = 0
    api_version: str = "2.1.0"


class LogsResponse(BaseModel):
    lines: list[str]
    path: str
