from __future__ import annotations

import re
import socket
import subprocess
import sys
import time


def _decode_output(data: bytes | None) -> str:
    if not data:
        return ""
    for encoding in ("utf-8", "cp1252", "mbcs"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def _run_command(command: list[str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(command, capture_output=True, check=False)


def _pids_on_port_powershell(port: int) -> set[str]:
    script = (
        f"(Get-NetTCPConnection -LocalPort {port} -State Listen "
        f"-ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess "
        f"| Sort-Object -Unique) -join ' '"
    )
    result = _run_command(["powershell", "-NoProfile", "-Command", script])
    output = _decode_output(result.stdout).strip()
    if not output:
        return set()
    return {pid for pid in output.split() if pid.isdigit() and pid not in {"0", "4"}}


def _pids_on_port_netstat(port: int) -> set[str]:
    result = _run_command(["netstat", "-ano"])
    output = _decode_output(result.stdout)
    if not output:
        return set()

    port_pattern = re.compile(rf":{port}(?:\s|$)")
    pids: set[str] = set()
    for line in output.splitlines():
        upper = line.upper()
        if "LISTENING" not in upper and "ESTABLISHED" not in upper:
            continue
        if not port_pattern.search(line):
            continue
        parts = line.split()
        if parts and parts[-1].isdigit():
            pid = parts[-1]
            if pid not in {"0", "4"}:
                pids.add(pid)
    return pids


def is_port_in_use(port: int) -> bool:
    """Detecte un port occupe (IPv4 + IPv6, comme Next.js :::port)."""
    for family, target in (
        (socket.AF_INET, ("127.0.0.1", port)),
        (socket.AF_INET6, ("::1", port, 0, 0)),
    ):
        with socket.socket(family, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.25)
            try:
                if sock.connect_ex(target) == 0:
                    return True
            except OSError:
                pass

    for family, bind_addr in (
        (socket.AF_INET, ("127.0.0.1", port)),
        (socket.AF_INET, ("0.0.0.0", port)),
        (socket.AF_INET6, ("::1", port, 0, 0)),
        (socket.AF_INET6, ("::", port, 0, 0)),
    ):
        with socket.socket(family, socket.SOCK_STREAM) as sock:
            try:
                if family == socket.AF_INET6:
                    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(bind_addr)
            except OSError:
                return True
    return False


def resolve_port(port: int, *, auto_fallback: bool = True) -> int:
    if not is_port_in_use(port):
        return port
    if not auto_fallback:
        return port
    for candidate in range(port + 1, port + 20):
        if not is_port_in_use(candidate):
            print(f"Port {port} occupe — bascule sur {candidate}")
            return candidate
    return port


def kill_process_on_port(port: int) -> bool:
    if sys.platform != "win32":
        return False

    pids = _pids_on_port_powershell(port)
    if not pids:
        pids = _pids_on_port_netstat(port)

    if not pids:
        print(f"Aucun processus trouve sur le port {port}.")
        return False

    killed = False
    for pid in sorted(pids):
        proc = _run_command(["taskkill", "/PID", pid, "/F", "/T"])
        if proc.returncode == 0:
            print(f"Processus arrete : PID {pid}")
            killed = True
        else:
            err = _decode_output(proc.stderr).strip()
            if err:
                print(f"taskkill PID {pid} : {err}")

    if killed:
        time.sleep(1.5)
    return killed


def prepare_port(port: int, *, kill: bool = False, auto_port: bool = True) -> int:
    if not is_port_in_use(port):
        return port

    if kill:
        print(f"Port {port} occupe — liberation...")
        kill_process_on_port(port)

    if is_port_in_use(port) and auto_port:
        chosen = resolve_port(port, auto_fallback=True)
        if chosen != port:
            print(f"Port {port} toujours occupe — bascule sur {chosen}.")
            return chosen

    if is_port_in_use(port):
        raise RuntimeError(
            f"Port {port} toujours occupe. Essayez : py -3 launcher.py web --port {port + 1}"
        )

    return port
