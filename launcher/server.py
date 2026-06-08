from __future__ import annotations


def run_server(*, host: str | None = None, port: int | None = None) -> int:
    try:
        import uvicorn  # noqa: F401
    except ImportError:
        print("Installez le backend : pip install -r backend/requirements.txt")
        return 1

    from backend.app.core.config import get_settings
    from backend.app.main import run_server as _run_server

    settings = get_settings()
    if host is not None:
        settings.host = host
    if port is not None:
        settings.port = port

    print(f"API : http://{settings.host}:{settings.port}")
    print(f"Pour iPhone (meme Wi-Fi) : http://<IP-PC>:{settings.port}")
    print(f"Docs : http://127.0.0.1:{settings.port}/docs")
    _run_server()
    return 0
