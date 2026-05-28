#!/usr/bin/env python3
"""Uniformly crop team headshots from highest-resolution sources available.

Pipeline per photo:
1. Detect the largest face using OpenCV Haar cascade.
2. Compute a square crop centered on the face, sized so the face fills
   ~55% of the frame (face_width ≈ 0.55 × crop_width). This places the
   eye line at the visual sweet spot (~38–42% from the top).
3. Resize to 400×400, save as JPEG q=88.

If no face is detected, fall back to a center-square crop and log it.

Source priority per slug: explicit override → ~/Downloads/2026 Team Photos
→ ~/Downloads → existing team-images/<slug>.jpg.
"""
from __future__ import annotations

import sys
from pathlib import Path
from PIL import Image
import cv2
import numpy as np

REPO = Path(__file__).resolve().parents[1]
HOME = Path.home()
DOWNLOADS = HOME / "Downloads"
TEAM_PHOTOS = DOWNLOADS / "2026 Team Photos"
OUT_DIR = REPO / "team-images"

# Final output dimensions
OUT_SIZE = 400
# Face should fill this fraction of the cropped square's WIDTH.
FACE_FILL_RATIO = 0.55
# Eye line target: 38% from the top of the output (visual center for circles).
EYE_VERTICAL_TARGET = 0.38

# slug -> source filename (relative to TEAM_PHOTOS unless absolute path given)
# None means "use existing team-images/<slug>.jpg as the source"
SLUG_TO_SOURCE = {
    "albert-amarente":       "Albert Amarente.jpg",
    "alex":                  "Alex2.jpeg",
    "anthony":               "Anthony.png",                  # Anthony Gonzalez
    "anthony-portillo":      "DSC01647.png",
    "elysia-powell":         DOWNLOADS / "Elysia Powell Black Background .png",
    "elysia-powell-royale":  DOWNLOADS / "Royale Elysia Powell 1_1.jpg",
    "gus":                   "Gus (1).jpg",
    "jouvens":               "Jouvens Corantin.jpg",
    "lisa":                  "Lisa.jpeg",
    "lorri-hill":            "Lorri Hill.png",
    "roxana-umana":          "Roxana Umana.png",
    "sondra":                "Sondra.jpg",
    # No high-res source available — re-crop the existing in-repo file
    "brian-cavanaugh":       None,
    "paul-sorrentino":       None,
    "willie-henderson":      None,
    "daniel-corcega":        None,
    # Daniel + Ray variants — preserve as distinct slugs but re-process from
    # existing in-repo file so they all hit the same 1:1 / face-centered standard.
    "daniel":                None,   # black-background variant
    "daniel-white":          None,   # white-background variant
    "ray":                   None,
    "ray-long":              None,   # "long shot" variant (intentionally wider)
    "elysia":                None,   # Kore CRM padded variant
    # Intentionally skipped: roxana-umana final.jpg (stray — separately deleted).
}

FACE_CASCADE = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)


def resolve_source(slug: str, src) -> Path | None:
    if src is None:
        existing = OUT_DIR / f"{slug}.jpg"
        return existing if existing.exists() else None
    if isinstance(src, Path):
        return src if src.exists() else None
    cand = TEAM_PHOTOS / src
    if cand.exists():
        return cand
    cand = DOWNLOADS / src
    if cand.exists():
        return cand
    return None


def detect_face(img_bgr: np.ndarray) -> tuple[int, int, int, int] | None:
    """Return (x, y, w, h) of the largest detected face, or None."""
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    # Tunable params; these work well for studio portraits.
    faces = FACE_CASCADE.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)
    )
    if len(faces) == 0:
        # Try again with looser params for tricky shots
        faces = FACE_CASCADE.detectMultiScale(
            gray, scaleFactor=1.05, minNeighbors=3, minSize=(50, 50)
        )
    if len(faces) == 0:
        return None
    # Largest face wins
    faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
    return tuple(int(v) for v in faces[0])


def compute_crop(img_w: int, img_h: int, face: tuple[int, int, int, int]) -> tuple[int, int, int]:
    """Return (left, top, square) so the face fills FACE_FILL_RATIO of the
    crop width and the eye line sits at EYE_VERTICAL_TARGET of the crop height.
    """
    fx, fy, fw, fh = face
    # Eye line approximation: top of face box + 40% (Haar boxes include forehead)
    eye_y = fy + int(fh * 0.40)
    face_cx = fx + fw // 2

    # Target crop width such that face_width / crop_width = FACE_FILL_RATIO
    crop = int(fw / FACE_FILL_RATIO)
    # Cap to image bounds — never larger than the smaller image dimension
    crop = min(crop, img_w, img_h)

    # Position vertically so eye_y lands at EYE_VERTICAL_TARGET of crop
    top = eye_y - int(crop * EYE_VERTICAL_TARGET)
    left = face_cx - crop // 2

    # Clamp to image bounds
    if left < 0: left = 0
    if top < 0: top = 0
    if left + crop > img_w: left = img_w - crop
    if top + crop > img_h: top = img_h - crop

    return left, top, crop


def process(slug: str, src_path: Path) -> str:
    img_bgr = cv2.imread(str(src_path))
    if img_bgr is None:
        # Try PIL → BGR (handles formats cv2 won't read)
        with Image.open(src_path) as im:
            arr = np.array(im.convert("RGB"))
        img_bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

    h, w = img_bgr.shape[:2]
    face = detect_face(img_bgr)
    if face is None:
        # Fallback: center square
        sq = min(w, h)
        left = (w - sq) // 2
        top = (h - sq) // 2
        crop = sq
        status = "NO-FACE-DETECTED — centered fallback"
    else:
        left, top, crop = compute_crop(w, h, face)
        status = f"face={face[2]}x{face[3]} at ({face[0]},{face[1]}) -> crop {crop}x{crop} at ({left},{top})"

    cropped_bgr = img_bgr[top:top + crop, left:left + crop]
    cropped_rgb = cv2.cvtColor(cropped_bgr, cv2.COLOR_BGR2RGB)
    pil = Image.fromarray(cropped_rgb).resize((OUT_SIZE, OUT_SIZE), Image.LANCZOS)

    dst = OUT_DIR / f"{slug}.jpg"
    # Quality target: <= 250 KB
    for q in (90, 88, 85, 82, 80, 75, 70):
        pil.save(dst, "JPEG", quality=q, optimize=True, progressive=True)
        if dst.stat().st_size <= 250_000:
            break

    return f"{slug:<24}  {dst.stat().st_size // 1024:>4} KB  {status}"


def main() -> int:
    # Allow per-slug filtering: scripts/headshot-crop.py slug1 slug2 ...
    only = set(sys.argv[1:]) if len(sys.argv) > 1 else None

    print(f"{'slug':<24}  {'size':>4}      result")
    print("-" * 90)
    processed = 0
    for slug, src in SLUG_TO_SOURCE.items():
        if only and slug not in only:
            continue
        src_path = resolve_source(slug, src)
        if src_path is None:
            print(f"{slug:<24}        SKIP — no source")
            continue
        try:
            print(process(slug, src_path))
            processed += 1
        except Exception as e:
            print(f"{slug:<24}        ERROR: {e}")
    print("-" * 90)
    print(f"processed {processed} photo(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
