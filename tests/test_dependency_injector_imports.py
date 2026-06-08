import importlib
import unittest


class DependencyInjectorImportTests(unittest.TestCase):

    REQUIRED_MODULES = (
        "dependency_injector",
        "dependency_injector.errors",
        "dependency_injector.providers",
        "dependency_injector.containers",
        "dependency_injector.wiring",
        "dependency_injector.resources",
        "dependency_injector._cwiring",
    )

    def test_required_modules_importable(self) -> None:
        for module_name in self.REQUIRED_MODULES:
            with self.subTest(module=module_name):
                module = importlib.import_module(module_name)
                self.assertIsNotNone(module)

    def test_application_container_importable(self) -> None:
        from src.infrastructure.application_container import ApplicationContainer

        self.assertTrue(hasattr(ApplicationContainer, "config_service"))


if __name__ == "__main__":
    unittest.main()
