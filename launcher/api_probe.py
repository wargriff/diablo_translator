"""Verification que l'API Diablo Translator repond sur le port attendu."""

from __future__ import annotations

import json
import urllib.error
import urllib.request

DEFAULT_API_PORT = 8000
HEALTH_PATH = "/api/v1/health"


def api_health_url(port: int = DEFAULT_API_PORT, host: str = "127.0.0.1") -> str:
    return f"http://{host}:{port}{HEALTH_PATH}"


def probe_diablo_api(port: int = DEFAULT_API_PORT, *, timeout: float = 0.8) -> bool:
    url = api_health_url(port)
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            if response.status != 200:
                return False
            payload = json.loads(response.read(512).decode("utf-8", errors="replace"))
            return payload.get("status") == "ok"
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError):
        return False


def probe_web_home(port: int = 3000, *, timeout: float = 0.8) -> bool:
    url = f"http://127.0.0.1:{port}/"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.status == 200
    except (urllib.error.URLError, TimeoutError, OSError):
        return False
