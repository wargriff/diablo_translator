from __future__ import annotations

import asyncio
import json
from datetime import datetime
from typing import Any

from fastapi import WebSocket

_clients: set[WebSocket] = set()
_loop: asyncio.AbstractEventLoop | None = None


def bind_loop(loop: asyncio.AbstractEventLoop) -> None:
    global _loop
    _loop = loop


def record_to_payload(record) -> dict[str, Any]:
    created_at = record.created_at
    if isinstance(created_at, datetime):
        created_at = created_at.isoformat()
    return {
        "type": "translation",
        "id": record.id,
        "source_text": record.source_text,
        "translated_text": record.translated_text,
        "source_language": record.source_language,
        "target_language": record.target_language,
        "created_at": str(created_at),
    }


async def register_client(websocket: WebSocket) -> None:
    _clients.add(websocket)


async def unregister_client(websocket: WebSocket) -> None:
    _clients.discard(websocket)


async def broadcast(payload: dict[str, Any]) -> None:
    if not _clients:
        return

    message = json.dumps(payload, ensure_ascii=False)
    dead: list[WebSocket] = []
    for client in list(_clients):
        try:
            await client.send_text(message)
        except Exception:
            dead.append(client)

    for client in dead:
        _clients.discard(client)


def schedule_broadcast(payload: dict[str, Any]) -> None:
    if _loop is None or not _loop.is_running():
        return
    asyncio.run_coroutine_threadsafe(broadcast(payload), _loop)


def on_translation_added(record) -> None:
    schedule_broadcast(record_to_payload(record))
