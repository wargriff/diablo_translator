from __future__ import annotations

__all__ = ["OCRService"]


def __getattr__(name: str):
    if name == "OCRService":
        from src.ocr.ocr_service import OCRService

        return OCRService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
