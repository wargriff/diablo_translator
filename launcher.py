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
    if not getattr(sys, "frozen", False):
        return

    import traceback

    log_path = Path(sys.executable).resolve().parent / "logs" / "crash.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    previous_hook = sys.excepthook

    def _hook(exc_type, exc, tb) -> None:
        try:
            log_path.write_text(
                "".join(traceback.format_exception(exc_type, exc, tb)),
                encoding="utf-8",
            )
        except Exception:
            pass
        previous_hook(exc_type, exc, tb)

    sys.excepthook = _hook


def bootstrap() -> Path:
    _configure_fast_startup()
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
