"""Generate Windows .ico and PNG app icons for Diablo Translator."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw


OUTPUT_DIR = Path(__file__).resolve().parent
SIZES = (16, 32, 48, 64, 128, 256)


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _star_points(cx: float, cy: float, outer_r: float, inner_r: float, points: int = 5) -> list[tuple[float, float]]:
    coords: list[tuple[float, float]] = []
    for index in range(points * 2):
        angle = math.pi / 2 + index * math.pi / points
        radius = outer_r if index % 2 == 0 else inner_r
        coords.append((cx + math.cos(angle) * radius, cy - math.sin(angle) * radius))
    return coords


def render_icon(size: int) -> Image.Image:
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    margin = max(2, size // 16)
    radius = size // 5

    draw.rounded_rectangle(
        (margin, margin, size - margin, size - margin),
        radius=radius,
        fill=(18, 14, 11, 255),
        outline=(184, 134, 11, 255),
        width=max(1, size // 32),
    )

    glow_radius = size * 0.34
    glow_box = (
        size / 2 - glow_radius,
        size / 2 - glow_radius * 0.55,
        size / 2 + glow_radius,
        size / 2 + glow_radius * 1.05,
    )
    draw.ellipse(glow_box, fill=(120, 24, 24, 70))

    star_outer = size * 0.22
    star_inner = size * 0.095
    star_center_y = size * 0.43
    star = _star_points(size / 2, star_center_y, star_outer, star_inner)
    draw.polygon(star, fill=(212, 175, 55, 255), outline=(90, 61, 8, 255))

    line_y1 = size * 0.74
    line_y2 = size * 0.82
    line_width = max(1, size // 32)
    draw.line(
        (size * 0.28, line_y1, size * 0.72, line_y1),
        fill=(184, 134, 11, 220),
        width=line_width,
    )
    draw.line(
        (size * 0.34, line_y2, size * 0.66, line_y2),
        fill=(122, 32, 32, 220),
        width=max(1, line_width - 1),
    )

    return image


def main() -> None:
    icons = [render_icon(size) for size in SIZES]
    png_path = OUTPUT_DIR / "app.png"
    ico_path = OUTPUT_DIR / "app.ico"

    icons[-1].save(png_path, format="PNG")
    icons[0].save(
        ico_path,
        format="ICO",
        sizes=[(icon.width, icon.height) for icon in icons],
        append_images=icons[1:],
    )

    print(f"Created {png_path}")
    print(f"Created {ico_path}")


if __name__ == "__main__":
    main()
