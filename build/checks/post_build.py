from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class CheckResult:

    name: str
    ok: bool
    detail: str = ""


def _check_exe_exists(dist_exe: Path) -> CheckResult:
    if not dist_exe.exists():
        return CheckResult("Exe genere", False, str(dist_exe))
    size_mb = dist_exe.stat().st_size / (1024 * 1024)
    if size_mb < 80:
        return CheckResult(
            "Exe genere",
            False,
            f"Trop petit ({size_mb:.1f} Mo) — build incomplet?",
        )
    return CheckResult("Exe genere", True, f"{size_mb:.1f} Mo")


def _check_frozen_verify(dist_exe: Path, dist_dir: Path) -> CheckResult:
    try:
        proc = subprocess.run(
            [str(dist_exe), "verify"],
            cwd=str(dist_dir),
            capture_output=True,
            text=True,
            timeout=180,
        )
    except subprocess.TimeoutExpired:
        return CheckResult("Verification frozen", False, "Timeout 180s")

    detail = (proc.stdout or proc.stderr or "").strip()[-400:]
    return CheckResult(
        "Verification frozen",
        proc.returncode == 0,
        detail or f"code {proc.returncode}",
    )


def _check_pe_version(dist_exe: Path) -> CheckResult:
    try:
        import win32api  # type: ignore

        info = win32api.GetFileVersionInfo(str(dist_exe), "\\")
        ms = info["FileVersionMS"]
        ls = info["FileVersionLS"]
        version = f"{win32api.HIWORD(ms)}.{win32api.LOWORD(ms)}.{win32api.HIWORD(ls)}.{win32api.LOWORD(ls)}"
        return CheckResult("Version PE", True, version)
    except Exception:
        return CheckResult("Version PE", True, "Non verifiee (pywin32 optionnel)")


def run_post_build_checks(dist_exe: Path, *, verify_runtime: bool = True) -> tuple[bool, list[CheckResult]]:
    dist_dir = dist_exe.parent
    results = [
        _check_exe_exists(dist_exe),
        _check_pe_version(dist_exe),
    ]

    if verify_runtime:
        results.append(_check_frozen_verify(dist_exe, dist_dir))

    ok = all(item.ok for item in results)
    return ok, results
