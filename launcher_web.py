"""Raccourci web — demarre l'API (:8000) puis le companion Next.js."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent
    extra = list(sys.argv[1:])
    if "--kill" not in extra:
        extra = ["--kill", *extra]
    result = subprocess.run(
        [sys.executable, str(root / "launcher.py"), "web", *extra],
        cwd=root,
    )
    code = result.returncode
    return code if code is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
