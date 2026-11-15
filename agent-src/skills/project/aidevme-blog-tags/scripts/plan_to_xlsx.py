#!/usr/bin/env python3
"""Turn tag_plan.json into tag_plan.xlsx (tabs Plan, Descriptions, Retag, Redirects), redirects.csv for the
Redirection plugin, and before/after numbers. Also validates the plan against the targets: kept tags with at least
3 posts, descriptions of 120-160 characters, 3-6 tags per post, and every tag in the plan exactly once.
Standard library only (writes the .xlsx directly).

Usage:
  python plan_to_xlsx.py tag_plan.json [--taxonomy aidevme_taxonomy.json] [--out tag_plan.xlsx]
"""
import argparse
import csv
import json
import os
import sys
import zipfile
from xml.sax.saxutils import escape

KEEP_ACTIONS = {"keep", "rename", "new_product"}
GONE_ACTIONS = {"merge", "move_to_category", "delete"}


def column(n):
    name = ""
    while n:
        n, r = divmod(n - 1, 26)
        name = chr(65 + r) + name
    return name


def sheet_xml(rows):
    out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
           '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">',
           '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" state="frozen"/>'
           '</sheetView></sheetViews><sheetData>']
    for r, row in enumerate(rows, start=1):
        out.append(f'<row r="{r}">')
        for c, value in enumerate(row, start=1):
            ref = f"{column(c)}{r}"
            style = ' s="1"' if r == 1 else ""
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                out.append(f'<c r="{ref}"{style}><v>{value}</v></c>')
            else:
                text = escape("" if value is None else str(value))
                out.append(f'<c r="{ref}" t="inlineStr"{style}><is><t xml:space="preserve">{text}</t></is></c>')
        out.append("</row>")
    out.append("</sheetData></worksheet>")
    return "".join(out)


