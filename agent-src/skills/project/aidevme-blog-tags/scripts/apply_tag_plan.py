#!/usr/bin/env python3
"""Apply an approved tag_plan.json to aidevme.com through the WordPress REST API. Zsolt runs this, not the agent.

Order: create new tags -> rename and update descriptions -> retag posts (which carries out merges and moves) ->
delete merged, moved and deleted tags that have no posts left. Every request is logged to tag_changes.log.

Safety:
  - Dry run by default: prints every request and writes nothing. --apply is required to write.
  - Credentials come only from the environment: AIDEVME_WP_USER and AIDEVME_WP_APP_PASSWORD (a WordPress
    application password, Users -> Profile -> Application Passwords). Nothing is stored or printed.
  - Before deleting, the script re-reads each tag, skips any that still has posts, lists the rest and asks you to
    type DELETE. Take a database backup first.

Usage:
  python apply_tag_plan.py tag_plan.json             # dry run
  python apply_tag_plan.py tag_plan.json --apply     # write
"""
import argparse
import base64
import datetime
import json
import os
import sys
import urllib.error
import urllib.request

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/126.0 Safari/537.36")
KEEP_ACTIONS = {"keep", "rename", "new_product"}
GONE_ACTIONS = {"merge", "move_to_category", "delete"}


