#!/usr/bin/env python3
"""One-shot asset normalizer for SMAART Gmail signatures.

- Crops + resizes team photos to 200x200 JPG (<=100 KB) under team-images/
- Moves/renames logos into logos/ with kebab-case names
- Generates 48x48 PNG social icons into social-icons/ (Navy #0D004C fill)
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parents[1]
NAVY = (13, 0, 76)
WHITE = (255, 255, 255)

# (source path relative to repo root, destination relative to repo root)
PHOTO_MOVES = [
    ("Gus (1).jpg", "team-images/gus.jpg"),
    ("Lisa.jpeg", "team-images/lisa.jpg"),
    ("Lorri Hill.png", "team-images/lorri-hill.jpg"),
    ("Ray (1).jpg", "team-images/ray.jpg"),
    ("Roxana Umana.png", "team-images/roxana-umana.jpg"),
    ("team-images/Albert Amarente.jpg", "team-images/albert-amarente.jpg"),
    ("team-images/Alex2.jpeg", "team-images/alex.jpg"),
    ("team-images/Anthony.png", "team-images/anthony.jpg"),
]

LOGO_MOVES = [
    ("Smaart-Company-Logos-white-and-Navy.png", "logos/smaart-white-and-navy.png"),
    ("Smaart-Company-Logos-white.png", "logos/smaart-white.png"),
]


def square_crop(img: Image.Image, size: int) -> Image.Image:
    img = img.convert("RGB")
    w, h = img.size
    scale = size / min(w, h)
    img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    nw, nh = img.size
    left = (nw - size) // 2
    top = (nh - size) // 2
    return img.crop((left, top, left + size, top + size))


def compress_to_jpg(img: Image.Image, out: Path, max_bytes: int = 100_000) -> None:
    for q in (85, 80, 75, 70, 65, 60, 55, 50):
        img.save(out, "JPEG", quality=q, optimize=True, progressive=True)
        if out.stat().st_size <= max_bytes:
            return


def normalize_photos() -> None:
    for src_rel, dst_rel in PHOTO_MOVES:
        src = REPO / src_rel
        dst = REPO / dst_rel
        if not src.exists():
            print(f"SKIP photo (missing): {src_rel}")
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(src) as im:
            cropped = square_crop(im, 200)
        compress_to_jpg(cropped, dst)
        print(f"photo {src_rel} -> {dst_rel} ({dst.stat().st_size // 1024} KB)")
        if src.resolve() != dst.resolve():
            src.unlink()


def move_logos() -> None:
    (REPO / "logos").mkdir(parents=True, exist_ok=True)
    for src_rel, dst_rel in LOGO_MOVES:
        src = REPO / src_rel
        dst = REPO / dst_rel
        if not src.exists():
            print(f"SKIP logo (missing): {src_rel}")
            continue
        shutil.move(src, dst)
        print(f"logo  {src_rel} -> {dst_rel}")


def _draw_icon_base(size: int = 48) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((0, 0, size - 1, size - 1), fill=NAVY)
    return img, draw


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNS.ttf",
    ):
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def _centered_text(draw: ImageDraw.ImageDraw, text: str, font, size: int) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (size - tw) // 2 - bbox[0]
    y = (size - th) // 2 - bbox[1]
    draw.text((x, y), text, fill=WHITE, font=font)


def build_social_icons() -> None:
    out_dir = REPO / "social-icons"
    out_dir.mkdir(parents=True, exist_ok=True)
    size = 48

    # LinkedIn
    img, draw = _draw_icon_base(size)
    _centered_text(draw, "in", _load_font(22), size)
    img.save(out_dir / "linkedin.png", "PNG", optimize=True)

    # Facebook
    img, draw = _draw_icon_base(size)
    _centered_text(draw, "f", _load_font(30), size)
    img.save(out_dir / "facebook.png", "PNG", optimize=True)

    # Instagram — rounded square with camera glyph suggestion
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((0, 0, size - 1, size - 1), radius=11, fill=NAVY)
    cx = cy = size // 2
    r_outer = 11
    draw.ellipse((cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer), outline=WHITE, width=3)
    dot_r = 2
    draw.ellipse((size - 13, 9, size - 13 + 2 * dot_r, 9 + 2 * dot_r), fill=WHITE)
    img.save(out_dir / "instagram.png", "PNG", optimize=True)

    # X (Twitter)
    img, draw = _draw_icon_base(size)
    _centered_text(draw, "X", _load_font(24), size)
    img.save(out_dir / "x.png", "PNG", optimize=True)

    # YouTube — rounded rectangle with play triangle
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((2, 10, size - 3, size - 11), radius=8, fill=NAVY)
    draw.polygon([(20, 17), (20, size - 17), (34, size // 2)], fill=WHITE)
    img.save(out_dir / "youtube.png", "PNG", optimize=True)

    print(f"social icons -> {out_dir.relative_to(REPO)}/ (5 files)")


if __name__ == "__main__":
    normalize_photos()
    move_logos()
    build_social_icons()
    print("done.")
