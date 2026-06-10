"""Ports actifs des services (API / Web)."""

from __future__ import annotations

from launcher.api_probe import DEFAULT_API_PORT, probe_diablo_api, probe_web_home

DEFAULT_WEB_PORT = 3000
API_PORT = DEFAULT_API_PORT
WEB_PORT = DEFAULT_WEB_PORT


def resolve_web_port(*, start: int = DEFAULT_WEB_PORT, span: int = 20) -> int:
    for port in range(start, start + span):
        if probe_web_home(port, timeout=0.4):
            return port
    return start


def resolve_api_port(*, start: int = DEFAULT_API_PORT, span: int = 5) -> int:
    for port in range(start, start + span):
        if probe_diablo_api(port, timeout=0.4):
            return port
    return start


def web_base_url(port: int | None = None) -> str:
    chosen = port if port is not None else resolve_web_port()
    return f"http://127.0.0.1:{chosen}"


def api_base_url(port: int | None = None) -> str:
    chosen = port if port is not None else resolve_api_port()
    return f"http://127.0.0.1:{chosen}"
