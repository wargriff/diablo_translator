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
    web_url = f"http://127.0.0.1:{web_port}"

    if not probe_diablo_api(DEFAULT_API_PORT):
        proc = run_server()
        if on_spawn:
            on_spawn(proc)
        else:
            children.append(proc)
        if not wait_for_api(timeout_sec=35):
            return False, "API indisponible — pip install -r backend/requirements.txt puis relancez"

    if not probe_web_home(web_port):
        proc = run_web(kill=True)
        if on_spawn:
            on_spawn(proc)
        else:
            children.append(proc)
        if not wait_for_web(web_port, timeout_sec=90):
            return False, "Web indisponible — Node.js (C:\\src ou PATH) puis npm install dans web/"

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