def write_xlsx(path, sheets):
    names = list(sheets)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                   '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                   '<Default Extension="xml" ContentType="application/xml"/>'
                   '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
                   '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
                   + "".join(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                             for i in range(1, len(names) + 1)) + "</Types>")
        z.writestr("_rels/.rels",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
                   "</Relationships>")
        z.writestr("xl/workbook.xml",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                   'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
                   + "".join(f'<sheet name="{escape(n)}" sheetId="{i}" r:id="rId{i}"/>' for i, n in enumerate(names, 1))
                   + "</sheets></workbook>")
        z.writestr("xl/_rels/workbook.xml.rels",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   + "".join(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>'
                             for i in range(1, len(names) + 1))
                   + f'<Relationship Id="rId{len(names) + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
                   "</Relationships>")
        z.writestr("xl/styles.xml",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                   '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font>'
                   '<font><b/><sz val="11"/><name val="Calibri"/></font></fonts>'
                   '<fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>'
                   '<borders count="1"><border/></borders><cellStyleXfs count="1"><xf/></cellStyleXfs>'
                   '<cellXfs count="2"><xf fontId="0"/><xf fontId="1" applyFont="1"/></cellXfs></styleSheet>')
        for i, n in enumerate(names, 1):
            z.writestr(f"xl/worksheets/sheet{i}.xml", sheet_xml(sheets[n]))


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("plan")
    parser.add_argument("--taxonomy", help="default: the plan's based_on file, next to the plan")
    parser.add_argument("--out", help="default: tag_plan.xlsx next to the plan")
    args = parser.parse_args()

    folder = os.path.dirname(os.path.abspath(args.plan))
    plan = json.load(open(args.plan, encoding="utf-8"))
    taxonomy_path = args.taxonomy or os.path.join(folder, plan.get("based_on", "aidevme_taxonomy.json"))
    taxonomy = json.load(open(taxonomy_path, encoding="utf-8"))
    out = args.out or os.path.join(folder, "tag_plan.xlsx")
    categories = {c["id"]: c for c in taxonomy["categories"]}
    live = {t["id"]: t for t in taxonomy["tags"]}
    issues = []

    planned = [t["id"] for t in plan["tags"]]
    missing = sorted(set(live) - set(planned))
    dupes = sorted({i for i in planned if planned.count(i) > 1})
    if missing:
        issues.append(f"{len(missing)} live tag(s) not in the plan: {missing[:10]}")
    if dupes:
        issues.append(f"tag(s) listed twice: {dupes}")

    final_name = {}
    for t in plan["tags"]:
        if t["action"] in KEEP_ACTIONS:
            final_name[t["id"]] = t.get("new_name") or t["name"]
    kept_names = set(final_name.values()) | {n["name"] for n in plan.get("new_tags", [])}
    for t in plan["tags"]:
        if t["action"] == "merge" and t.get("merge_into") not in kept_names:
            issues.append(f"'{t['name']}' merges into '{t.get('merge_into')}', which isn't a kept or new tag")

    # Projected tags per post: posts listed in the plan use 'proposed'; the rest keep their current tags.
    listed = {p["id"]: p for p in plan.get("posts", [])}
    projected = {}
    for post in taxonomy["posts"]:
        if post["id"] in listed:
            projected[post["id"]] = list(listed[post["id"]]["proposed"])
        else:
            projected[post["id"]] = [final_name[i] for i in post["tags"] if i in final_name]
            gone = [live[i]["name"] for i in post["tags"] if i in live and i not in final_name]
            if gone:
                issues.append(f"post {post['id']} has tags that go away ({', '.join(gone)}) but no retag entry")
    usage = {}
    for names in projected.values():
        for n in names:
            usage[n] = usage.get(n, 0) + 1
    for n in sorted(set(usage) - kept_names):
        issues.append(f"proposed tag '{n}' isn't a kept or new tag")

    def description_of(t):
        return (t.get("description") or "").strip()

    for t in [t for t in plan["tags"] if t["action"] in KEEP_ACTIONS] + plan.get("new_tags", []):
        d = description_of(t)
        if not 120 <= len(d) <= 160:
            issues.append(f"description of '{t.get('new_name') or t['name']}' is {len(d)} characters (120-160)")
    for n in sorted(kept_names):
        if usage.get(n, 0) < 3:
            issues.append(f"kept tag '{n}' would have {usage.get(n, 0)} post(s) (target: 3+)")
    outside_after = [pid for pid, names in projected.items() if not 3 <= len(names) <= 6]
    if outside_after:
        issues.append(f"{len(outside_after)} post(s) still outside 3-6 tags: {outside_after[:10]}")

    redirects = []
    slug_of = {(t.get("new_name") or t["name"]): (t.get("new_slug") or t["slug"])
               for t in plan["tags"] if t["action"] in KEEP_ACTIONS}
    slug_of.update({n["name"]: n["slug"] for n in plan.get("new_tags", [])})
    for t in plan["tags"]:
        if t["action"] == "rename" and t.get("new_slug") and t["new_slug"] != t["slug"]:
            redirects.append((f"/tag/{t['slug']}/", f"/tag/{t['new_slug']}/", t["name"]))
        elif t["action"] == "merge" and t.get("merge_into") in slug_of:
            redirects.append((f"/tag/{t['slug']}/", f"/tag/{slug_of[t['merge_into']]}/", t["name"]))
        elif t["action"] == "move_to_category" and t.get("category_id") in categories:
            redirects.append((f"/tag/{t['slug']}/", f"/category/{categories[t['category_id']]['slug']}/", t["name"]))
    redirects += [(r["from"], r["to"], "manual") for r in plan.get("redirects", [])]

    def target(t):
        if t["action"] == "rename":
            return t.get("new_name")
        if t["action"] == "merge":
            return t.get("merge_into")
        if t["action"] == "move_to_category":
            c = categories.get(t.get("category_id"))
            return c["name"] if c else t.get("category_id")
        return ""

    sheets = {
        "Plan": [["ID", "Tag", "Slug", "Posts", "Action", "Target", "New slug", "Reason"]]
        + [[t["id"], t["name"], t["slug"], t.get("count", live.get(t["id"], {}).get("count", "")), t["action"],
            target(t), t.get("new_slug", ""), t.get("reason", "")] for t in plan["tags"]]
        + [["new", n["name"], n["slug"], usage.get(n["name"], 0), "create", "", n["slug"], n.get("reason", "")]
           for n in plan.get("new_tags", [])],
        "Descriptions": [["ID", "Tag", "Description", "Length"]]
        + [[t["id"], t.get("new_name") or t["name"], description_of(t), len(description_of(t))]
           for t in plan["tags"] if t["action"] in KEEP_ACTIONS]
        + [["new", n["name"], description_of(n), len(description_of(n))] for n in plan.get("new_tags", [])],
        "Retag": [["Post ID", "Title", "Current tags", "Proposed tags", "Tags before", "Tags after"]]
        + [[p["id"], p.get("title", ""), ", ".join(p["current"]), ", ".join(p["proposed"]), len(p["current"]),
            len(p["proposed"])] for p in plan.get("posts", [])],
        "Redirects": [["From", "To", "Code", "Old tag"]] + [[f, t, 301, n] for f, t, n in redirects],
    }
    write_xlsx(out, sheets)
    with open(os.path.join(os.path.dirname(out), "redirects.csv"), "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["source", "target", "regex", "code"])
        for f, t, _ in redirects:
            writer.writerow([f, t, 0, 301])

    before_thin = sum(1 <= t["count"] <= 2 for t in live.values())
    after_thin = sum(1 <= usage.get(n, 0) <= 2 for n in kept_names)
    before_outside = sum(not 3 <= len(p["tags"]) <= 6 for p in taxonomy["posts"])
    print(f"Saved {out} and redirects.csv ({len(redirects)} redirect(s))")
    print("| Measure | Before | After |\n| --- | --- | --- |")
    print(f"| Tags | {len(live)} | {len(kept_names)} |")
    print(f"| Thin tags (1-2 posts) | {before_thin} | {after_thin} |")
    print(f"| Posts outside 3-6 tags | {before_outside} | {len(outside_after)} |")
    if issues:
        print(f"\nPlan issues ({len(issues)}):")
        for i in issues:
            print(f"  - {i}")
        return 1
    print("\nPlan checks: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
