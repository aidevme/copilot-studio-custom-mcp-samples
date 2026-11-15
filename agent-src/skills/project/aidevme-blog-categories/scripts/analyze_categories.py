#!/usr/bin/env python3
"""Analyze the aidevme.com category structure from aidevme_taxonomy.json.

The taxonomy file comes from aidevme-blog-tags' fetch_taxonomy.py (or fetch_taxonomy.js). The canonical product
list and the name normalization are imported from aidevme-blog-tags' analyze_tags.py, so both skills judge names
the same way.

Reports the category tree, empty and thin categories, posts outside 1-2 categories (one primary, at most one
secondary), posts filed under both a category and its parent, posts in the default "Uncategorized", product-named
categories that should be tags, categories that duplicate a tag, near-duplicates, pillar coverage, old product
names in slugs, missing or off-length descriptions, and a count sanity check. Writes category_analysis.json and
prints a summary. Every number comes from the input file. Standard library only.

Usage:
  python analyze_categories.py aidevme_taxonomy.json [--out category_analysis.json]
"""
import argparse
import collections
import difflib
import itertools
import json
import os
import re
import sys

# Reuse aidevme-blog-tags' normalization and canonical product list (sibling skill folder).
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "aidevme-blog-tags",
                                "scripts"))
from analyze_tags import CANONICAL, PILLARS, key, plain  # noqa: E402

