from __future__ import annotations


class GameDetectionService:

    PROCESS_NAMES = ("Diablo III64.exe", "Diablo III.exe")

    def is_running(self) -> bool:
        import psutil

        for process in psutil.process_iter(["name"]):
            if process.info["name"] in self.PROCESS_NAMES:
                return True

        return False
