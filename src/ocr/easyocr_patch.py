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


def _reload_reader_from_source(module: ModuleType, source: str) -> None:
    patched_name = f"{module.__name__}_patched"
    compiled = compile(source, patched_name, "exec")
    namespace: dict = {}
    exec(compiled, namespace)
    if "Reader" not in namespace:
        return

    module.Reader = namespace["Reader"]
    import easyocr

    easyocr.Reader = namespace["Reader"]
    module._dt_corrupt_msg_patch = True
    easyocr._dt_corrupt_msg_patch = True


def apply_easyocr_corrupt_msg_patch() -> None:
    """Fix easyocr bug: corrupt_msg used in Reader.__init__ before it is defined."""
    try:
        import easyocr
        import easyocr.easyocr as easyocr_module
    except ImportError:
        return

    if getattr(easyocr_module, "_dt_corrupt_msg_patch", False):
        return

    source_path = Path(easyocr_module.__file__)
    text = source_path.read_text(encoding="utf-8")
    patched_text = _patch_source(text)
    if patched_text is None:
        easyocr_module._dt_corrupt_msg_patch = True
        return

    try:
        source_path.write_text(patched_text, encoding="utf-8")
        easyocr_module._dt_corrupt_msg_patch = True
        import easyocr as easyocr_pkg

        easyocr_pkg._dt_corrupt_msg_patch = True
        return
    except OSError:
        pass

    _reload_reader_from_source(easyocr_module, patched_text)

    if easyocr_module.__name__ in sys.modules:
        sys.modules[easyocr_module.__name__]._dt_corrupt_msg_patch = True
