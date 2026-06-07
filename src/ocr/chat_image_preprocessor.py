from __future__ import annotations

from typing import Any

from PIL import Image, ImageChops, ImageEnhance, ImageOps


class ChatImagePreprocessor:

    @classmethod
    def prepare(cls, image: Any, *, enabled: bool = True) -> Any:
        if image is None or not enabled:
            return image

        rgb = image.convert("RGB")
        red, green, blue = rgb.split()
        # Diablo chat uses colored text (whisper pink, system green...) on dark UI.
        max_channel = ImageChops.lighter(ImageChops.lighter(red, green), blue)
        scaled = max_channel.resize(
            (max_channel.width * 2, max_channel.height * 2),
            Image.Resampling.LANCZOS,
        )
        contrast = ImageEnhance.Contrast(scaled).enhance(2.4)
        sharp = ImageEnhance.Sharpness(contrast).enhance(1.8)
        return ImageOps.autocontrast(sharp, cutoff=2)
