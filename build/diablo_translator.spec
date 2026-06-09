# -*- mode: python ; coding: utf-8 -*-
# Diablo Translator v2 — build bureau uniquement (sans API / web / mobile)

from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules

spec_dir = Path(SPECPATH).resolve()
project_root = spec_dir.parent
build_dir = spec_dir
icon_path = project_root / "assets" / "icons" / "app.ico"
version_path = build_dir / "version_info.txt"
manifest_path = build_dir / "app.manifest"
runtime_hook = str(build_dir / "runtime_hooks" / "pyi_rth_win_dll.py")

src_hiddenimports = collect_submodules("src")
launcher_hiddenimports = collect_submodules("launcher")

hiddenimports = [
    "PyQt6",
    "PyQt6.QtCore",
    "PyQt6.QtGui",
    "PyQt6.QtWidgets",
    "deep_translator",
    "mss",
    "PIL",
    "PIL.Image",
    "psutil",
    "speech_recognition",
    "sounddevice",
    "_sounddevice",
    "langdetect",
    "langdetect.detector_factory",
    "easyocr",
    "cv2",
    "numpy",
    "scipy",
    "scipy.special",
    "shapely",
    "torch",
    "torchvision",
    "src.bootstrap.app",
    "src.programs.cli",
    "launcher.hub",
    "launcher.hub_sounds",
    "launcher.hub_workers",
    "launcher.hub_translator",
    "launcher.processes",
] + src_hiddenimports + launcher_hiddenimports

binaries = []
datas = [
    (str(project_root / "assets"), "assets"),
    (str(project_root / "launcher" / "hub_theme.qss"), "launcher"),
    (str(project_root / ".env.example"), "."),
]

easyocr_vendor_dir = build_dir / "easyocr_vendor"
if easyocr_vendor_dir.is_dir():
    datas.append((str(easyocr_vendor_dir), "easyocr_vendor"))

for package in ("cv2", "torch", "scipy", "numpy", "shapely", "PyQt6", "sounddevice"):
    try:
        binaries += collect_dynamic_libs(package)
    except Exception:
        pass

for package in ("langdetect", "_sounddevice_data"):
    try:
        datas += collect_data_files(package)
    except Exception:
        pass

a = Analysis(
    [str(project_root / "launcher.py")],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[runtime_hook],
    excludes=[
        "matplotlib",
        "notebook",
        "jupyter",
        "pyttsx3",
        "tensorboard",
        "tensorflow",
        "pythoncom",
        "pywintypes",
        "win32com",
        "win32com.client",
        "win32api",
        "win32con",
        "pywin32",
        "fastapi",
        "uvicorn",
        "starlette",
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="DiabloTranslator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_path) if icon_path.exists() else None,
    version=str(version_path) if version_path.exists() else None,
    manifest=str(manifest_path) if manifest_path.exists() else None,
)
