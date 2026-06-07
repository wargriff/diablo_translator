# -*- mode: python ; coding: utf-8 -*-

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
    "src.translation.language_detection_service",
    "src.translation.conversation_context",
    "src.translation.translation_service",
    "src.translation.translation_pipeline",
    "src.application.live_chat_service",
    "src.application.in_game_chat_router",
    "src.application.config_profiles",
    "src.capture.capture_region_resolver",
    "src.capture.game_window_service",
    "src.infrastructure.container",
    "src.bootstrap.app",
    "src.programs.cli",
] + src_hiddenimports

binaries = []
datas = [
    (str(project_root / "assets"), "assets"),
    (str(project_root / ".env.example"), "."),
]

for package in ("cv2", "torch", "scipy", "numpy", "shapely", "PyQt6"):
    try:
        binaries += collect_dynamic_libs(package)
    except Exception:
        pass

try:
    datas += collect_data_files("langdetect")
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
