from __future__ import annotations

import unittest
from unittest.mock import patch

from src.infrastructure import agent_debug_log


class AgentDebugLogTests(unittest.TestCase):

    def test_agent_log_is_silent_without_debug_flag(self) -> None:
        with patch.dict("os.environ", {"DT_AGENT_DEBUG": ""}, clear=False):
            with patch.object(agent_debug_log, "_listeners", [lambda payload: None]):
                with patch("builtins.open") as handle:
                    agent_debug_log.agent_log(
                        "test.py:silent",
                        "should not write",
                        hypothesis_id="T",
                    )
                    handle.assert_not_called()

    def test_agent_log_writes_when_debug_enabled(self) -> None:
        recorded: list[dict] = []
        with patch.dict("os.environ", {"DT_AGENT_DEBUG": "1"}, clear=False):
            with patch.object(agent_debug_log, "_listeners", [recorded.append]):
                with patch("builtins.open"):
                    agent_debug_log.agent_log(
                        "test.py:enabled",
                        "debug on",
                        hypothesis_id="T",
                    )
        self.assertEqual(len(recorded), 1)
        self.assertEqual(recorded[0]["message"], "debug on")


if __name__ == "__main__":
    unittest.main()
