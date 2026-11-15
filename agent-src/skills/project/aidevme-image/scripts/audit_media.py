#!/usr/bin/env python3
"""List every file in the aidevme.com media library and check whether each image has an optimized version.

An original (PNG, JPEG, GIF, BMP or TIFF) counts as optimized when the library also holds a WebP or AVIF
attachment with the same base file name (copilot-studio-hooks.png -> copilot-studio-hooks.webp). WordPress's
"-scaled" suffix is ignored when matching. WebP and AVIF files over the size budget are flagged as oversized.
SVG, PDF, video and other files are listed but not checked.

Reads the public WordPress REST API (wp/v2/media) with a browser user agent, standard library only. Read-only.

Usage:
  python audit_media.py [--site https://aidevme.com] [--max-kb 300] [--out-dir DIR]

Writes to --out-dir (default: current directory):
  media-inventory.csv   one row per media item, with its status
  media-audit.md        summary and the items that need attention, ready for a GitHub issue body
Exit code 0 even when items need attention; 1 when the API can't be read.
"""
import argparse
import csv
import datetime
import json
import os
import re
import sys
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from urllib.parse import urlparse, unquote

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")
ORIGINAL_EXT = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tif", ".tiff"}
OPTIMIZED_EXT = {".webp", ".avif"}
FIELDS = "id,date,slug,mime_type,source_url,media_details,post"
MAX_ISSUE_CHARS = 60000


def fetch_all(site):
    items, page, total_pages, total = [], 1, 1, None
    while page <= total_pages:
        url = f"{site}/wp-json/wp/v2/media?per_page=100&page={page}&_fields={FIELDS}"
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            total_pages = int(resp.headers.get("X-WP-TotalPages", "1"))
            total = total if total is not None else int(resp.headers.get("X-WP-Total", "0"))
            items.extend(json.load(resp))
        page += 1
    return items, total


def file_info(item):
    path = unquote(urlparse(item.get("source_url", "")).path)
    name = os.path.basename(path)
    stem, ext = os.path.splitext(name)
    stem = re.sub(r"-scaled$", "", stem.lower())
    details = item.get("media_details") or {}
    size = details.get("filesize")
    return {
        "id": item.get("id"),
        "date": (item.get("date") or "")[:10],
        "file": name,
        "folder": os.path.dirname(path).rsplit("/uploads/", 1)[-1],
        "ext": ext.lower(),
        "stem": stem,
        "mime": item.get("mime_type", ""),
        "kb": round(size / 1024) if isinstance(size, int) else "",
        "width": details.get("width", ""),
        "height": details.get("height", ""),
        "attached_to": item.get("post") or "",
        "url": item.get("source_url", ""),
    }


def classify(rows, max_kb):
    twins = defaultdict(list)
    for r in rows:
        if r["ext"] in OPTIMIZED_EXT:
            twins[r["stem"]].append(r)
    for r in rows:
        if r["ext"] in ORIGINAL_EXT:
            match = twins.get(r["stem"], [])
            r["optimized_version"] = " ".join(m["file"] for m in match)
            r["status"] = "optimized" if match else "missing optimized version"
        elif r["ext"] in OPTIMIZED_EXT:
            r["optimized_version"] = ""
            over = isinstance(r["kb"], int) and r["kb"] > max_kb
            r["status"] = f"oversized (> {max_kb} KB)" if over else "ok"
        else:
            r["optimized_version"] = ""
            r["status"] = "not checked"
    return rows


def table(rows, cols):
    head = "| " + " | ".join(c for c, _ in cols) + " |\n| " + " | ".join("---" for _ in cols) + " |\n"
    body = "".join("| " + " | ".join(str(f(r)) for _, f in cols) + " |\n" for r in rows)
    return head + body