SIMILARITY = 0.85
DESCRIPTION_MIN, DESCRIPTION_MAX = 120, 160
MAX_CATEGORIES_PER_POST = 2          # one primary + at most one secondary (aidevme-blog-optimization)
OLD_NAMES_IN_SLUGS = ["azure-ai-foundry", "powerapps", "power-virtual-agents", "common-data-service"]
DEFAULT_NAMES = {"uncategorized"}
NOT_A_CATEGORY = {"featured post", "featured", "blog", "features", "portfolio", "programming", "productivity"}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("taxonomy")
    parser.add_argument("--out", default="category_analysis.json")
    args = parser.parse_args()

    data = json.load(open(args.taxonomy, encoding="utf-8"))
    cats = {c["id"]: c for c in data["categories"]}
    tags = {t["id"]: t for t in data["tags"]}
    posts = data["posts"]
    for c in cats.values():
        c["name"] = plain(c["name"])
        c["description"] = plain(c.get("description"))
        c["key"] = key(c["name"])
        c["posts"] = []
    for p in posts:
        p["title"] = plain(p["title"]["rendered"] if isinstance(p["title"], dict) else p["title"])
        for cid in p["categories"]:
            if cid in cats:
                cats[cid]["posts"].append(p["id"])

    def path(c):
        parts, seen = [c["slug"]], {c["id"]}
        while c.get("parent") and c["parent"] in cats and c["parent"] not in seen:
            c = cats[c["parent"]]
            seen.add(c["id"])
            parts.append(c["slug"])
        return "/category/" + "/".join(reversed(parts)) + "/"

    def brief(c):
        return {"id": c["id"], "name": c["name"], "slug": c["slug"], "count": c["count"], "parent": c["parent"],
                "path": c.get("link") or path(c)}

    def post_brief(p):
        return {"id": p["id"], "title": p["title"], "link": p["link"],
                "categories": [cats[i]["name"] for i in p["categories"] if i in cats]}

    def tree(parent=0, depth=0):
        rows = []
        for c in sorted((c for c in cats.values() if (c["parent"] or 0) == parent), key=lambda c: c["name"].lower()):
            rows.append({"depth": depth, **brief(c)})
            rows += tree(c["id"], depth + 1)
        return rows

    by_count = sorted(cats.values(), key=lambda c: (-c["count"], c["name"].lower()))
    inventory = {
        "categories": len(cats), "top_level": sum(not c["parent"] for c in cats.values()),
        "children": sum(bool(c["parent"]) for c in cats.values()), "posts": len(posts),
        "categories_with_0_posts": sum(c["count"] == 0 for c in cats.values()),
        "categories_with_1_to_2_posts": sum(1 <= c["count"] <= 2 for c in cats.values()),
        "posts_per_category_count": dict(sorted(collections.Counter(len(p["categories"]) for p in posts).items())),
    }

    # Posts outside the 1-2 rule, and posts filed under a category and its own parent.
    too_many = [post_brief(p) for p in posts if len(p["categories"]) > MAX_CATEGORIES_PER_POST]
    none = [post_brief(p) for p in posts if not p["categories"]]
    parent_and_child = [post_brief(p) for p in posts
                        if any(cats.get(i, {}).get("parent") in p["categories"] for i in p["categories"])]
    default_ids = {cid for cid, c in cats.items() if c["key"] in {key(n) for n in DEFAULT_NAMES}}
    in_default = [post_brief(p) for p in posts if default_ids & set(p["categories"])]

    canonical_keys = {key(n): n for n in CANONICAL}
    pillar_keys = {key(n): n for n in PILLARS}
    product_named = [dict(brief(c), canonical_tag=canonical_keys[c["key"]])
                     for c in cats.values() if c["key"] in canonical_keys]
    tag_keys = {}
    for t in tags.values():
        tag_keys.setdefault(key(plain(t["name"])), []).append(t)
    duplicates_tag = [dict(brief(c), tags=[{"id": t["id"], "name": plain(t["name"]), "count": t["count"]}
                                            for t in tag_keys[c["key"]]])
                      for c in cats.values() if c["key"] in tag_keys]
    pillars_present = {pillar_keys[c["key"]]: brief(c) for c in cats.values() if c["key"] in pillar_keys}
    pillar_coverage = {p: pillars_present.get(p) for p in PILLARS}

    groups = collections.defaultdict(list)
    for c in cats.values():
        groups[c["key"]].append(c)
    near_duplicates = [{"reason": "same normalized name", "categories": [brief(c) for c in g]}
                       for g in groups.values() if len(g) > 1]
    for a, b in itertools.combinations(sorted(groups), 2):
        ratio = difflib.SequenceMatcher(None, a, b).ratio()
        if ratio >= SIMILARITY:
            near_duplicates.append({"reason": f"similar names (difflib {ratio:.2f})",
                                    "categories": [brief(c) for c in groups[a] + groups[b]]})

    old_slugs = [brief(c) for c in cats.values()
                 if any(o in c["slug"] for o in OLD_NAMES_IN_SLUGS) or re.search(r"-\d+$", c["slug"])]
    not_a_category = [brief(c) for c in cats.values() if c["name"].lower() in NOT_A_CATEGORY]
    used = [c for c in cats.values() if c["count"] >= 1]
    descriptions = {
        "missing": [brief(c) for c in used if not c["description"]],
        "off_length": [dict(brief(c), length=len(c["description"])) for c in used
                       if c["description"] and not DESCRIPTION_MIN <= len(c["description"]) <= DESCRIPTION_MAX],
    }

    assignments = sum(len([i for i in p["categories"] if i in cats]) for p in posts)
    count_sum = sum(c["count"] for c in cats.values())
    sanity = {"sum_of_category_counts": count_sum, "category_assignments_in_posts": assignments,
              "match": count_sum == assignments,
              "note": "" if count_sum == assignments else
              "Counts include posts the public API doesn't return (drafts, private, scheduled) or are stale."}

    result = {
        "source": args.taxonomy, "retrieved": data.get("retrieved"), "inventory": inventory, "tree": tree(),
        "top_categories": [brief(c) for c in by_count[:10]],
        "empty_categories": [brief(c) for c in by_count if c["count"] == 0],
        "thin_categories": [brief(c) for c in by_count if 1 <= c["count"] <= 2],
        "posts_with_too_many_categories": too_many, "posts_without_category": none,
        "posts_with_parent_and_child": parent_and_child, "posts_in_default_category": in_default,
        "product_named_categories": product_named, "categories_duplicating_tags": duplicates_tag,
        "pillar_coverage": pillar_coverage, "near_duplicates": near_duplicates, "old_names_in_slugs": old_slugs,
        "not_a_category": not_a_category, "descriptions": descriptions, "sanity_check": sanity,
    }
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)

    inv = inventory
    print(f"Source: {args.taxonomy} (retrieved {data.get('retrieved')})")
    print(f"Categories {inv['categories']} ({inv['top_level']} top-level, {inv['children']} children) | "
          f"posts {inv['posts']}")
    print(f"Empty: {inv['categories_with_0_posts']} | thin (1-2 posts): {inv['categories_with_1_to_2_posts']}")
    print("Top 10: " + ", ".join(f"{c['name']} ({c['count']})" for c in result["top_categories"]))
    print(f"Posts per number of categories: {inv['posts_per_category_count']}")
    print(f"Posts with more than {MAX_CATEGORIES_PER_POST} categories: {len(too_many)} | without: {len(none)} | "
          f"parent and child: {len(parent_and_child)} | in Uncategorized: {len(in_default)}")
    print(f"Product-named (should be tags): {len(product_named)} | duplicating a tag: {len(duplicates_tag)} | "
          f"not a category: {len(not_a_category)} | near-duplicate groups: {len(near_duplicates)}")
    print("Pillars present: " + ", ".join(f"{p}: {'yes' if v else 'no'}" for p, v in pillar_coverage.items()))
    print(f"Old names in slugs: {len(old_slugs)} | descriptions missing: {len(descriptions['missing'])} | "
          f"outside {DESCRIPTION_MIN}-{DESCRIPTION_MAX} chars: {len(descriptions['off_length'])}")
    print(f"Sanity: sum of category counts {count_sum} vs assignments {assignments} -> "
          f"{'OK' if sanity['match'] else 'MISMATCH: ' + sanity['note']}")
    print(f"Saved {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
