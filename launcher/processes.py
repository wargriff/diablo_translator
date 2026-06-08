from __future__ import annotations

import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from collections.abc import Callable
from pathlib import Path

from src.infrastructure.paths import PROJECT_ROOT

PYTHON = sys.executable
LAUNCHER = PROJECT_ROOT / "launcher.py"
DEFAULT_WEB_PORT = 3000
DEFAULT_API_PORT = 8000


def probe_url(url: str, *, timeout: float = 0.6) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.status == 200
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        return False


def wait_for_url(url: str, *, timeout_sec: float = 60, interval: float = 0.5) -> bool:
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        if probe_url(url, timeout=1.0):
            return True
        time.sleep(interval)
    return False


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


def prepare_live_web(
    children: list[subprocess.Popen[bytes]],
    *,
    on_spawn: Callable[[subprocess.Popen[bytes]], None] | None = None,
    web_port: int = DEFAULT_WEB_PORT,
) -> tuple[bool, str]:
    """Démarre API + Web si nécessaire, puis ouvre /live."""
    api_url = f"http://127.0.0.1:{DEFAULT_API_PORT}/api/v1/health"
    web_url = f"http://127.0.0.1:{web_port}"

    if not probe_url(api_url):
        proc = run_server()
        if on_spawn:
            on_spawn(proc)
        else:
            children.append(proc)
        if not wait_for_url(api_url, timeout_sec=35):
            return False, "API indisponible — vérifiez le serveur (:8000)"

    if not probe_url(web_url):
        proc = run_web(kill=True)
        if on_spawn:
            on_spawn(proc)
        else:
            children.append(proc)
        if not wait_for_url(web_url, timeout_sec=90):
            return False, "Web indisponible — installez Node.js et lancez Services → Web"

    open_web_browser(web_port, "/live")
    return True, f"Live web ouvert — {web_url}/live"


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


def run_platform() -> tuple[subprocess.Popen[bytes], subprocess.Popen[bytes]]:
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
