from __future__ import annotations

from pathlib import Path

from src.application.config_profiles import PROFILE_CATALOG
from src.game_detection import SUPPORTED_GAMES
from src.infrastructure.config_manager import ConfigManager
from src.infrastructure.paths import BUILD_DIR, PROJECT_ROOT


def format_preset_preview() -> str:
    config = ConfigManager.load()
    lines: list[str] = [
        "=" * 60,
        "DIABLO TRANSLATOR — APERCU PRESET (avant build exe)",
        "=" * 60,
        "",
        "CONFIG UTILISATEUR ACTUELLE",
        "-" * 40,
        f"  Langue           : {config.language}",
        f"  Overlay compact  : {config.overlay_compact}",
        f"  Toujours devant  : {config.always_on_top}",
        f"  OCR auto         : {config.auto_start_monitor}",
        f"  Zone chat        : {config.chat_region_preset}",
        f"  Profil résolution: {config.resolution_profile}",
        f"  Jeu favori launch: {config.preferred_launch_game}",
        "",
        "CHEMINS EXE LAUNCHER",
        "-" * 40,
    ]

    for game in SUPPORTED_GAMES:
        path_map = {
            "d3": config.d3_exe_path,
            "d4": config.d4_exe_path,
            "immortal": config.immortal_exe_path,
        }
        path = path_map.get(game.key, "") or "(non configuré)"
        lines.append(f"  {game.title:<18} : {path}")

    lines.extend(
        [
            "",
            "PROFILS PRO DISPONIBLES (Réglages)",
            "-" * 40,
        ]
    )
    for key, meta in PROFILE_CATALOG.items():
        lines.append(f"  [{key}]")
        lines.append(f"    {meta['title']}")
        lines.append(f"    {meta['subtitle']}")
        lines.append("")

    dist_exe = BUILD_DIR / "dist" / "DiabloTranslator.exe"
    spec_path = BUILD_DIR / "diablo_translator.spec"
    lines.extend(
        [
            "BUILD EXE (prochaine étape)",
            "-" * 40,
            f"  Commande         : py -3 build\\build.py --pro",
            f"  Spec PyInstaller   : {spec_path}",
            f"  Sortie exe         : {dist_exe}",
            f"  Exe existant       : {'oui' if dist_exe.exists() else 'non'}",
        ]
    )
    if dist_exe.exists():
        size_mb = dist_exe.stat().st_size / (1024 * 1024)
        lines.append(f"  Taille actuelle    : {size_mb:.1f} Mo")

    lines.extend(
        [
            "",
            "MODULES CRITIQUES INCLUS (spec)",
            "-" * 40,
            "  PyQt6, easyocr, torch, sounddevice, speech_recognition",
            "  src.bootstrap.app, src.infrastructure.container",
            "",
            f"Racine projet : {PROJECT_ROOT}",
            "=" * 60,
        ]
    )
    return "\n".join(lines)


def run_preset_preview() -> int:
    print(format_preset_preview())
    return 0
