from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


_CORRUPT_MSG_LINE = "        corrupt_msg = 'MD5 hash mismatch, possible file corruption'\n"
_RECOGNITION_MARKER = "        # recognition model\n"


def _patch_source(text: str) -> str | None:
    before_recognition = text.split(_RECOGNITION_MARKER, 1)[0]
    if "corrupt_msg = " in before_recognition:
        return None
    if _RECOGNITION_MARKER not in text:
        return None
    return text.replace(_RECOGNITION_MARKER, _CORRUPT_MSG_LINE + _RECOGNITION_MARKER, 1)


def _mark_patched(module: ModuleType) -> None:
    module._dt_corrupt_msg_patch = True
    try:
        import easyocr

        easyocr._dt_corrupt_msg_patch = True
    except ImportError:
        pass


def _load_reader_from_vendor(vendor_path: Path, easyocr_module: ModuleType) -> None:
    package_dir = Path(easyocr_module.__file__).resolve().parent
    spec = importlib.util.spec_from_file_location(
        easyocr_module.__name__,
        vendor_path,
        submodule_search_locations=[str(package_dir)],
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossible de charger le patch OCR : {vendor_path}")

    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    if not hasattr(loaded, "Reader"):
        raise RuntimeError("Patch OCR invalide : classe Reader absente")

    easyocr_module.Reader = loaded.Reader
    try:
        import easyocr

        easyocr.Reader = loaded.Reader
    except ImportError:
        pass
    _mark_patched(easyocr_module)


def write_patched_easyocr_vendor(target_dir: Path) -> Path | None:
    """Genere une copie patchee d'easyocr.py pour le bundle PyInstaller."""
    try:
        import easyocr.easyocr as easyocr_module
    except ImportError:
        return None

    source_path = Path(easyocr_module.__file__)
    if not source_path.is_file():
        return None

    text = source_path.read_text(encoding="utf-8")
    patched_text = _patch_source(text) or text
    vendor_dir = target_dir / "easyocr_vendor"
    vendor_dir.mkdir(parents=True, exist_ok=True)
    vendor_file = vendor_dir / "easyocr.py"
    vendor_file.write_text(patched_text, encoding="utf-8")
    return vendor_file


def apply_easyocr_corrupt_msg_patch() -> None:
    """Fix easyocr bug: corrupt_msg used in Reader.__init__ before it is defined."""
    try:
        import easyocr.easyocr as easyocr_module
    except ImportError:
        return

    if getattr(easyocr_module, "_dt_corrupt_msg_patch", False):
        return

    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            vendor = Path(meipass) / "easyocr_vendor" / "easyocr.py"
            if vendor.is_file():
                try:
                    _load_reader_from_vendor(vendor, easyocr_module)
                    return
                except Exception:
                    pass
        _mark_patched(easyocr_module)
        return

    source_path = Path(easyocr_module.__file__)
    if not source_path.is_file():
        _mark_patched(easyocr_module)
        return

    text = source_path.read_text(encoding="utf-8")
    patched_text = _patch_source(text)
    if patched_text is None:
        _mark_patched(easyocr_module)
        return

    try:
        source_path.write_text(patched_text, encoding="utf-8")
        _mark_patched(easyocr_module)
        return
    except OSError:
        pass

    try:
        _load_reader_from_vendor_from_text(patched_text, easyocr_module)
    except Exception:
        _mark_patched(easyocr_module)


def _load_reader_from_vendor_from_text(source: str, easyocr_module: ModuleType) -> None:
    vendor_dir = Path(easyocr_module.__file__).resolve().parent.parent / ".easyocr_patch"
    vendor_dir.mkdir(parents=True, exist_ok=True)
    vendor_file = vendor_dir / "easyocr.py"
    vendor_file.write_text(source, encoding="utf-8")
    _load_reader_from_vendor(vendor_file, easyocr_module)
