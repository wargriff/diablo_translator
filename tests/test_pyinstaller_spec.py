import unittest
from pathlib import Path


class PyInstallerSpecTests(unittest.TestCase):

    def test_spec_does_not_bundle_dependency_injector(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        spec_path = project_root / "build" / "diablo_translator.spec"
        content = spec_path.read_text(encoding="utf-8")

        self.assertNotIn("dependency_injector", content)
        self.assertIn('collect_submodules("src")', content)
        self.assertIn("src.bootstrap.app", content)


if __name__ == "__main__":
    unittest.main()
