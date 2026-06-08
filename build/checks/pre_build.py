from __future__ import annotations

import importlib
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class CheckResult:

    name: str
    ok: bool
    detail: str = ""


REQUIRED_IMPORTS: tuple[tuple[str, str], ...] = (
    ("PyQt6", "PyQt6"),
    ("cv2", "opencv-python"),
    ("numpy", "numpy"),
    ("PIL", "pillow"),
    ("easyocr", "easyocr"),
    ("torch", "torch"),
    ("mss", "mss"),
    ("psutil", "psutil"),
    ("langdetect", "langdetect"),
    ("deep_translator", "deep-translator"),
    ("pyperclip", "pyperclip"),
)

REQUIRED_SOURCE_MODULES: tuple[str, ...] = (
    "src.translation.language_detection_service",
    "src.translation.conversation_context",
    "src.translation.translation_service",
    "src.translation.translation_pipeline",
    "src.application.live_chat_service",
    "src.application.in_game_chat_router",
    "src.capture.capture_region_resolver",
    "src.infrastructure.container",
    "src.infrastructure.application_container",
    "src.bootstrap.app",
    "src.programs.cli",
)

REQUIRED_FILES: tuple[tuple[Path, str, int], ...] = (
    # path relative to project root, label, min_bytes
)


def _check_python_version() -> CheckResult:
    major, minor = sys.version_info[:2]
    if major == 3 and minor >= 12:
        return CheckResult("Python", True, f"{major}.{minor}")
    return CheckResult(
        "Python",
        False,
        f"{major}.{minor} — Python 3.12+ recommande",
    )


def _check_pyinstaller() -> CheckResult:
    try:
        import PyInstaller  # noqa: F401

        return CheckResult("PyInstaller", True, "installe")
    except ImportError:
        return CheckResult("PyInstaller", False, "pip install pyinstaller")


def _check_disk_space(project_root: Path, min_mb: int = 2500) -> CheckResult:
    usage = shutil.disk_usage(project_root)
    free_mb = usage.free // (1024 * 1024)
    ok = free_mb >= min_mb
    return CheckResult(
        "Espace disque",
        ok,
        f"{free_mb} Mo libres (min {min_mb} Mo)",
    )


def _check_imports() -> list[CheckResult]:
    results: list[CheckResult] = []
    for module_name, package_name in REQUIRED_IMPORTS:
        try:
            importlib.import_module(module_name)
            results.append(CheckResult(f"Import {package_name}", True))
        except ImportError as exc:
            results.append(
                CheckResult(
                    f"Import {package_name}",
                    False,
                    str(exc),
                )
            )
    return results


def _check_source_modules(project_root: Path) -> list[CheckResult]:
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    results: list[CheckResult] = []
    for module_name in REQUIRED_SOURCE_MODULES:
        try:
            importlib.import_module(module_name)
            results.append(CheckResult(f"Module {module_name}", True))
        except ModuleNotFoundError as exc:
            results.append(
                CheckResult(f"Module {module_name}", False, str(exc))
            )
    return results


def _check_assets(project_root: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    icon = project_root / "assets" / "icons" / "app.ico"
    if icon.exists() and icon.stat().st_size >= 1024:
        results.append(CheckResult("Icone app.ico", True, f"{icon.stat().st_size} octets"))
    else:
        results.append(
            CheckResult(
                "Icone app.ico",
                False,
                "Fichier absent ou trop petit (< 1 Ko)",
            )
        )

    manifest = project_root / "build" / "app.manifest"
    results.append(
        CheckResult(
            "Manifest Windows",
            manifest.exists(),
            str(manifest) if manifest.exists() else "build/app.manifest manquant",
        )
    )

    version_info = project_root / "build" / "version_info.txt"
    results.append(
        CheckResult(
            "Version info",
            version_info.exists(),
            str(version_info) if version_info.exists() else "manquant",
        )
    )

    theme = project_root / "assets" / "themes" / "diablo_dark.qss"
    results.append(
        CheckResult(
            "Theme UI",
            theme.exists(),
            "diablo_dark.qss",
        )
    )
    return results


def _check_exe_lock(dist_exe: Path) -> CheckResult:
    if not dist_exe.exists():
        return CheckResult("Exe verrouille", True, "Aucun exe existant")

    try:
        with open(dist_exe, "r+b"):
            pass
        return CheckResult("Exe verrouille", True, "Ecriture OK")
    except PermissionError:
        return CheckResult(
            "Exe verrouille",
            False,
            "Fermez DiabloTranslator.exe avant le build",
        )


def run_pre_build_checks(
    project_root: Path,
    dist_exe: Path,
    *,
    run_tests: bool = False,
) -> tuple[bool, list[CheckResult]]:
    results: list[CheckResult] = [
        _check_python_version(),
        _check_pyinstaller(),
        _check_disk_space(project_root),
        _check_exe_lock(dist_exe),
    ]
    results.extend(_check_imports())
    results.extend(_check_source_modules(project_root))
    results.extend(_check_assets(project_root))

    if run_tests:
        import subprocess

        proc = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"],
            cwd=project_root,
            capture_output=True,
            text=True,
        )
        results.append(
            CheckResult(
                "Tests unitaires",
                proc.returncode == 0,
                proc.stdout[-300:] if proc.stdout else proc.stderr[-300:],
            )
        )

    ok = all(item.ok for item in results)
    return ok, results
