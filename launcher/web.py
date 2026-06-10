from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = PROJECT_ROOT / "web"


def _ensure_node_modules(npm: Path) -> bool:
    if (WEB_DIR / "node_modules").is_dir():
        return True
    print("Installation web (npm install) — premiere fois...")
    from launcher.nodejs import node_env

    result = subprocess.run(
        [str(npm), "install"],
        cwd=WEB_DIR,
        env=node_env(),
    )
    if result.returncode != 0:
        print("npm install a echoue — verifiez Node.js et votre connexion.")
        return False
    return True


def run_web(*, port: int = 3000, kill: bool = False, auto_port: bool = True, ensure_api: bool = True) -> int:
    if not WEB_DIR.exists():
        print(f"Dossier web introuvable : {WEB_DIR}")
        return 1

    package_json = WEB_DIR / "package.json"
    if not package_json.exists():
        print("web/package.json manquant — restaurez les sources Next.js du projet.")
        return 1

    if ensure_api:
        from launcher.processes import ensure_api_running

        ok, message = ensure_api_running()
        if not ok:
            print(message)
            return 1
        print(message)

    from launcher.nodejs import find_npm, node_env, npm_hint

    npm = find_npm()
    if npm is None:
        print(npm_hint())
        return 1

    print(npm_hint())

    if not _ensure_node_modules(npm):
        return 1

    from launcher.ports import is_port_in_use, prepare_port

    try:
        port = prepare_port(port, kill=kill, auto_port=auto_port)
    except RuntimeError as exc:
        print(exc)
        return 1

    print(f"Web companion : http://127.0.0.1:{port}")
    print("Arret : Ctrl+C")
    env = node_env()
    env["API_PROXY_TARGET"] = f"http://127.0.0.1:8000"
    env.pop("NEXT_PUBLIC_API_URL", None)
    command = [str(npm), "run", "dev", "--", "-p", str(port), "-H", "127.0.0.1"]

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
