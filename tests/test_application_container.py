import unittest

from src.infrastructure.application_container import ApplicationContainer


class ApplicationContainerTests(unittest.TestCase):

    def test_services_wire_without_dependency_injector(self) -> None:
        container = ApplicationContainer()
        container.init_resources()

        config = container.config_service()
        pipeline = container.translation_pipeline()
        live_chat = container.live_chat_service()
        worker = container.translation_worker()
        launch = container.game_launch_orchestrator()

        self.assertIsNotNone(config.config)
        self.assertIs(pipeline, container.translation_pipeline())
        self.assertIs(live_chat, container.live_chat_service())
        self.assertIs(worker, container.translation_worker())
        self.assertIs(launch, container.game_launch_orchestrator())

        container.shutdown_resources()

    def test_container_facade_boots_and_shuts_down(self) -> None:
        from src.infrastructure.container import Container

        app = Container()
        self.assertIsNotNone(app.pipeline)
        self.assertIsNotNone(app.game_launch)
        app.shutdown()


if __name__ == "__main__":
    unittest.main()
