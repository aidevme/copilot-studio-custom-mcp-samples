#!/usr/bin/env python3
"""Analyze the aidevme.com tag structure from aidevme_taxonomy.json (fetch_taxonomy.py / fetch_taxonomy.js).

Reports inventory, unused and thin tags, near-duplicates (normalized names, known aliases, difflib >= 0.85),
category clashes, casing and spelling against the canonical product list, -2 slugs, missing or off-length
descriptions, generic tags, posts outside 3-6 tags, tags that nearly always co-occur, stale tags and a count
sanity check. Writes tag_analysis.json and prints a summary. Every number comes from the input file.
Standard library only.

Usage:
  python analyze_tags.py aidevme_taxonomy.json [--out tag_analysis.json] [--today YYYY-MM-DD]
"""
import argparse
import datetime
import difflib
import html
import itertools
import json
import re
import sys

PILLARS = ["Build with AI", "Build AI agents", "Pro-code Power Platform", "ALM and governance",
           "Open source and speaking"]
CANONICAL = ["PCF", "Power Apps Code Apps", "Canvas apps", "Model-driven apps", "Custom pages", "Power Pages",
             "Dataverse", "Copilot Studio", "Microsoft Foundry", "MCP", "Dataverse MCP", "GitHub Copilot",
             "Claude Code", "Agent skills", "React", "Fluent UI", "Storybook", "TypeScript", "Azure DevOps",
             "GitHub Actions", "Terraform", "Power Platform CLI", "Solution Health Checker", "Accessibility",
             "Entire.io"]
# Known aliases, applied after normalization: alias -> canonical name.
ALIASES = {
    "powerapps": "power apps", "azure ai foundry": "microsoft foundry", "azure foundry": "microsoft foundry",
    "ai foundry": "microsoft foundry", "model context protocol": "mcp", "mcp server": "mcp",
    "mcp servers": "mcp", "power apps component framework": "pcf", "pcf control": "pcf", "pcf controls": "pcf",
    "code apps": "power apps code apps", "power apps code app": "power apps code apps",
    "canvas app": "canvas apps", "model driven apps": "model-driven apps", "model driven app": "model-driven apps",
    "custom page": "custom pages", "pac cli": "power platform cli", "pac": "power platform cli",
    "common data service": "dataverse", "cds": "dataverse", "power virtual agents": "copilot studio",
    "pva": "copilot studio", "copilot studio agents": "copilot studio", "github actions workflow": "github actions",
    "ado": "azure devops", "azure devops pipelines": "azure devops", "fluentui": "fluent ui",
    "fluent ui react": "fluent ui", "ts": "typescript", "a11y": "accessibility", "skills": "agent skills",
    "claude skills": "agent skills", "entire": "entire.io",
}
GENERIC = {"power platform", "ai", "microsoft", "tutorial", "tutorials", "guide", "how to", "tips",
           "artificial intelligence", "development", "news", "blog", "technology", "low code", "lowcode"}
SIMILARITY = 0.85
DESCRIPTION_MIN, DESCRIPTION_MAX = 120, 160
STALE_MONTHS = 18


def plain(text):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", text or ""))).strip()


def singular(word):
    if len(word) > 3 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 3 and word.endswith("s") and not word.endswith(("ss", "us", "is")):
        return word[:-1]
    return word


def base_key(text):
    """Lowercase, '&' as 'and', spaces/hyphens/dots/slashes stripped, each word singularized."""
    words = re.split(r"[\s\-.\/_]+", plain(text).lower().replace("&", "and"))
    return "".join(singular(w) for w in words if w)


ALIAS_KEYS = {base_key(alias): base_key(target) for alias, target in ALIASES.items()}


