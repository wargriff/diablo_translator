from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = PROJECT_ROOT / "web"


def _find_npm() -> str | None:
    npm = shutil.which("npm")
    if npm:
        return npm
    if sys.platform == "win32":
        candidates = (
            Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "nodejs" / "npm.cmd",
            Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "nodejs" / "npm.cmd",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "node" / "npm.cmd",
            Path(os.environ.get("APPDATA", "")) / "npm" / "npm.cmd",
        )
        for candidate in candidates:
            if candidate.exists():
                return str(candidate)
    return None


def run_web(*, port: int = 3000, kill: bool = False, auto_port: bool = True) -> int:
    if not WEB_DIR.exists():
        print(f"Dossier web introuvable : {WEB_DIR}")
        return 1

    package_json = WEB_DIR / "package.json"
    if not package_json.exists():
        print("web/package.json manquant — restaurez les sources Next.js du projet.")
        return 1

    npm = _find_npm()
    if npm is None:
        print("npm introuvable. Installez Node.js LTS ou ajoutez C:\\Program Files\\nodejs au PATH.")
        return 1

    from launcher.ports import is_port_in_use, prepare_port

    try:
        port = prepare_port(port, kill=kill, auto_port=auto_port)
    except RuntimeError as exc:
        print(exc)
        return 1

    print(f"Web companion : http://127.0.0.1:{port}")
    print("Arret : Ctrl+C")
    env = {**os.environ, "PORT": str(port)}
    command = [npm, "run", "dev", "--", "-p", str(port)]

    try:
        result = subprocess.run(command, cwd=WEB_DIR, env=env)
    except KeyboardInterrupt:
        return 0

    if result.returncode not in (0, None):
        if is_port_in_use(port) and auto_port:
            fallback = port + 1
            while fallback < port + 20 and is_port_in_use(fallback):
                fallback += 1
            if fallback < port + 20:
                print(f"Echec sur {port} — nouvelle tentative sur {fallback}...")
                return run_web(port=fallback, kill=False, auto_port=False)
        return result.returncode or 1

    return 0


if __name__ == "__main__":
    kill = "--kill" in sys.argv
    port = 3000
    for index, arg in enumerate(sys.argv[1:], start=1):
        if arg == "--port" and index < len(sys.argv) - 1:
            port = int(sys.argv[index + 1])
    raise SystemExit(run_web(port=port, kill=kill))
