from __future__ import annotations

import os
import sys
from pathlib import Path


def _configure_fast_startup() -> None:
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
    os.environ.setdefault("PYTHONUTF8", "1")


def _install_frozen_crash_logger() -> None:
    import traceback
    from pathlib import Path

    from src.infrastructure.agent_debug_log import LOG_MIRROR_PATH, agent_log

    log_dir = (
        Path(sys.executable).resolve().parent / "logs"
        if getattr(sys, "frozen", False)
        else LOG_MIRROR_PATH.parent
    )
    log_dir.mkdir(parents=True, exist_ok=True)
    crash_path = log_dir / "crash.log"
    native_path = log_dir / "crash_native.log"

    try:
        import faulthandler

        native_handle = open(native_path, "a", encoding="utf-8")
        faulthandler.enable(file=native_handle, all_threads=True)
    except Exception:
        native_handle = None

    previous_hook = sys.excepthook

    def _hook(exc_type, exc, tb) -> None:
        detail = "".join(traceback.format_exception(exc_type, exc, tb))
        try:
            crash_path.write_text(detail, encoding="utf-8")
        except Exception:
            pass
        agent_log(
            "launcher.py:excepthook",
            "Exception non geree",
            hypothesis_id="D",
            run_id="user-verify",
            data={"error": str(exc), "traceback": detail[-800:]},
        )
        previous_hook(exc_type, exc, tb)

    sys.excepthook = _hook


def bootstrap() -> Path:
    _configure_fast_startup()

    from src.infrastructure.agent_debug_log import LOG_FALLBACK_PATH, agent_log

    agent_log(
        "launcher.py:bootstrap",
        "Bootstrap demarre",
        hypothesis_id="D",
        run_id="user-verify",
        data={"fallbackLog": str(LOG_FALLBACK_PATH)},
    )

    _install_frozen_crash_logger()

    if getattr(sys, "frozen", False):
        from src.infrastructure.paths import PROJECT_ROOT, ensure_project_dirs

        ensure_project_dirs()
        os.chdir(PROJECT_ROOT)
        return PROJECT_ROOT

    root = Path(__file__).resolve().parent
    root_str = str(root)

    if root_str not in sys.path:
        sys.path.insert(0, root_str)

    os.chdir(root)

    from src.infrastructure.paths import ensure_project_dirs

    ensure_project_dirs()
    return root


def main(argv: list[str] | None = None) -> int:
    bootstrap()

    from src.programs.cli import build_parser, dispatch

    parser = build_parser()
    args = parser.parse_args(argv)
    return dispatch(args)


if __name__ == "__main__":
    raise SystemExit(main())
