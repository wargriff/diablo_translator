import sys
import unittest
from types import ModuleType
from unittest.mock import patch

from src.ocr.easyocr_patch import _CORRUPT_MSG_LINE, _patch_source, apply_easyocr_corrupt_msg_patch


class EasyOcrPatchTests(unittest.TestCase):

    def test_patch_source_inserts_corrupt_msg(self):
        sample = "        # recognition model\n        separator_list = {}\n"
        patched = _patch_source(sample)
        self.assertIsNotNone(patched)
        assert patched is not None
        self.assertIn("corrupt_msg = ", patched.split("# recognition model")[0])

    def test_patch_source_idempotent(self):
        already = _CORRUPT_MSG_LINE + "        # recognition model\n"
        self.assertIsNone(_patch_source(already))

    def test_frozen_mode_skips_missing_source_file(self):
        fake_parent = ModuleType("easyocr")
        fake_module = ModuleType("easyocr.easyocr")
        fake_module.__file__ = r"C:\Temp\_MEI123\easyocr\easyocr.py"

        saved = {key: sys.modules.get(key) for key in ("easyocr", "easyocr.easyocr")}
        try:
            sys.modules["easyocr"] = fake_parent
            sys.modules["easyocr.easyocr"] = fake_module
            with patch.object(sys, "frozen", True, create=True), patch.object(
                sys, "_MEIPASS", r"C:\Temp\_MEI123", create=True
            ):
                apply_easyocr_corrupt_msg_patch()
            self.assertTrue(fake_module._dt_corrupt_msg_patch)
        finally:
            for key, value in saved.items():
                if value is None:
                    sys.modules.pop(key, None)
                else:
                    sys.modules[key] = value


if __name__ == "__main__":
    unittest.main()
