#!/usr/bin/env python3
"""Downsize images in docs/assets/ in place (the optimize plugin only compresses).

    python scripts/resize_assets.py [--dry-run]
"""

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageOps

ASSETS = Path("docs/assets")

# Max length of the longest edge, per subfolder (fallback: DEFAULT_CAP).
CAPS = {
    "profiles": 600,    # avatars render small; 600 covers hi-dpi comfortably
    "projects": 1600,   # card / full-width covers
}
DEFAULT_CAP = 1600

EXTS = {".jpg", ".jpeg", ".png", ".webp"}
# Re-save quality. JPG is re-compressed again by the optimize plugin at build
# (quality 60), so the source just needs to be a sane intermediate, not pristine.
# WebP isn't handled by optimize, so its quality here IS the final quality.
SAVE = {
    ".jpg": dict(quality=85),
    ".jpeg": dict(quality=85),
    ".webp": dict(quality=80, method=6),
}


def cap_for(path: Path) -> int:
    for part in path.relative_to(ASSETS).parts:
        if part in CAPS:
            return CAPS[part]
    return DEFAULT_CAP


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not ASSETS.is_dir():
        print(f"no {ASSETS} directory", file=sys.stderr)
        return 1

    before = after = 0
    for path in sorted(ASSETS.rglob("*")):
        if path.suffix.lower() not in EXTS:
            continue
        size0 = path.stat().st_size
        before += size0

        with Image.open(path) as im:
            im = ImageOps.exif_transpose(im)  # bake in orientation, drop EXIF
            cap = cap_for(path)
            longest = max(im.size)
            if longest <= cap:
                after += size0
                continue

            scale = cap / longest
            new = (round(im.width * scale), round(im.height * scale))
            label = f"{im.width}x{im.height} -> {new[0]}x{new[1]}"
            if args.dry_run:
                print(f"  would resize {path.relative_to(ASSETS)}  {label}")
                after += size0
                continue

            im = im.resize(new, Image.LANCZOS)
            im.save(path, **SAVE.get(path.suffix.lower(), {}))

        size1 = path.stat().st_size
        after += size1
        print(f"  {path.relative_to(ASSETS)}  {label}  {size0//1024}KB -> {size1//1024}KB")

    verb = "would save" if args.dry_run else "saved"
    print(f"\n{verb}: {before//1024}KB -> {after//1024}KB "
          f"({(1 - after/before)*100:.0f}% smaller)" if before else "no images")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
