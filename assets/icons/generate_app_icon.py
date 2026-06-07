"""Generate high-resolution Windows .ico and PNG app icons for Diablo Translator."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


OUTPUT_DIR = Path(__file__).resolve().parent
MASTER_SIZE = 1024
ICO_SIZES = (16, 20, 24, 32, 40, 48, 64, 96, 128, 256, 512)


def _star_points(
    cx: float,
    cy: float,
    outer_r: float,
    inner_r: float,
    points: int = 5,
) -> list[tuple[float, float]]:
    coords: list[tuple[float, float]] = []
    for index in range(points * 2):
        angle = math.pi / 2 + index * math.pi / points
        radius = outer_r if index % 2 == 0 else inner_r
        coords.append((cx + math.cos(angle) * radius, cy - math.sin(angle) * radius))
    return coords


def render_icon(size: int) -> Image.Image:
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    margin = max(4, size // 14)
    corner_radius = size // 5
    border = max(2, size // 48)

    draw.rounded_rectangle(
        (margin, margin, size - margin, size - margin),
        radius=corner_radius,
        fill=(18, 14, 11, 255),
        outline=(184, 134, 11, 255),
        width=border,
    )

    inner_margin = margin + border * 2
    draw.rounded_rectangle(
        (inner_margin, inner_margin, size - inner_margin, size - inner_margin),
        radius=max(8, corner_radius - border),
        outline=(92, 74, 48, 120),
        width=max(1, border // 2),
    )

    glow_radius = size * 0.34
    glow_box = (
        size / 2 - glow_radius,
        size / 2 - glow_radius * 0.55,
        size / 2 + glow_radius,
        size / 2 + glow_radius * 1.05,
    )
    draw.ellipse(glow_box, fill=(120, 24, 24, 90))

    star_outer = size * 0.22
    star_inner = size * 0.095
    star_center_y = size * 0.43
    star = _star_points(size / 2, star_center_y, star_outer, star_inner)
    draw.polygon(star, fill=(212, 175, 55, 255), outline=(90, 61, 8, 255))

    highlight = _star_points(size / 2, star_center_y, star_outer * 0.55, star_inner * 0.55)
    draw.polygon(highlight, fill=(255, 243, 196, 45))

    line_y1 = size * 0.74
    line_y2 = size * 0.82
    line_width = max(2, size // 28)
    draw.line(
        (size * 0.28, line_y1, size * 0.72, line_y1),
        fill=(184, 134, 11, 230),
        width=line_width,
    )
    draw.line(
        (size * 0.34, line_y2, size * 0.66, line_y2),
        fill=(122, 32, 32, 230),
        width=max(2, line_width - 1),
    )

    if size >= 256:
        image = image.filter(ImageFilter.SHARPEN)

    return image


def main() -> None:
    master = render_icon(MASTER_SIZE)
    png_path = OUTPUT_DIR / "app.png"
    png_hd_path = OUTPUT_DIR / "app_1024.png"
    ico_path = OUTPUT_DIR / "app.ico"

    master.save(png_hd_path, format="PNG", optimize=True)
    master.resize((512, 512), Image.Resampling.LANCZOS).save(png_path, format="PNG", optimize=True)
    master.save(
        ico_path,
        format="ICO",
        sizes=[(size, size) for size in ICO_SIZES],
    )

    print(f"Created {png_hd_path} ({png_hd_path.stat().st_size // 1024} KB)")
    print(f"Created {png_path} ({png_path.stat().st_size // 1024} KB)")
    print(f"Created {ico_path} ({ico_path.stat().st_size // 1024} KB, {len(ICO_SIZES)} sizes)")


if __name__ == "__main__":
    main()
