from __future__ import annotations

import os
import sys
from pathlib import Path


def bootstrap() -> Path:
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
