import unittest

from src.ocr.easyocr_patch import _CORRUPT_MSG_LINE, _patch_source


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


if __name__ == "__main__":
    unittest.main()