class Client:
    def __init__(self, site, apply, log_path):
        self.base = site.rstrip("/") + "/wp-json/wp/v2"
        self.apply = apply
        self.log = open(log_path, "a", encoding="utf-8")
        self.auth = None
        user, password = os.environ.get("AIDEVME_WP_USER"), os.environ.get("AIDEVME_WP_APP_PASSWORD")
        if user and password:
            self.auth = "Basic " + base64.b64encode(f"{user}:{password}".encode()).decode()
        elif apply:
            raise SystemExit("Set AIDEVME_WP_USER and AIDEVME_WP_APP_PASSWORD (an application password) to apply.")
        self.write(f"--- {datetime.datetime.now().isoformat(timespec='seconds')} "
                   f"{'APPLY' if apply else 'DRY RUN'} ---")

    def write(self, line):
        print(line)
        self.log.write(line + "\n")
        self.log.flush()

    def request(self, method, path, body=None):
        url = f"{self.base}/{path}"
        headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
        if self.auth:
            headers["Authorization"] = self.auth
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8") or "null"), resp.headers
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", "replace")[:300]
            hint = " (a security plugin may be blocking the REST API)" if error.code in (401, 403, 404) else ""
            raise SystemExit(f"{method} {url}: HTTP {error.code}{hint}: {detail}")

    def get_all(self, path):
        items, page, pages = [], 1, 1
        while page <= pages:
            _, data, headers = self.request("GET", f"{path}&page={page}")
            pages = int(headers.get("X-WP-TotalPages") or 1)
            items += data
            page += 1
        return items

    def change(self, method, path, body=None, note=""):
        self.write(f"{'' if self.apply else '[dry run] '}{method} /wp/v2/{path} {json.dumps(body) if body else ''} {note}".rstrip())
        if self.apply:
            status, data, _ = self.request(method, path, body)
            self.write(f"  -> HTTP {status}")
            return data
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("plan")
    parser.add_argument("--apply", action="store_true", help="write the changes (default: dry run)")
    parser.add_argument("--log", help="default: tag_changes.log next to the plan")
    args = parser.parse_args()

    plan = json.load(open(args.plan, encoding="utf-8"))
    log = args.log or os.path.join(os.path.dirname(os.path.abspath(args.plan)), "tag_changes.log")
    wp = Client(plan.get("site", "https://aidevme.com"), args.apply, log)

    live_tags = {t["id"]: t for t in wp.get_all("tags?per_page=100&_fields=id,name,slug,count,description")}
    live_posts = {p["id"]: p for p in wp.get_all("posts?per_page=100&_fields=id,tags,categories")}
    for t in plan["tags"]:
        if t["id"] not in live_tags:
            raise SystemExit(f"Tag {t['id']} ({t['name']}) is no longer on the site; re-run retrieve and analyze.")
        if live_tags[t["id"]]["count"] != t.get("count", live_tags[t["id"]]["count"]):
            wp.write(f"WARNING: '{t['name']}' now has {live_tags[t['id']]['count']} posts, the plan says {t['count']}.")

    # 1. Create new tags.
    id_by_name = {}
    for n in plan.get("new_tags", []):
        existing = [t for t in live_tags.values() if t["slug"] == n["slug"]]
        if existing:
            id_by_name[n["name"]] = existing[0]["id"]
            wp.write(f"'{n['name']}' already exists as tag {existing[0]['id']}; not created.")
            continue
        created = wp.change("POST", "tags", {"name": n["name"], "slug": n["slug"], "description": n.get("description", "")},
                            "(create)")
        id_by_name[n["name"]] = created["id"] if created else f"<new:{n['name']}>"

    # 2. Rename and update descriptions.
    for t in plan["tags"]:
        if t["action"] not in KEEP_ACTIONS:
            continue
        live = live_tags[t["id"]]
        body = {}
        if t.get("new_name") and t["new_name"] != live["name"]:
            body["name"] = t["new_name"]
        if t.get("new_slug") and t["new_slug"] != live["slug"]:
            body["slug"] = t["new_slug"]
        if t.get("description") is not None and t["description"].strip() != (live.get("description") or "").strip():
            body["description"] = t["description"].strip()
        if body:
            wp.change("POST", f"tags/{t['id']}", body, f"({live['name']})")
        id_by_name[t.get("new_name") or t["name"]] = t["id"]

    # 3. Retag posts. Merges and moves happen here: the proposed list replaces the old tag.
    category_for = {t["id"]: t["category_id"] for t in plan["tags"] if t["action"] == "move_to_category"}
    for p in plan.get("posts", []):
        if p["id"] not in live_posts:
            wp.write(f"WARNING: post {p['id']} not found; skipped.")
            continue
        try:
            new_ids = [id_by_name[name] for name in p["proposed"]]
        except KeyError as missing:
            raise SystemExit(f"Post {p['id']}: proposed tag {missing} isn't a kept or new tag in the plan.")
        body = {}
        if sorted(map(str, new_ids)) != sorted(map(str, live_posts[p["id"]]["tags"])):
            body["tags"] = new_ids
        extra = [category_for[i] for i in live_posts[p["id"]]["tags"] if i in category_for]
        cats = list(dict.fromkeys(live_posts[p["id"]]["categories"] + extra))
        if cats != live_posts[p["id"]]["categories"]:
            body["categories"] = cats
        if body:
            wp.change("POST", f"posts/{p['id']}", body, f"({p.get('title', '')[:50]})")

    # 4. Delete tags that are gone, only when no post uses them any more.
    gone = [t for t in plan["tags"] if t["action"] in GONE_ACTIONS]
    if not gone:
        wp.write("No deletions in the plan.")
        return 0
    deletable, blocked = [], []
    for t in gone:
        if args.apply:
            _, fresh, _ = wp.request("GET", f"tags/{t['id']}?_fields=id,name,count")
            count = fresh["count"]
        else:
            still = [pid for pid, post in live_posts.items() if t["id"] in post["tags"]
                     and not any(p["id"] == pid for p in plan.get("posts", []))]
            count = len(still)
        (deletable if count == 0 else blocked).append((t, count))
    for t, count in blocked:
        wp.write(f"NOT DELETED: '{t['name']}' ({t['id']}) still has {count} post(s); add those posts to the retag list.")
    if not deletable:
        return 0
    wp.write(f"Tags to delete ({len(deletable)}):")
    for t, _ in deletable:
        wp.write(f"  {t['id']}  {t['name']}  /tag/{t['slug']}/  ({t['action']})")
    if args.apply:
        answer = input(f"Type DELETE to delete these {len(deletable)} tags permanently (anything else skips): ")
        if answer.strip() != "DELETE":
            wp.write("Deletions skipped by the user.")
            return 0
    for t, _ in deletable:
        wp.change("DELETE", f"tags/{t['id']}?force=true", None, f"({t['name']})")
    wp.write("Done. Re-run fetch_taxonomy.py and analyze_tags.py to report before/after.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
