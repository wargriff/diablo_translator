from __future__ import annotations

import subprocess
import sys
import time
import webbrowser
from collections.abc import Callable

from launcher.api_probe import (
    DEFAULT_API_PORT,
    probe_diablo_api,
    probe_web_home,
)
from src.infrastructure.paths import PROJECT_ROOT

PYTHON = sys.executable
LAUNCHER = PROJECT_ROOT / "launcher.py"
DEFAULT_WEB_PORT = 3000


def wait_for_api(*, timeout_sec: float = 60, interval: float = 0.5) -> bool:
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        if probe_diablo_api(DEFAULT_API_PORT, timeout=1.0):
            return True
        time.sleep(interval)
    return False


def wait_for_web(port: int = DEFAULT_WEB_PORT, *, timeout_sec: float = 90, interval: float = 0.5) -> bool:
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        if probe_web_home(port, timeout=1.0):
            return True
        time.sleep(interval)
    return False


def ensure_api_running(
    *,
    spawn_if_missing: bool = True,
    on_spawn: Callable[[subprocess.Popen[bytes]], None] | None = None,
    children: list[subprocess.Popen[bytes]] | None = None,
) -> tuple[bool, str]:
    """Verifie que l'API Diablo ecoute sur :8000; la demarre si besoin."""
    if probe_diablo_api(DEFAULT_API_PORT):
        return True, f"API active — http://127.0.0.1:{DEFAULT_API_PORT}"

    try:
        import uvicorn  # noqa: F401
    except ImportError:
        return False, "Installez l'API : pip install -r backend/requirements.txt"

    if not spawn_if_missing:
        return False, "API arretee — lancez launcher.py server dans un autre terminal"

    print("Demarrage API FastAPI (:8000)...")
    proc = run_server()
    if on_spawn:
        on_spawn(proc)
    elif children is not None:
        children.append(proc)
    if not wait_for_api(timeout_sec=45):
        return (
            False,
            "API indisponible — verifiez la fenetre console « server » "
            "ou : pip install -r backend/requirements.txt",
        )
    return True, f"API demarree — http://127.0.0.1:{DEFAULT_API_PORT}"


def _launcher_command(args: list[str]) -> list[str]:
    if getattr(sys, "frozen", False):
        return [PYTHON, *args]
    return [PYTHON, str(LAUNCHER), *args]


def _spawn(args: list[str], *, new_console: bool = True) -> subprocess.Popen[bytes]:
    creationflags = 0
    if sys.platform == "win32" and new_console:
        creationflags = subprocess.CREATE_NEW_CONSOLE  # type: ignore[attr-defined]
    return subprocess.Popen(
        _launcher_command(args),
        cwd=PROJECT_ROOT,
        creationflags=creationflags,
    )


def open_web_browser(port: int = DEFAULT_WEB_PORT, path: str = "/") -> None:
    webbrowser.open(f"http://127.0.0.1:{port}{path}")


def launch_platform_orchestrated(
    children: list[subprocess.Popen[bytes]],
    *,
    on_spawn: Callable[[subprocess.Popen[bytes]], None] | None = None,
    web_port: int = DEFAULT_WEB_PORT,
    open_browser: bool = False,
    browser_path: str = "/",
) -> tuple[bool, str]:
    """Demarre API puis Web dans l'ordre, avec attente de disponibilite."""
    ok, message = ensure_api_running(on_spawn=on_spawn, children=children)
    if not ok:
        return False, message
    if message.startswith("API demarree"):
        print(message)

    if not probe_web_home(web_port):
        proc = run_web(kill=True)
        if on_spawn:
            on_spawn(proc)
        else:
            children.append(proc)
        if not wait_for_web(web_port, timeout_sec=120):
            return False, "Web indisponible — Node.js (C:\\src) puis relancez Plateforme"

    url = f"http://127.0.0.1:{web_port}{browser_path}"
    if open_browser:
        webbrowser.open(url)
    return True, f"Plateforme OK — {url}"


def prepare_live_web(
    children: list[subprocess.Popen[bytes]],
    *,
    on_spawn: Callable[[subprocess.Popen[bytes]], None] | None = None,
    web_port: int = DEFAULT_WEB_PORT,
) -> tuple[bool, str]:
    """Demarre API + Web si necessaire, puis ouvre /live."""
    ok, message = launch_platform_orchestrated(
        children,
        on_spawn=on_spawn,
        web_port=web_port,
        open_browser=True,
        browser_path="/live",
    )
    if ok:
        return True, message.replace("Plateforme OK", "Live web ouvert")
    return False, message


def stop_all_services(children: list[subprocess.Popen[bytes]]) -> int:
    from launcher.ports import kill_process_on_port

    stopped = terminate_processes(children)
    if probe_diablo_api(DEFAULT_API_PORT):
        if kill_process_on_port(DEFAULT_API_PORT):
            stopped += 1
    for port in range(DEFAULT_WEB_PORT, DEFAULT_WEB_PORT + 10):
        if probe_web_home(port, timeout=0.3):
            if kill_process_on_port(port):
                stopped += 1
    return stopped


def run_desktop() -> subprocess.Popen[bytes]:
    return _spawn(["gui"])


def run_server() -> subprocess.Popen[bytes]:
    return _spawn(["server"])


def run_web(*, kill: bool = True) -> subprocess.Popen[bytes]:
    args = ["web"]
    if kill:
        args.append("--kill")
    return _spawn(args)


def run_mobile() -> subprocess.Popen[bytes]:
    return _spawn(["mobile"])


def run_platform(*, open_browser: bool = False) -> tuple[bool, str]:
    return launch_platform_orchestrated([], open_browser=open_browser)


def run_platform_processes() -> tuple[subprocess.Popen[bytes], subprocess.Popen[bytes]]:
    return run_server(), run_web(kill=True)


def run_cli_tool(command: str) -> int:
    return subprocess.run(_launcher_command([command]), cwd=PROJECT_ROOT).returncode or 0


def terminate_processes(processes: list[subprocess.Popen[bytes]]) -> int:
    stopped = 0
    for process in list(processes):
        if process.poll() is not None:
            continue
        process.terminate()
        stopped += 1
    processes.clear()
    return stopped
