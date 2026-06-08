from __future__ import annotations

from pydantic import BaseModel, Field


class TranslateRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
    origin: str = "user"


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


class ComposeResponse(BaseModel):
    source_text: str
    translated_text: str
    character_count: int


class QuickReplyItem(BaseModel):
    key: str
    label: str
    translated_text: str


class SettingsResponse(BaseModel):
    language: str
    translator: str
    bidirectional_mode: bool
