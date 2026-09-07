from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from src.capture.display_service import DisplayService


class DisplayServiceTests(unittest.TestCase):

    def test_list_monitors_returns_empty_when_mss_fails(self) -> None:
        fake_mss = MagicMock()
        fake_mss.MSS.side_effect = OSError("no display")
        fake_mss.mss.side_effect = OSError("no display")
        with patch.dict("sys.modules", {"mss": fake_mss}):
            self.assertEqual(DisplayService.list_monitors(), ())

    def test_primary_monitor_falls_back_when_empty(self) -> None:
        with patch.object(DisplayService, "list_monitors", return_value=()):
            monitor = DisplayService.primary_monitor()
        self.assertEqual(monitor.width, 1920)
        self.assertEqual(monitor.height, 1080)


if __name__ == "__main__":
    unittest.main()
