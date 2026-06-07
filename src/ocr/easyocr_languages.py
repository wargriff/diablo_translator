from __future__ import annotations

CYRILLIC_LANGS = frozenset(
    {
        "ru",
        "rs_cyrillic",
        "be",
        "bg",
        "uk",
        "mn",
    }
)


def split_easyocr_language_groups(
    languages: tuple[str, ...],
) -> tuple[tuple[str, ...], tuple[str, ...] | None]:
    """EasyOCR: cyrillic scripts must not share a reader with Latin scripts."""
    ordered = tuple(dict.fromkeys(code.strip().lower() for code in languages if code.strip()))

    latin = tuple(code for code in ordered if code not in CYRILLIC_LANGS)
    cyrillic = tuple(code for code in ordered if code in CYRILLIC_LANGS)

    if not latin:
        latin = ("en",)

    cyrillic_group = None
    if cyrillic:
        cyrillic_group = tuple(dict.fromkeys(("en", *cyrillic)))

    return latin, cyrillic_group
