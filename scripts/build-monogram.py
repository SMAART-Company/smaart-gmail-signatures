#!/usr/bin/env python3
"""Generate a 200x200 monogram avatar.

Usage:
    python3 scripts/build-monogram.py DC team-images/daniel-corcega.jpg
"""
from __future__ import annotations

import os
import sys
from PIL import Image, ImageDraw, ImageFont

NAVY = (13, 0, 76)
WHITE = (255, 255, 255)


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/SFNS.ttf",
    ):
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def build(initials: str, out_path: str, size: int = 200) -> None:
    img = Image.new("RGB", (size, size), NAVY)
    draw = ImageDraw.Draw(img)
    font = load_font(int(size * 0.44))
    bbox = draw.textbbox((0, 0), initials, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (size - tw) // 2 - bbox[0]
    y = (size - th) // 2 - bbox[1]
    draw.text((x, y), initials, fill=WHITE, font=font)
    img.save(out_path, "JPEG", quality=90, optimize=True, progressive=True)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    build(sys.argv[1].upper(), sys.argv[2])
    print(f"wrote {sys.argv[2]} ({os.path.getsize(sys.argv[2])} bytes)")