def report(rows, site, max_kb, today, total):
    counts = Counter(r["status"] for r in rows)
    originals = [r for r in rows if r["ext"] in ORIGINAL_EXT]
    missing = sorted((r for r in originals if r["status"].startswith("missing")),
                     key=lambda r: r["kb"] if isinstance(r["kb"], int) else 0, reverse=True)
    oversized = sorted((r for r in rows if r["status"].startswith("oversized")), key=lambda r: r["kb"], reverse=True)
    pct = round(100 * (len(originals) - len(missing)) / len(originals), 1) if originals else 100.0
    link = lambda r: f"[{r['file']}]({r['url']})"
    lines = [
        f"Media library of {site}, read on {today} through `wp-json/wp/v2/media` (public REST API).",
        "",
        "## Summary",
        "",
        f"- **Media items:** {len(rows)}" + (f" (the API reports {total}; the difference is items added or removed"
        f" while paging, or items the public API returns on no page)" if total and total != len(rows) else ""),
        f"- **Originals (PNG, JPEG, GIF, BMP, TIFF):** {len(originals)}; **with a WebP or AVIF version:** "
        f"{len(originals) - len(missing)} ({pct}%)",
        f"- **Missing an optimized version:** {len(missing)}",
        f"- **WebP or AVIF over {max_kb} KB:** {len(oversized)}",
        f"- **Not checked (SVG, PDF, video, other):** {counts.get('not checked', 0)}",
        "- **By type:** " + ", ".join(f"{m} {n}" for m, n in Counter(r["ext"] or "(none)" for r in rows).most_common()),
        "",
    ]
    sections = [
        ("Missing an optimized version", missing,
         [("ID", lambda r: r["id"]), ("File", link), ("KB", lambda r: r["kb"]), ("Size", lambda r: f"{r['width']}×{r['height']}"),
          ("Uploaded", lambda r: r["date"]), ("Attached to post", lambda r: r["attached_to"])]),
        (f"WebP or AVIF over {max_kb} KB", oversized,
         [("ID", lambda r: r["id"]), ("File", link), ("KB", lambda r: r["kb"]), ("Size", lambda r: f"{r['width']}×{r['height']}"),
          ("Uploaded", lambda r: r["date"])]),
    ]
    text = "\n".join(lines)
    for title, items, cols in sections:
        text += f"\n## {title} ({len(items)})\n\n"
        if not items:
            text += "None.\n"
            continue
        shown = items
        while shown and len(text) + len(table(shown, cols)) > MAX_ISSUE_CHARS - 2000:
            shown = shown[: len(shown) * 3 // 4]
        text += table(shown, cols)
        if len(shown) < len(items):
            text += f"\n{len(items) - len(shown)} more rows omitted; see `media-inventory.csv`.\n"
    return text


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--site", default="https://aidevme.com")
    ap.add_argument("--max-kb", type=int, default=300, help="size budget for WebP/AVIF files (default 300)")
    ap.add_argument("--out-dir", default=".")
    args = ap.parse_args()
    site = args.site.rstrip("/")
    try:
        items, total = fetch_all(site)
    except (urllib.error.URLError, ValueError) as exc:
        print(f"ERROR: can't read {site}/wp-json/wp/v2/media: {exc}", file=sys.stderr)
        return 1
    rows = classify([file_info(i) for i in items], args.max_kb)
    rows.sort(key=lambda r: (r["date"], r["id"]), reverse=True)
    os.makedirs(args.out_dir, exist_ok=True)
    cols = ["id", "date", "file", "folder", "mime", "kb", "width", "height", "status", "optimized_version",
            "attached_to", "url"]
    with open(os.path.join(args.out_dir, "media-inventory.csv"), "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    today = datetime.date.today().isoformat()
    with open(os.path.join(args.out_dir, "media-audit.md"), "w", encoding="utf-8") as fh:
        fh.write(report(rows, site, args.max_kb, today, total))
    counts = Counter(r["status"] for r in rows)
    print(f"{len(rows)} media items: " + ", ".join(f"{s} {n}" for s, n in counts.most_common()))
    print(f"Wrote {args.out_dir}/media-inventory.csv and {args.out_dir}/media-audit.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
