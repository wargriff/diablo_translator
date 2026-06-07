from src.chat.chat_region import CHAT_REGION_PRESETS, get_preset

__all__ = ["CHAT_REGION_PRESETS", "ChatMonitorService", "get_preset"]


def __getattr__(name: str):
    if name == "ChatMonitorService":
        from src.chat.chat_monitor_service import ChatMonitorService

        return ChatMonitorService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
