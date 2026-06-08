from __future__ import annotations

import asyncio
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import get_settings
from backend.app.live_bus import bind_loop, on_translation_added, register_client, unregister_client
from backend.app.schemas.api import (
    ComposeRequest,
    ComposeResponse,
    GameStatusResponse,
    LogsResponse,
    MessageItem,
    QuickReplyItem,
    SettingsResponse,
    SettingsUpdateRequest,
    StatsResponse,
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
    async def _startup() -> None:
        from src.infrastructure.database import Database
        from src.services.history_events import on_translation_added as subscribe

        Database.initialize()
        bind_loop(asyncio.get_running_loop())
        subscribe(on_translation_added)

    @app.get("/api/v1/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "version": settings.version, "app": settings.app_name}

    @app.post("/api/v1/translate", response_model=TranslateResponse)
    def translate(payload: TranslateRequest) -> TranslateResponse:
        from src.infrastructure.container import Container

        container = Container()
        result = container.pipeline.process_text(
            payload.text,
            origin=payload.origin,
            source_language=payload.source_language,
            target_language=payload.target_language,
        )
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
        result = container.pipeline.process_text(
            payload.text,
            origin="user",
            source_language=payload.source_language,
            target_language=payload.target_language,
        )
        return ComposeResponse(
            source_text=result.source_text,
            translated_text=result.translated_text,
            character_count=len(result.translated_text),
            source_language=result.source_language,
            target_language=result.target_language,
        )

    @app.get("/api/v1/messages")
    def messages(limit: int = 50, offset: int = 0) -> dict[str, object]:
        from src.services.history_service import HistoryService

        service = HistoryService()
        rows = service.list_recent(limit=limit, offset=offset)
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
        return {"items": items, "total": service.count(), "limit": limit, "offset": offset}

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
        return _settings_from_config(config)

    @app.put("/api/v1/settings", response_model=SettingsResponse)
    def update_settings_route(payload: SettingsUpdateRequest) -> SettingsResponse:
        return _apply_settings_update(payload)

    @app.patch("/api/v1/settings", response_model=SettingsResponse)
    def patch_settings_route(payload: SettingsUpdateRequest) -> SettingsResponse:
        return _apply_settings_update(payload)

    @app.get("/api/v1/stats", response_model=StatsResponse)
    def stats_route() -> StatsResponse:
        from src.analytics.analytics_service import AnalyticsService
        from src.infrastructure.config_manager import ConfigManager
        from src.services.history_service import HistoryService

        config = ConfigManager.load()
        service = HistoryService()
        analytics = AnalyticsService().get_summary()
        return StatsResponse(
            message_count=service.count(),
            recent_count=len(service.list_recent(limit=200)),
            translator=config.translator,
            language=config.language,
            translations_today=analytics.translations_today,
            unique_sources=analytics.unique_sources,
            api_version=settings.version,
        )

    @app.get("/api/v1/stats/summary", response_model=StatsResponse)
    def stats_summary_route() -> StatsResponse:
        return stats_route()

    @app.websocket("/ws/v1/live")
    async def live_websocket(websocket: WebSocket) -> None:
        await websocket.accept()
        await register_client(websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            await unregister_client(websocket)
        except Exception:
            await unregister_client(websocket)

    @app.get("/api/v1/game/status", response_model=GameStatusResponse)
    def game_status_route() -> GameStatusResponse:
        from src.infrastructure.container import Container

        status = Container().game_detection.scan(force=True)
        return GameStatusResponse(
            running=status.is_any_running,
            summary=status.summary(),
            games=[
                {"key": game.key, "title": game.title, "short_title": game.short_title}
                for game in status.running_games
            ],
        )

    @app.get("/api/v1/logs", response_model=LogsResponse)
    def logs_route(lines: int = 80) -> LogsResponse:
        from src.infrastructure.paths import LOGS_DIR

        log_path = LOGS_DIR / "app.log"
        if not log_path.exists():
            return LogsResponse(lines=[], path=str(log_path))

        content = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
        tail = content[-max(1, min(lines, 500)) :]
        return LogsResponse(lines=tail, path=str(log_path))

    return app


def _apply_settings_update(payload: SettingsUpdateRequest) -> SettingsResponse:
    from src.infrastructure.config_manager import ConfigManager

    config = ConfigManager.load()
    updates = payload.model_dump(exclude_unset=True)
    deepl_key = updates.pop("deepl_api_key", None)
    for key, value in updates.items():
        if hasattr(config, key):
            setattr(config, key, value)
    if deepl_key is not None:
        config.deepl_api_key = deepl_key.strip()
    ConfigManager.save(config)
    return _settings_from_config(config)


def _settings_from_config(config) -> SettingsResponse:
    return SettingsResponse(
        language=config.language,
        translator=config.translator,
        bidirectional_mode=config.bidirectional_mode,
        auto_detect_language=config.auto_detect_language,
        default_reply_language=config.default_reply_language,
        capture_fps=config.capture_fps,
        chat_monitor_enabled=config.chat_monitor_enabled,
        voice_input_enabled=config.voice_input_enabled,
        speak_translation=config.speak_translation,
        hub_sounds_enabled=config.hub_sounds_enabled,
        preferred_launch_game=config.preferred_launch_game,
        ocr_languages=config.ocr_languages,
        deepl_api_key_set=bool(config.deepl_api_key.strip()),
    )


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
