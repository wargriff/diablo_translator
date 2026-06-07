"""Script de build PyInstaller pour Diablo Translator."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

BUILD_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BUILD_DIR.parent


def main() -> int:
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
