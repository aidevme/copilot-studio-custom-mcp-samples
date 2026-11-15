#!/usr/bin/env python3
"""Turn category_plan.json into category_plan.xlsx (tabs Plan, Descriptions, Recategorize, Redirects),
redirects.csv for the Redirection plugin, and before/after numbers. Validates the plan: every category exactly once,
targets that exist, 1-2 categories per post, retag entries for every post that loses a category, descriptions of
120-160 characters, and the default category. Reuses the .xlsx writer from aidevme-blog-tags. Standard library only.

Usage:
  python category_plan_to_xlsx.py category_plan.json [--taxonomy aidevme_taxonomy.json] [--out category_plan.xlsx]
"""
import argparse
import csv
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "aidevme-blog-tags",
                                "scripts"))
from plan_to_xlsx import write_xlsx  # noqa: E402

KEEP = {"keep", "rename", "reparent"}
GONE = {"merge", "move_to_tag", "delete"}


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("plan")
    parser.add_argument("--taxonomy", help="default: the plan's based_on file, next to the plan")
    parser.add_argument("--out", help="default: category_plan.xlsx next to the plan")
    args = parser.parse_args()

    folder = os.path.dirname(os.path.abspath(args.plan))
    plan = json.load(open(args.plan, encoding="utf-8"))
    taxonomy = json.load(open(args.taxonomy or os.path.join(folder, plan.get("based_on", "aidevme_taxonomy.json")),
                              encoding="utf-8"))
    out = args.out or os.path.join(folder, "category_plan.xlsx")
    live = {c["id"]: c for c in taxonomy["categories"]}
    tag_slug = {t["name"]: t["slug"] for t in taxonomy["tags"]}
    issues = []

    planned = [c["id"] for c in plan["categories"]]
    if set(live) - set(planned):
        issues.append(f"live categories not in the plan: {sorted(set(live) - set(planned))}")
    if len(planned) != len(set(planned)):
        issues.append("a category is listed twice")

    # Final tree: name -> (slug, parent name) for every kept and new category.
    live_name = {cid: c["name"] for cid, c in live.items()}
    final_name = {c["id"]: c.get("new_name") or c["name"] for c in plan["categories"] if c["action"] in KEEP}
    final = {}
    for c in plan["categories"]:
        if c["action"] in KEEP:
            # A kept category stays under its current parent (by that parent's final name) unless new_parent is set.
            parent = c["new_parent"] if "new_parent" in c else final_name.get(live[c["id"]]["parent"])
            final[final_name[c["id"]]] = {"slug": c.get("new_slug") or c["slug"], "parent": parent or None}
    for n in plan.get("new_categories", []):
        final[n["name"]] = {"slug": n["slug"], "parent": n.get("parent")}
    for name, info in final.items():
        if info["parent"] and info["parent"] not in final:
            issues.append(f"'{name}' has parent '{info['parent']}', which isn't a kept or new category")

    def new_path(name, seen=()):
        info = final[name]
        if info["parent"] and info["parent"] in final and info["parent"] not in seen:
            return new_path(info["parent"], seen + (name,)).rstrip("/") + "/" + info["slug"] + "/"
        return "/category/" + info["slug"] + "/"

    def old_path(cid):
        link = live[cid].get("link")
        if link:
            return re.sub(r"^https?://[^/]+", "", link)
        return "/category/" + live[cid]["slug"] + "/"

    for c in plan["categories"]:
        if c["action"] == "merge" and c.get("merge_into") not in final:
            issues.append(f"'{c['name']}' merges into '{c.get('merge_into')}', which isn't a kept or new category")
        if c["action"] == "move_to_tag" and not c.get("tag"):
            issues.append(f"'{c['name']}' moves to a tag but names none")
        if c["action"] in GONE and live[c["id"]]["slug"] == "uncategorized":
            issues.append("'Uncategorized' is WordPress's default category: set another default before deleting it")

    # Projected categories per post.
    listed = {p["id"]: p for p in plan.get("posts", [])}
    projected = {}
    for post in taxonomy["posts"]:
        if post["id"] in listed:
            projected[post["id"]] = listed[post["id"]]["proposed"]
            continue
        keep_names = []
        for cid in post["categories"]:
            entry = next((c for c in plan["categories"] if c["id"] == cid), None)
            if entry and entry["action"] in KEEP:
                keep_names.append(entry.get("new_name") or entry["name"])
            elif entry:
                issues.append(f"post {post['id']} loses '{entry['name']}' but has no recategorize entry")
        projected[post["id"]] = keep_names
    usage = {}
    for pid, names in projected.items():
        if not 1 <= len(names) <= 2:
            issues.append(f"post {pid} would have {len(names)} categories (target: 1-2, primary first)")
        for n in names:
            if n not in final:
                issues.append(f"post {pid}: proposed category '{n}' isn't a kept or new category")
            usage[n] = usage.get(n, 0) + 1

    def describe(entry):
        return (entry.get("description") or "").strip()

    for entry in [c for c in plan["categories"] if c["action"] in KEEP] + plan.get("new_categories", []):
        d = describe(entry)
        if not 120 <= len(d) <= 160:
            issues.append(f"description of '{entry.get('new_name') or entry['name']}' is {len(d)} characters (120-160)")

    redirects = []
    for c in plan["categories"]:
        before = old_path(c["id"])
        if c["action"] in KEEP:
            after = new_path(c.get("new_name") or c["name"])
        elif c["action"] == "merge" and c.get("merge_into") in final:
            after = new_path(c["merge_into"])
        elif c["action"] == "move_to_tag" and c.get("tag"):
            after = f"/tag/{tag_slug.get(c['tag'], slugify(c['tag']))}/"
        else:
            continue
        if after != before:
            redirects.append((before, after, c["name"]))
    redirects += [(r["from"], r["to"], "manual") for r in plan.get("redirects", [])]

    def target(c):
        if c["action"] == "rename":
            return c.get("new_name", "")
        if c["action"] == "reparent":
            return f"under {c.get('new_parent') or 'top level'}"
        if c["action"] == "merge":
            return c.get("merge_into", "")
        if c["action"] == "move_to_tag":
            return f"tag: {c.get('tag', '')}"
        return ""

    sheets = {
        "Plan": [["ID", "Category", "Slug", "Parent", "Posts", "Action", "Target", "New slug", "Reason"]]
        + [[c["id"], c["name"], c["slug"], live_name.get(live[c["id"]]["parent"], ""), live[c["id"]]["count"],
            c["action"], target(c), c.get("new_slug", ""), c.get("reason", "")] for c in plan["categories"]]
        + [["new", n["name"], n["slug"], n.get("parent") or "", usage.get(n["name"], 0), "create", "", n["slug"],
            n.get("reason", "")] for n in plan.get("new_categories", [])],
        "Descriptions": [["Category", "Description", "Length"]]
        + [[c.get("new_name") or c["name"], describe(c), len(describe(c))]
           for c in plan["categories"] if c["action"] in KEEP]
        + [[n["name"], describe(n), len(describe(n))] for n in plan.get("new_categories", [])],
        "Recategorize": [["Post ID", "Title", "Current categories", "Proposed categories (primary first)",
                          "Tags to add"]]
        + [[p["id"], p.get("title", ""), ", ".join(p["current"]), ", ".join(p["proposed"]),
            ", ".join(p.get("add_tags", []))] for p in plan.get("posts", [])],
        "Redirects": [["From", "To", "Code", "Old category"]] + [[f, t, 301, n] for f, t, n in redirects],
    }
    write_xlsx(out, sheets)
    with open(os.path.join(os.path.dirname(out), "redirects.csv"), "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["source", "target", "regex", "code"])
        for f, t, _ in redirects:
            writer.writerow([f, t, 0, 301])

    before_outside = sum(not 1 <= len(p["categories"]) <= 2 for p in taxonomy["posts"])
    after_outside = sum(not 1 <= len(n) <= 2 for n in projected.values())
    print(f"Saved {out} and redirects.csv ({len(redirects)} redirect(s))")
    print("| Measure | Before | After |\n| --- | --- | --- |")
    print(f"| Categories | {len(live)} | {len(final)} |")
    print(f"| Empty categories | {sum(c['count'] == 0 for c in live.values())} | "
          f"{sum(usage.get(n, 0) == 0 for n in final)} |")
    print(f"| Posts outside 1-2 categories | {before_outside} | {after_outside} |")
    if issues:
        print(f"\nPlan issues ({len(issues)}):")
        for i in issues:
            print(f"  - {i}")
        return 1
    print("\nPlan checks: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
