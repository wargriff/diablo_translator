from __future__ import annotations


def run_server(*, host: str | None = None, port: int | None = None) -> int:
    try:
        import uvicorn  # noqa: F401
    except ImportError:
        print("Installez l'API : pip install -r backend/requirements.txt")
        return 1

    from launcher.api_probe import DEFAULT_API_PORT, probe_diablo_api
    from launcher.ports import is_port_in_use, kill_process_on_port
    from backend.app.core.config import get_settings
    from backend.app.main import run_server as _run_server

    settings = get_settings()
    if host is not None:
        settings.host = host
    if port is not None:
        settings.port = port

    listen_port = settings.port

    if is_port_in_use(listen_port) and not probe_diablo_api(listen_port):
        print(
            f"Port {listen_port} occupe par un autre programme (pas l'API Diablo). "
            "Liberation..."
        )
        kill_process_on_port(listen_port)

    if is_port_in_use(listen_port) and not probe_diablo_api(listen_port):
        print(
            f"Impossible de demarrer l'API sur {listen_port}. "
            f"Fermez l'autre application ou lancez : launcher.py server --port {listen_port + 1}"
        )
        return 1

    if probe_diablo_api(listen_port):
        print(f"API deja active : http://127.0.0.1:{listen_port}{'/api/v1/health'}")
        return 0

    print(f"API : http://{settings.host}:{settings.port}")
    print(f"Docs : http://127.0.0.1:{settings.port}/docs")
    _run_server()
    return 0
