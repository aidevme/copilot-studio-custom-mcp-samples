#!/usr/bin/env python3
"""Apply an approved category_plan.json to aidevme.com through the WordPress REST API. Zsolt runs this, not the
agent.

Order: create new categories (parents first) -> rename, reparent and update descriptions -> recategorize posts
(proposed categories, plus tags for move_to_tag) -> delete merged, moved and deleted categories that have no posts
left. Every request is logged to category_changes.log. Reuses the REST client from aidevme-blog-tags'
apply_tag_plan.py.

Safety:
  - Dry run by default: prints every request and writes nothing. --apply is required to write.
  - Credentials come only from AIDEVME_WP_USER and AIDEVME_WP_APP_PASSWORD (a WordPress application password).
  - Before deleting, each category is re-read; any that still has posts is skipped. The rest are listed and need
    a typed DELETE. The default category ("Uncategorized") is never deleted. Take a database backup first.

Usage:
  python apply_category_plan.py category_plan.json             # dry run
  python apply_category_plan.py category_plan.json --apply     # write
"""
import argparse
import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "aidevme-blog-tags",
                                "scripts"))
from apply_tag_plan import Client  # noqa: E402

KEEP = {"keep", "rename", "reparent"}
GONE = {"merge", "move_to_tag", "delete"}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("plan")
    parser.add_argument("--apply", action="store_true", help="write the changes (default: dry run)")
    parser.add_argument("--log", help="default: category_changes.log next to the plan")
    args = parser.parse_args()

    plan = json.load(open(args.plan, encoding="utf-8"))
    log = args.log or os.path.join(os.path.dirname(os.path.abspath(args.plan)), "category_changes.log")
    wp = Client(plan.get("site", "https://aidevme.com"), args.apply, log)

    cats = {c["id"]: c for c in wp.get_all("categories?per_page=100&_fields=id,name,slug,count,description,parent")}
    tags = {t["name"]: t["id"] for t in wp.get_all("tags?per_page=100&_fields=id,name")}
    posts = {p["id"]: p for p in wp.get_all("posts?per_page=100&_fields=id,categories,tags")}
    for c in plan["categories"]:
        if c["id"] not in cats:
            raise SystemExit(f"Category {c['id']} ({c['name']}) is no longer on the site; retrieve and analyze again.")

    id_by_name = {c.get("new_name") or c["name"]: c["id"] for c in plan["categories"] if c["action"] in KEEP}

    # 1. Create new categories, parents before children.
    pending = list(plan.get("new_categories", []))
    while pending:
        progressed = False
        for n in list(pending):
            parent = n.get("parent")
            if parent and parent not in id_by_name:
                continue
            existing = [c for c in cats.values() if c["slug"] == n["slug"]]
            if existing:
                id_by_name[n["name"]] = existing[0]["id"]
                wp.write(f"'{n['name']}' already exists as category {existing[0]['id']}; not created.")
            else:
                body = {"name": n["name"], "slug": n["slug"], "description": n.get("description", ""),
                        "parent": id_by_name[parent] if parent else 0}
                created = wp.change("POST", "categories", body, "(create)")
                id_by_name[n["name"]] = created["id"] if created else f"<new:{n['name']}>"
            pending.remove(n)
            progressed = True
        if not progressed:
            raise SystemExit("New categories reference parents that don't exist: "
                             + ", ".join(n["name"] for n in pending))

    # 2. Rename, reparent and update descriptions.
    for c in plan["categories"]:
        if c["action"] not in KEEP:
            continue
        live = cats[c["id"]]
        body = {}
        if c.get("new_name") and c["new_name"] != live["name"]:
            body["name"] = c["new_name"]
        if c.get("new_slug") and c["new_slug"] != live["slug"]:
            body["slug"] = c["new_slug"]
        if "new_parent" in c:
            parent_id = id_by_name.get(c["new_parent"], 0) if c["new_parent"] else 0
            if parent_id != live["parent"]:
                body["parent"] = parent_id
        if c.get("description") is not None and c["description"].strip() != (live.get("description") or "").strip():
            body["description"] = c["description"].strip()
        if body:
            wp.change("POST", f"categories/{c['id']}", body, f"({live['name']})")

    # 3. Recategorize posts; move_to_tag also adds the tag.
    for p in plan.get("posts", []):
        if p["id"] not in posts:
            wp.write(f"WARNING: post {p['id']} not found; skipped.")
            continue
        try:
            new_cats = [id_by_name[name] for name in p["proposed"]]
        except KeyError as missing:
            raise SystemExit(f"Post {p['id']}: proposed category {missing} isn't a kept or new category.")
        new_tags = list(posts[p["id"]]["tags"])
        for name in p.get("add_tags", []):
            if name not in tags:
                created = wp.change("POST", "tags", {"name": name}, "(create tag)")
                tags[name] = created["id"] if created else f"<new tag:{name}>"
            if tags[name] not in new_tags:
                new_tags.append(tags[name])
        body = {}
        if [str(i) for i in new_cats] != [str(i) for i in posts[p["id"]]["categories"]]:
            body["categories"] = new_cats
        if new_tags != posts[p["id"]]["tags"]:
            body["tags"] = new_tags
        if body:
            wp.change("POST", f"posts/{p['id']}", body, f"({p.get('title', '')[:50]})")

    # 4. Delete categories that are gone, only when empty, never the default category.
    gone = [c for c in plan["categories"] if c["action"] in GONE]
    deletable, blocked = [], []
    for c in gone:
        if cats[c["id"]]["slug"] == "uncategorized":
            wp.write("NOT DELETED: 'Uncategorized' is the default category; change the default in Settings → Writing.")
            continue
        if args.apply:
            _, fresh, _ = wp.request("GET", f"categories/{c['id']}?_fields=id,count")
            count = fresh["count"]
        else:
            listed = {p["id"] for p in plan.get("posts", [])}
            count = sum(1 for pid, post in posts.items() if c["id"] in post["categories"] and pid not in listed)
        (deletable if count == 0 else blocked).append((c, count))
    for c, count in blocked:
        wp.write(f"NOT DELETED: '{c['name']}' ({c['id']}) still has {count} post(s); add them to the post list.")
    if not deletable:
        wp.write("No categories to delete.")
        return 0
    wp.write(f"Categories to delete ({len(deletable)}):")
    for c, _ in deletable:
        wp.write(f"  {c['id']}  {c['name']}  ({c['action']})")
    if args.apply:
        answer = input(f"Type DELETE to delete these {len(deletable)} categories permanently (anything else skips): ")
        if answer.strip() != "DELETE":
            wp.write("Deletions skipped by the user.")
            return 0
    for c, _ in deletable:
        wp.change("DELETE", f"categories/{c['id']}?force=true", None, f"({c['name']})")
    wp.write("Done. Retrieve and analyze again to report before/after.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
