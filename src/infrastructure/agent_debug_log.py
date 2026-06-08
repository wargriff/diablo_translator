from __future__ import annotations

import json
import os
import sys
import threading
import time
from pathlib import Path
from typing import Any

from src.infrastructure.paths import LOGS_DIR, PROJECT_ROOT

SESSION_ID = "c786be"
LOG_PATH = PROJECT_ROOT / "debug-c786be.log"
LOG_MIRROR_PATH = LOGS_DIR / "debug-c786be.log"
LOG_FALLBACK_PATH = Path(os.environ.get("TEMP", os.environ.get("TMP", "."))) / "diablo_translator_debug_c786be.log"
LOG_HOME_PATH = Path.home() / "DiabloTranslator" / "debug-c786be.log"
_lock = threading.Lock()
_listeners: list = []


def log_paths() -> tuple[str, ...]:
    return tuple(
        str(path)
        for path in (LOG_PATH, LOG_MIRROR_PATH, LOG_FALLBACK_PATH, LOG_HOME_PATH)
    )


def register_listener(callback) -> None:
    _listeners.append(callback)


def agent_log(
    location: str,
    message: str,
    *,
    hypothesis_id: str,
    data: dict[str, Any] | None = None,
    run_id: str = "pre-fix",
) -> None:
    payload = {
        "sessionId": SESSION_ID,
        "runId": run_id,
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data or {},
        "timestamp": int(time.time() * 1000),
        "thread": threading.current_thread().name,
        "threadId": threading.get_ident(),
        "executable": sys.executable,
        "frozen": getattr(sys, "frozen", False),
    }
    line = json.dumps(payload, ensure_ascii=False)

    with _lock:
        for path in (LOG_PATH, LOG_MIRROR_PATH, LOG_FALLBACK_PATH, LOG_HOME_PATH):
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, "a", encoding="utf-8") as handle:
                    handle.write(line + "\n")
            except OSError:
                pass

    for listener in list(_listeners):
        try:
            listener(payload)
        except Exception:
            pass
