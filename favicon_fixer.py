"""Utility to regenerate favicon assets for Kloud."""
from __future__ import annotations

import os
from pathlib import Path


FAVICON_SVG = """
<svg width="32" height="32" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="neuroGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#6366f1;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#8b5cf6;stop-opacity:1" />
        </linearGradient>
    </defs>
    <circle cx="16" cy="16" r="14" fill="url(#neuroGrad)" stroke="#1e1b4b" stroke-width="1"/>
    <path d="M12 12 L20 12 L20 20 L12 20 Z" fill="none" stroke="white" stroke-width="2"/>
    <circle cx="16" cy="16" r="3" fill="white"/>
    <path d="M10 10 L12 12 M22 10 L20 12 M10 22 L12 20 M22 22 L20 20"
          stroke="white" stroke-width="1.5"/>
</svg>
""".strip()

# Common output locations developers expect a favicon in
POSSIBLE_FAVICON_PATHS = (
    Path("favicon.ico"),
    Path("static/favicon.ico"),
    Path("public/favicon.ico"),
    Path("assets/favicon.ico"),
    Path("Kloud-cloud/favicon.ico"),
)


def _generate_icon_bytes(width: int = 16, height: int = 16) -> bytes:
    """Return ICO bytes for a simple Kloud gradient orb."""
    if width != height:
        raise ValueError("ICO generation expects square dimensions")

    # ICONDIR header
    icon_dir = bytearray()
    icon_dir.extend((0).to_bytes(2, "little"))  # reserved
    icon_dir.extend((1).to_bytes(2, "little"))  # type: icon
    icon_dir.extend((1).to_bytes(2, "little"))  # count

    # Prepare pixel data (BGRA, bottom-up as required by ICO spec)
    pixel_data = bytearray()
    for y in range(height - 1, -1, -1):
        for x in range(width):
            # simple radial fade based on distance from center
            dx, dy = x - (width - 1) / 2, y - (height - 1) / 2
            dist = (dx * dx + dy * dy) ** 0.5
            t = max(0.0, min(1.0, 1.0 - dist / (width / 2)))
            # interpolate between Kloud brand colors (approx.)
            r = int(99 + (139 - 99) * (1 - t))
            g = int(102 + (92 - 102) * (1 - t))
            b = int(241 + (246 - 241) * (1 - t))
            a = 255 if dist <= width / 2 else 0
            pixel_data.extend((b, g, r, a))

    # AND mask (1 bit per pixel, padded to 32 bits per row)
    row_bytes = ((width + 31) // 32) * 4
    mask = bytearray()
    for _ in range(height):
        mask.extend(b"\x00" * row_bytes)

    bmp_height = height * 2  # color + mask
    bmp_size_image = len(pixel_data) + len(mask)

    bmp_header = bytearray()
    bmp_header.extend((40).to_bytes(4, "little"))  # header size
    bmp_header.extend((width).to_bytes(4, "little", signed=True))
    bmp_header.extend((bmp_height).to_bytes(4, "little", signed=True))
    bmp_header.extend((1).to_bytes(2, "little"))  # planes
    bmp_header.extend((32).to_bytes(2, "little"))  # bit count
    bmp_header.extend((0).to_bytes(4, "little"))  # compression BI_RGB
    bmp_header.extend(bmp_size_image.to_bytes(4, "little"))
    bmp_header.extend((2835).to_bytes(4, "little", signed=True))  # 72 DPI
    bmp_header.extend((2835).to_bytes(4, "little", signed=True))
    bmp_header.extend((0).to_bytes(4, "little"))  # clr used
    bmp_header.extend((0).to_bytes(4, "little"))  # clr important

    image_bytes = bytes(bmp_header + pixel_data + mask)
    image_size = len(image_bytes)

    icon_entry = bytearray()
    icon_entry.extend((width if width < 256 else 0).to_bytes(1, "little"))
    icon_entry.extend((height if height < 256 else 0).to_bytes(1, "little"))
    icon_entry.extend((0).to_bytes(1, "little"))  # color count
    icon_entry.extend((0).to_bytes(1, "little"))  # reserved
    icon_entry.extend((1).to_bytes(2, "little"))  # planes
    icon_entry.extend((32).to_bytes(2, "little"))  # bit count
    icon_entry.extend(image_size.to_bytes(4, "little"))
    icon_entry.extend((6 + 16).to_bytes(4, "little"))  # image offset

    return bytes(icon_dir + icon_entry + image_bytes)


def create_favicon() -> None:
    """Generate favicon.svg and favicon.ico in common locations."""
    root = Path.cwd()
    svg_path = root / "favicon.svg"
    svg_path.write_text(FAVICON_SVG, encoding="utf-8")

    icon_bytes = _generate_icon_bytes()
    for icon_path in POSSIBLE_FAVICON_PATHS:
        full_path = root / icon_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(icon_bytes)


if __name__ == "__main__":
    create_favicon()


