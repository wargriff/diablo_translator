"""Pipeline de build PyInstaller pro pour Diablo Translator."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

BUILD_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BUILD_DIR.parent
DIST_DIR = BUILD_DIR / "dist"
DIST_EXE = DIST_DIR / "DiabloTranslator.exe"
WORK_DIR = BUILD_DIR / "work"


def _print_phase(title: str) -> None:
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def _print_results(results) -> None:
    for item in results:
        status = "OK" if item.ok else "ECHEC"
        detail = f" — {item.detail}" if item.detail else ""
        print(f"  [{status}] {item.name}{detail}")


def _ensure_import_path() -> None:
    root = str(PROJECT_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)


def _stop_running_exe() -> bool:
    import psutil

    target = DIST_EXE.resolve()
    target_name = target.name.casefold()
    processes: list[int] = []

    for process in psutil.process_iter(["pid", "name", "exe"]):
        try:
            exe = process.info.get("exe")
            name = process.info.get("name") or ""
            if exe and Path(exe).resolve() == target:
                processes.append(process.info["pid"])
            elif name.casefold() == target_name:
                processes.append(process.info["pid"])
        except (psutil.Error, OSError, ValueError):
            continue

    if not processes:
        return True

    print("Fermeture de DiabloTranslator.exe en cours...")
    for pid in processes:
        try:
            psutil.Process(pid).terminate()
            print(f"  - PID {pid}")
        except psutil.Error as exc:
            print(f"  - PID {pid} : {exc}")

    deadline = time.time() + 10.0
    while time.time() < deadline:
        still_running = False
        for process in psutil.process_iter(["pid", "name", "exe"]):
            try:
                if process.info["pid"] in processes and process.is_running():
                    still_running = True
                    break
            except psutil.Error:
                continue
        if not still_running:
            time.sleep(0.5)
            return True
        time.sleep(0.5)

    return False


def _run_pre_build(*, run_tests: bool) -> int:
    _print_phase("PHASE 1 — Controles pre-build")
    _ensure_import_path()
    from build.checks.pre_build import run_pre_build_checks
    from src.ocr.easyocr_patch import apply_easyocr_corrupt_msg_patch

    apply_easyocr_corrupt_msg_patch()

    ok, results = run_pre_build_checks(
        PROJECT_ROOT,
        DIST_EXE,
        run_tests=run_tests,
    )
    _print_results(results)
    if not ok:
        print("\nBuild annule : corrigez les erreurs ci-dessus.")
        print("Astuce : py -3 build\\install_dependencies.py")
        return 1
    print("\nTous les controles pre-build sont OK.")
    return 0


def _unblock_python_environment() -> None:
    script = BUILD_DIR / "unblock_site_packages.ps1"
    if not script.exists():
        return

    print("Deblocage DLL Python (Smart App Control / MOTW)...")
    subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script),
            "-PythonExe",
            "py",
        ],
        cwd=PROJECT_ROOT,
    )


def _prepare_environment() -> int:
    _print_phase("PHASE 2 — Preparation")

    _unblock_python_environment()

    if DIST_EXE.exists() and not _stop_running_exe():
        print("\nERREUR : DiabloTranslator.exe est verrouille.")
        print("Fermez l'application puis relancez le build.")
        return 1

    icon_path = PROJECT_ROOT / "assets" / "icons" / "app.ico"
    icon_script = PROJECT_ROOT / "assets" / "icons" / "generate_app_icon.py"
    if icon_script.exists() and (not icon_path.exists() or icon_path.stat().st_size < 1024):
        print("Generation icone HD...")
        result = subprocess.run([sys.executable, str(icon_script)], cwd=PROJECT_ROOT)
        if result.returncode != 0:
            return result.returncode
    elif icon_path.exists():
        print(f"Icone : {icon_path} ({icon_path.stat().st_size} octets)")

    DIST_DIR.mkdir(parents=True, exist_ok=True)

    _ensure_import_path()
    from src.ocr.easyocr_patch import (
        apply_easyocr_corrupt_msg_patch,
        write_patched_easyocr_vendor,
    )

    apply_easyocr_corrupt_msg_patch()
    vendor_file = write_patched_easyocr_vendor(BUILD_DIR)
    if vendor_file:
        print(f"Patch OCR bundle : {vendor_file}")
    else:
        print("AVERTISSEMENT : patch OCR vendor non genere (EasyOCR absent ?)")

    return 0


def _run_pyinstaller(*, clean: bool) -> int:
    _print_phase("PHASE 3 — PyInstaller (DLL + manifest + runtime hooks)")
    print("(WARNING tensorboard / nvcuda = normal, pas une erreur)")

    spec = BUILD_DIR / "diablo_translator.spec"
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        str(spec),
        "--distpath",
        str(DIST_DIR),
        "--workpath",
        str(WORK_DIR),
        "--noconfirm",
    ]
    if clean:
        command.append("--clean")

    return subprocess.run(command, cwd=PROJECT_ROOT).returncode


def _run_post_build(*, verify_runtime: bool) -> int:
    _print_phase("PHASE 4 — Verification post-build")
    _ensure_import_path()
    from build.checks.post_build import run_post_build_checks

    ok, results = run_post_build_checks(DIST_EXE, verify_runtime=verify_runtime)
    _print_results(results)
    if not ok:
        print("\nBuild termine mais verification post-build en echec.")
        return 1
    return 0


def _run_windows_security() -> int:
    _print_phase("PHASE 5 — Securite Windows (MOTW / debloquer)")
    script = BUILD_DIR / "windows_security.ps1"
    if not script.exists():
        print("Script securite absent — etape ignoree.")
        return 0

    return subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script),
            "-DistPath",
            str(DIST_DIR),
        ],
        cwd=PROJECT_ROOT,
    ).returncode


def _create_shortcut() -> None:
    script = BUILD_DIR / "create_desktop_shortcut.ps1"
    if script.exists():
        subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script),
            ],
            cwd=PROJECT_ROOT,
        )


def main(argv: list[str] | None = None) -> int:
    _ensure_import_path()

    parser = argparse.ArgumentParser(description="Build pro Diablo Translator")
    parser.add_argument(
        "--pro",
        action="store_true",
        help="Pipeline complet : tests + clean + securite Windows",
    )
    parser.add_argument(
        "--tests",
        action="store_true",
        help="Lancer les tests unitaires avant build",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="PyInstaller --clean",
    )
    parser.add_argument(
        "--skip-verify",
        action="store_true",
        help="Ne pas lancer DiabloTranslator.exe verify",
    )
    parser.add_argument(
        "--skip-security",
        action="store_true",
        help="Ne pas debloquer MOTW post-build",
    )
    parser.add_argument(
        "--shortcut",
        action="store_true",
        help="Creer le raccourci bureau apres build",
    )
    args = parser.parse_args(argv)

    pro_mode = args.pro
    run_tests = args.tests or pro_mode
    clean = args.clean or pro_mode
    verify_runtime = not args.skip_verify
    run_security = not args.skip_security
    create_shortcut = args.shortcut or pro_mode

    print("Diablo Translator — Build Pipeline Pro")
    print(f"Projet : {PROJECT_ROOT}")

    if _run_pre_build(run_tests=run_tests) != 0:
        return 1

    if _prepare_environment() != 0:
        return 1

    if _run_pyinstaller(clean=clean) != 0:
        print("\nPyInstaller a echoue.")
        return 1

    if _run_post_build(verify_runtime=verify_runtime) != 0:
        return 1

    if run_security and _run_windows_security() != 0:
        print("\nAttention : etape securite Windows incomplete.")

    if create_shortcut:
        _create_shortcut()

    _print_phase("BUILD REUSSI")
    print(f"Exe : {DIST_EXE}")
    print(f"Lancer : build\\launch_app.ps1")
    print(f"         ou double-clic sur {DIST_EXE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
