import unittest
from pathlib import Path


class PyInstallerSpecTests(unittest.TestCase):

    def test_spec_includes_dependency_injector_errors(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        spec_path = project_root / "build" / "diablo_translator.spec"
        content = spec_path.read_text(encoding="utf-8")

        self.assertIn("collect_submodules(\"dependency_injector\")", content)
        self.assertIn("dependency_injector.errors", content)


if __name__ == "__main__":
    unittest.main()
