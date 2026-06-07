"""Install script for Diablo Translator dependencies on Windows."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
REQUIREMENTS = PROJECT_ROOT / "requirements.txt"
VOICE_REQUIREMENTS = PROJECT_ROOT / "requirements-voice.txt"


def run(command: list[str]) -> int:
    print(">", " ".join(command))
    return subprocess.call(command)


def main() -> int:
    steps = [
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
        [sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS)],
    ]

    for command in steps:
        code = run(command)
        if code != 0:
            print("\nEchec installation principale.")
            return code

    if VOICE_REQUIREMENTS.exists():
        print("\nInstallation micro (PyAudio, optionnel)...")
        voice_code = run(
            [sys.executable, "-m", "pip", "install", "-r", str(VOICE_REQUIREMENTS)]
        )
        if voice_code != 0:
            print(
                "\nMicro non installe. Installez : pip install -r requirements-voice.txt"
                "\n  (SoundDevice remplace PyAudio sur Python 3.14+)"
            )

    print("\nVerification des dependances...")
    return run([sys.executable, str(PROJECT_ROOT / "launcher.py"), "check"])


if __name__ == "__main__":
    raise SystemExit(main())
