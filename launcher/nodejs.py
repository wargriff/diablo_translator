"""Detection Node.js / npm — Windows (PATH + emplacements courants dont C:\\src)."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


def _node_dirs() -> list[Path]:
    dirs: list[Path] = []
    seen: set[str] = set()

    def add(path: Path) -> None:
        key = str(path.resolve()) if path.exists() else str(path)
        if key not in seen:
            seen.add(key)
            dirs.append(path)

    for raw in (
        os.environ.get("DT_NODE_HOME"),
        os.environ.get("NODE_HOME"),
        r"C:\src",
        os.environ.get("ProgramFiles", r"C:\Program Files") + r"\nodejs",
        os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)") + r"\nodejs",
        str(Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "node"),
        str(Path(os.environ.get("APPDATA", "")) / "npm"),
    ):
        if raw:
            add(Path(raw))

    return [d for d in dirs if d.is_dir()]


def find_node_exe() -> Path | None:
    found = shutil.which("node")
    if found:
        return Path(found)

    for directory in _node_dirs():
        candidate = directory / "node.exe"
        if candidate.is_file():
            return candidate
    return None


def find_npm() -> Path | None:
    found = shutil.which("npm")
    if found:
        return Path(found)

    for directory in _node_dirs():
        for name in ("npm.cmd", "npm.exe", "npm"):
            candidate = directory / name
            if candidate.is_file():
                return candidate
    return None


def node_env(base: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(os.environ if base is None else base)
    prefixes: list[str] = []
    node = find_node_exe()
    if node is not None:
        prefixes.append(str(node.parent))
    for directory in _node_dirs():
        prefixes.append(str(directory))
    if prefixes:
        env["PATH"] = os.pathsep.join(prefixes + [env.get("PATH", "")])
    return env


def npm_hint() -> str:
    node = find_node_exe()
    npm = find_npm()
    if node and npm:
        return f"Node detecte : {node.parent}"
    return (
        "Node.js introuvable. Installez Node.js LTS ou placez node.exe dans C:\\src "
        "(comme sur votre PC)."
    )
