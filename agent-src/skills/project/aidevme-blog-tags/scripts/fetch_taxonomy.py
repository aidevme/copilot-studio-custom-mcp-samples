#!/usr/bin/env python3
"""Fetch all aidevme.com tags, posts and categories from the WordPress REST API into one JSON file.

The local-shell equivalent of fetch_taxonomy.js (the curl fallback): public GET requests only, paginated with the
X-WP-TotalPages header. Sends a full browser user agent, because the site firewall answers 406 to short ones.
Standard library only.

Usage:
  python fetch_taxonomy.py [--site https://aidevme.com] [--out aidevme_taxonomy.json]
"""
import argparse
import datetime
import json
import sys
import urllib.error
import urllib.request

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/126.0 Safari/537.36")
COLLECTIONS = {
    "tags": "tags?per_page=100&_fields=id,name,slug,count,description,link",
    "posts": "posts?per_page=100&_fields=id,title,slug,link,date,modified,categories,tags",
    "categories": "categories?per_page=100&_fields=id,name,slug,count,description,parent,link",
}


def fetch_all(base, path):
    items, page, total_pages = [], 1, 1
    while page <= total_pages:
        url = f"{base}/{path}&page={page}"
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                total_pages = int(response.headers.get("X-WP-TotalPages") or 1)
                items.extend(json.loads(response.read().decode("utf-8")))
        except urllib.error.HTTPError as error:
            hint = ""
            if error.code in (401, 403, 404):
                hint = " - a security plugin may be blocking the REST API"
            elif error.code == 406:
                hint = " - the site firewall rejected the request; check the user agent"
            raise SystemExit(f"GET {url}: HTTP {error.code}{hint}")
        page += 1
    return items


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--site", default="https://aidevme.com")
    parser.add_argument("--out", default="aidevme_taxonomy.json")
    args = parser.parse_args()

    base = args.site.rstrip("/") + "/wp-json/wp/v2"
    result = {"site": args.site.rstrip("/"),
              "retrieved": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
              "source": "fetch_taxonomy.py"}
    for name, path in COLLECTIONS.items():
        result[name] = fetch_all(base, path)
    result["totals"] = {name: len(result[name]) for name in COLLECTIONS}
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)
    print(f"Saved {args.out}: " + ", ".join(f"{n} {c}" for n, c in result["totals"].items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
