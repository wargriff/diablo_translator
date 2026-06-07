"""Script de build PyInstaller pour Diablo Translator."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

BUILD_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BUILD_DIR.parent

REQUIRED_MODULES = (
    "src.translation.language_detection_service",
    "src.translation.conversation_context",
    "src.translation.translation_service",
    "src.translation.translation_pipeline",
    "src.infrastructure.container",
    "src.bootstrap.app",
)


def _verify_source_modules() -> int:
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    missing: list[str] = []
    for module_name in REQUIRED_MODULES:
        try:
            __import__(module_name)
        except ModuleNotFoundError:
            missing.append(module_name)

    if missing:
        print("Modules source manquants avant build :")
        for name in missing:
            print(f"  - {name}")
        print("\nLancez git pull puis reessayez.")
        return 1

    return 0


def main() -> int:
    verify_code = _verify_source_modules()
    if verify_code != 0:
        return verify_code
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
