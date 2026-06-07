"""Runtime hook PyInstaller : charge les DLL bundlees (PyQt, OpenCV, Torch, etc.)."""

from __future__ import annotations

import os
import sys


def _register_dll_directories(base: str) -> None:
    candidates = (
        base,
        os.path.join(base, "PyQt6", "Qt6", "bin"),
        os.path.join(base, "cv2"),
        os.path.join(base, "torch", "lib"),
        os.path.join(base, "scipy.libs"),
        os.path.join(base, "numpy.libs"),
        os.path.join(base, "shapely.libs"),
    )

    path_parts = [base]
    for folder in candidates:
        if os.path.isdir(folder):
            path_parts.append(folder)
            if hasattr(os, "add_dll_directory"):
                try:
                    os.add_dll_directory(folder)
                except OSError:
                    pass

    os.environ["PATH"] = os.pathsep.join(path_parts + [os.environ.get("PATH", "")])


if getattr(sys, "frozen", False):
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        _register_dll_directories(meipass)
