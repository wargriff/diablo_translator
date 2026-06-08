from __future__ import annotations

from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import get_settings
from backend.app.schemas.api import (
    ComposeRequest,
    ComposeResponse,
    MessageItem,
    QuickReplyItem,
    SettingsResponse,
    TranslateRequest,
    TranslateResponse,
)

QUICK_REPLIES = (
    ("hello", "Hello"),
    ("thanks", "Thanks"),
    ("yes", "Yes"),
    ("no", "No"),
    ("gg", "GG"),
)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=settings.version)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def _startup() -> None:
        from src.infrastructure.database import Database

        Database.initialize()

    @app.get("/api/v1/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "version": settings.version, "app": settings.app_name}

    @app.post("/api/v1/translate", response_model=TranslateResponse)
    def translate(payload: TranslateRequest) -> TranslateResponse:
        from src.infrastructure.container import Container

        container = Container()
        result = container.pipeline.process_text(payload.text, origin=payload.origin)
        return TranslateResponse(
            source_text=result.source_text,
            translated_text=result.translated_text,
            source_language=result.source_language,
            target_language=result.target_language,
            provider=result.provider,
        )

    @app.post("/api/v1/reply/compose", response_model=ComposeResponse)
    def compose(payload: ComposeRequest) -> ComposeResponse:
        from src.infrastructure.container import Container

        container = Container()
        result = container.pipeline.process_text(payload.text, origin="user")
        return ComposeResponse(
            source_text=result.source_text,
            translated_text=result.translated_text,
            character_count=len(result.translated_text),
        )

    @app.get("/api/v1/messages")
    def messages(limit: int = 50, offset: int = 0) -> dict[str, object]:
        from src.services.history_service import HistoryService

        rows = HistoryService().list_recent(limit=limit)
        items = [
            MessageItem(
                id=row.id,
                source_text=row.source_text,
                translated_text=row.translated_text,
                source_language=row.source_language,
                target_language=row.target_language,
                created_at=row.created_at.isoformat()
                if isinstance(row.created_at, datetime)
                else str(row.created_at),
            ).model_dump()
            for row in rows
        ]
        return {"items": items, "total": len(items), "limit": limit, "offset": offset}

    @app.get("/api/v1/reply/quick")
    def quick_replies() -> dict[str, list[QuickReplyItem]]:
        from src.infrastructure.container import Container

        container = Container()
        items: list[QuickReplyItem] = []
        for key, label in QUICK_REPLIES:
            result = container.pipeline.process_text(label, origin="user")
            items.append(
                QuickReplyItem(
                    key=key,
                    label=label,
                    translated_text=result.translated_text,
                )
            )
        return {"items": [item.model_dump() for item in items]}

    @app.get("/api/v1/settings", response_model=SettingsResponse)
    def get_settings_route() -> SettingsResponse:
        from src.infrastructure.config_manager import ConfigManager

        config = ConfigManager.load()
        return SettingsResponse(
            language=config.language,
            translator=config.translator,
            bidirectional_mode=config.bidirectional_mode,
        )

    return app


app = create_app()


def run_server() -> None:
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "backend.app.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )
