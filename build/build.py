"""Script de build PyInstaller pour Diablo Translator."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

BUILD_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BUILD_DIR.parent


def main() -> int:
    icon_path = PROJECT_ROOT / "assets" / "icons" / "app.ico"
    icon_script = PROJECT_ROOT / "assets" / "icons" / "generate_app_icon.py"
    if icon_script.exists() and not icon_path.exists():
        print("Generation de l'icone HD...")
        icon_result = subprocess.run([sys.executable, str(icon_script)], cwd=PROJECT_ROOT)
        if icon_result.returncode != 0:
            print("Echec generation icone.")
            return icon_result.returncode
    elif icon_path.exists():
        print(f"Icone personnalisee : {icon_path}")

    spec = BUILD_DIR / "diablo_translator.spec"
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        str(spec),
        "--distpath",
        str(BUILD_DIR / "dist"),
        "--workpath",
        str(BUILD_DIR / "work"),
        "--noconfirm",
    ]

    print("Build Diablo Translator...")
    result = subprocess.run(command, cwd=PROJECT_ROOT)
    if result.returncode == 0:
        print(f"Build terminé : {BUILD_DIR / 'dist'}")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
