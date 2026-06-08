from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MOBILE_DIR = PROJECT_ROOT / "mobile"


def _find_flutter() -> str | None:
    flutter = shutil.which("flutter")
    if flutter:
        return flutter
    candidate = Path("C:/src/flutter/bin/flutter.bat")
    if candidate.exists():
        return str(candidate)
    return None


def run_mobile(*, device: str | None = None) -> int:
    if not MOBILE_DIR.exists():
        print(f"Dossier mobile introuvable : {MOBILE_DIR}")
        return 1

    flutter = _find_flutter()
    if flutter is None:
        print("Flutter introuvable. Installez-le ou ajoutez C:\\src\\flutter\\bin au PATH.")
        return 1

    print("Diablo Translator Mobile (Flutter)")
    print("iPhone : necessite un Mac + Xcode pour build/install sur appareil.")
    print()

    pub_get = subprocess.run([flutter, "pub", "get"], cwd=MOBILE_DIR)
    if pub_get.returncode != 0:
        return pub_get.returncode or 1

    command = [flutter, "run"]
    if device:
        command.extend(["-d", device])

    return subprocess.run(command, cwd=MOBILE_DIR).returncode or 0
