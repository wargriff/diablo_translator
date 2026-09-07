from typing import Any

__all__ = ["OCRService"]


def __getattr__(name: str) -> Any:
    if name == "OCRService":
        from src.ocr.ocr_service import OCRService

        return OCRService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