def key(name):
    """Normalization key used to find duplicates: base_key with known aliases mapped to their canonical name."""
    k = base_key(name)
    return ALIAS_KEYS.get(k, k)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("taxonomy")
    parser.add_argument("--out", default="tag_analysis.json")
    parser.add_argument("--today", help="reference date for staleness (default: today)")
    args = parser.parse_args()

    data = json.load(open(args.taxonomy, encoding="utf-8"))
    tags = {t["id"]: t for t in data["tags"]}
    posts = data["posts"]
    categories = data["categories"]
    today = datetime.date.fromisoformat(args.today) if args.today else datetime.date.today()
    stale_before = today - datetime.timedelta(days=round(STALE_MONTHS * 30.44))

    for t in tags.values():
        t["name"] = plain(t["name"])
        t["description"] = plain(t.get("description"))
        t["key"] = key(t["name"])
        t["posts"] = []
    for p in posts:
        p["title"] = plain(p["title"]["rendered"] if isinstance(p["title"], dict) else p["title"])
        for tid in p["tags"]:
            if tid in tags:
                tags[tid]["posts"].append(p["id"])

    def brief(t):
        return {"id": t["id"], "name": t["name"], "slug": t["slug"], "count": t["count"]}

    by_count = sorted(tags.values(), key=lambda t: (-t["count"], t["name"].lower()))
    inventory = {
        "tags": len(tags), "posts": len(posts), "categories": len(categories),
        "tags_with_0_posts": sum(t["count"] == 0 for t in tags.values()),
        "tags_with_1_post": sum(t["count"] == 1 for t in tags.values()),
        "tags_with_2_posts": sum(t["count"] == 2 for t in tags.values()),
        "tags_with_3_plus_posts": sum(t["count"] >= 3 for t in tags.values()),
        "top_15": [brief(t) for t in by_count[:15]],
    }

    # Near-duplicates: same normalization key, or difflib ratio >= SIMILARITY on the keys.
    groups = {}
    for t in tags.values():
        groups.setdefault(t["key"], []).append(t)
    near_duplicates = [{"reason": "same normalized name", "tags": [brief(t) for t in sorted(g, key=lambda t: -t["count"])]}
                       for g in groups.values() if len(g) > 1]
    keys = sorted(groups)
    for a, b in itertools.combinations(keys, 2):
        ratio = difflib.SequenceMatcher(None, a, b).ratio()
        if ratio >= SIMILARITY:
            near_duplicates.append({"reason": f"similar names (difflib {ratio:.2f})",
                                    "tags": [brief(t) for t in groups[a] + groups[b]]})

    category_keys = {}
    for c in categories:
        category_keys[key(c["name"])] = c
        category_keys[key(c["slug"])] = c
    category_clashes = []
    for t in tags.values():
        c = category_keys.get(t["key"]) or category_keys.get(key(t["slug"]))
        if c:
            category_clashes.append({"tag": brief(t), "category": {"id": c["id"], "name": plain(c["name"]),
                                                                   "slug": c["slug"], "count": c["count"]}})

    canonical_by_key = {key(c): c for c in CANONICAL}
    pillar_keys = {key(p): p for p in PILLARS}
    spelling = [{"tag": brief(t), "canonical": canonical_by_key[t["key"]]}
                for t in tags.values() if t["key"] in canonical_by_key and t["name"] != canonical_by_key[t["key"]]]
    pillar_clashes = [{"tag": brief(t), "pillar": pillar_keys[t["key"]]} for t in tags.values() if t["key"] in pillar_keys]
    numbered_slugs = [brief(t) for t in tags.values() if re.search(r"-\d+$", t["slug"])]
    generic = [brief(t) for t in tags.values()
               if plain(t["name"]).lower() in GENERIC or t["key"] in {key(g) for g in GENERIC}]

    used = [t for t in tags.values() if t["count"] >= 1]
    descriptions = {
        "missing": [brief(t) for t in used if not t["description"]],
        "off_length": [dict(brief(t), length=len(t["description"])) for t in used
                       if t["description"] and not DESCRIPTION_MIN <= len(t["description"]) <= DESCRIPTION_MAX],
    }

    def post_brief(p):
        return {"id": p["id"], "title": p["title"], "link": p["link"], "tag_count": len(p["tags"])}

    per_post = {
        "with_0_tags": [post_brief(p) for p in posts if len(p["tags"]) == 0],
        "with_1_to_2_tags": [post_brief(p) for p in posts if 1 <= len(p["tags"]) <= 2],
        "with_more_than_8_tags": [post_brief(p) for p in posts if len(p["tags"]) > 8],
        "outside_3_to_6": sum(not 3 <= len(p["tags"]) <= 6 for p in posts),
    }

    # Co-occurrence: pairs sharing >= 80% of the smaller tag's posts (smaller tag needs at least 2 posts).
    sets = {tid: set(t["posts"]) for tid, t in tags.items() if len(t["posts"]) >= 2}
    co_occurrence = []
    for a, b in itertools.combinations(sorted(sets), 2):
        shared = len(sets[a] & sets[b])
        smaller = min(len(sets[a]), len(sets[b]))
        if shared and shared / smaller >= 0.8:
            co_occurrence.append({"tags": [brief(tags[a]), brief(tags[b])], "shared_posts": shared,
                                  "share_of_smaller": round(shared / smaller, 2)})
    co_occurrence.sort(key=lambda x: (-x["share_of_smaller"], -x["shared_posts"]))

    post_dates = {p["id"]: datetime.date.fromisoformat(p["date"][:10]) for p in posts}
    stale = [dict(brief(t), newest_post=max(post_dates[i] for i in t["posts"]).isoformat())
             for t in tags.values() if t["posts"] and all(post_dates[i] < stale_before for i in t["posts"])]

    assignments = sum(len([tid for tid in p["tags"] if tid in tags]) for p in posts)
    tag_count_sum = sum(t["count"] for t in tags.values())
    sanity = {"sum_of_tag_counts": tag_count_sum, "tag_assignments_in_posts": assignments,
              "match": tag_count_sum == assignments,
              "note": "" if tag_count_sum == assignments else
              "Tag counts include posts the public API doesn't return (drafts, private or scheduled posts) or are "
              "stale; WordPress recounts on the next post save."}

    result = {
        "source": args.taxonomy, "retrieved": data.get("retrieved"), "analyzed": today.isoformat(),
        "inventory": inventory,
        "unused_tags": [brief(t) for t in by_count if t["count"] == 0],
        "thin_tags": [brief(t) for t in by_count if 1 <= t["count"] <= 2],
        "near_duplicates": near_duplicates,
        "category_clashes": category_clashes,
        "pillar_clashes": pillar_clashes,
        "spelling_vs_canonical": spelling,
        "numbered_slugs": numbered_slugs,
        "generic_tags": generic,
        "descriptions": descriptions,
        "per_post": per_post,
        "co_occurrence": co_occurrence,
        "stale_tags": stale,
        "sanity_check": sanity,
    }
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)

    inv = inventory
    print(f"Source: {args.taxonomy} (retrieved {data.get('retrieved')})")
    print(f"Tags {inv['tags']} | posts {inv['posts']} | categories {inv['categories']}")
    print(f"Tags by posts: 0 -> {inv['tags_with_0_posts']}, 1 -> {inv['tags_with_1_post']}, "
          f"2 -> {inv['tags_with_2_posts']}, 3+ -> {inv['tags_with_3_plus_posts']}")
    print("Top 15: " + ", ".join(f"{t['name']} ({t['count']})" for t in inv["top_15"]))
    print(f"Near-duplicate groups: {len(near_duplicates)} | category clashes: {len(category_clashes)} | "
          f"pillar clashes: {len(pillar_clashes)} | generic: {len(generic)}")
    print(f"Spelling vs canonical: {len(spelling)} | -N slugs: {len(numbered_slugs)} | "
          f"used tags without description: {len(descriptions['missing'])} | "
          f"descriptions outside {DESCRIPTION_MIN}-{DESCRIPTION_MAX} chars: {len(descriptions['off_length'])}")
    print(f"Posts: 0 tags {len(per_post['with_0_tags'])}, 1-2 tags {len(per_post['with_1_to_2_tags'])}, "
          f">8 tags {len(per_post['with_more_than_8_tags'])}, outside 3-6: {per_post['outside_3_to_6']}")
    print(f"Co-occurring pairs (>= 80%): {len(co_occurrence)} | stale tags (all posts before "
          f"{stale_before.isoformat()}): {len(stale)}")
    print(f"Sanity: sum of tag counts {tag_count_sum} vs assignments {assignments} -> "
          f"{'OK' if sanity['match'] else 'MISMATCH: ' + sanity['note']}")
    print(f"Saved {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
