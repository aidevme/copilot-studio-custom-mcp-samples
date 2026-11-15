#!/usr/bin/env python3
"""Check an aidevme image file against its placement: format, dimensions, aspect ratio and file size.

Placements (ratio, minimum width, size budget):
  featured  1.91:1, >= 1200 px wide, <= 300 KB   WordPress featured image, Open Graph, LinkedIn link preview
  inline    16:9,   >= 1200 px wide, <= 200 KB   in-post illustration
  linkedin  1.91:1 or 4:5, >= 1080 px wide, <= 500 KB
  github    2:1,    >= 1280 px wide, <= 1 MB     GitHub social preview (GitHub's own limit is 1 MB)

Reads PNG, JPEG, WebP and GIF headers with the standard library only.

Usage:
  python check_image.py <image> [--placement featured|inline|linkedin|github]
"""
import argparse
import os
import struct
import sys

PLACEMENTS = {
    "featured": {"ratios": [1.91], "min_width": 1200, "max_kb": 300},
    "inline": {"ratios": [16 / 9], "min_width": 1200, "max_kb": 200},
    "linkedin": {"ratios": [1200 / 627, 4 / 5], "min_width": 1080, "max_kb": 500},
    "github": {"ratios": [2.0], "min_width": 1280, "max_kb": 1024},
}
RATIO_TOLERANCE = 0.02  # 2%


def dimensions(path):
    with open(path, "rb") as fh:
        head = fh.read(32)
        if head[:8] == b"\x89PNG\r\n\x1a\n":
            return "PNG", struct.unpack(">II", head[16:24])
        if head[:6] in (b"GIF87a", b"GIF89a"):
            return "GIF", struct.unpack("<HH", head[6:10])
        if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
            chunk = head[12:16]
            fh.seek(0)
            data = fh.read(64)
            if chunk == b"VP8X":
                w = int.from_bytes(data[24:27], "little") + 1
                h = int.from_bytes(data[27:30], "little") + 1
                return "WebP", (w, h)
            if chunk == b"VP8 ":
                w, h = struct.unpack("<HH", data[26:30])
                return "WebP", (w & 0x3FFF, h & 0x3FFF)
            if chunk == b"VP8L":
                bits = int.from_bytes(data[21:25], "little")
                return "WebP", ((bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1)
        if head[:2] == b"\xff\xd8":
            fh.seek(2)
            while True:
                marker = fh.read(2)
                if len(marker) < 2 or marker[0] != 0xFF:
                    break
                if 0xC0 <= marker[1] <= 0xCF and marker[1] not in (0xC4, 0xC8, 0xCC):
                    fh.read(3)
                    h, w = struct.unpack(">HH", fh.read(4))
                    return "JPEG", (w, h)
                length = struct.unpack(">H", fh.read(2))[0]
                fh.seek(length - 2, os.SEEK_CUR)
    return None, None


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("image")
    parser.add_argument("--placement", choices=PLACEMENTS, default="featured")
    args = parser.parse_args()

    fmt, size = dimensions(args.image)
    if not fmt:
        print(f"FAIL  {args.image}: not a PNG, JPEG, WebP or GIF file")
        return 1
    width, height = size
    kb = os.path.getsize(args.image) / 1024
    spec = PLACEMENTS[args.placement]
    ratio = width / height
    ratio_ok = any(abs(ratio - r) / r <= RATIO_TOLERANCE for r in spec["ratios"])
    checks = [
        ("Format", True, fmt),
        ("Dimensions", width >= spec["min_width"], f"{width} x {height} px (minimum width {spec['min_width']})"),
        ("Aspect ratio", ratio_ok, f"{ratio:.2f}:1 (expected "
                                   f"{' or '.join(f'{r:.2f}:1' for r in spec['ratios'])})"),
        ("File size", kb <= spec["max_kb"], f"{kb:,.0f} KB (budget {spec['max_kb']} KB)"),
    ]
    print(f"{args.image}  [{args.placement}]")
    for name, ok, detail in checks:
        print(f"  {'OK  ' if ok else 'FAIL'}  {name:<13} {detail}")
    if kb > spec["max_kb"]:
        print("  Fix: convert to WebP or JPEG at quality 80-85, e.g. cwebp -q 82 in.png -o out.webp")
    if not ratio_ok:
        print("  Fix: crop or regenerate at the placement's ratio")
    return 0 if all(ok for _, ok, _ in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
