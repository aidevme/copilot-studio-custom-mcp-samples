# Category plan format (`category_plan.json`)

<!-- cspell:ignore aidevme Dataverse recategorize Recategorize reparent Zsolt Billund -->

The plan step writes the plan as JSON. `category_plan_to_xlsx.py` turns it into the spreadsheet and the redirect
CSV, and `apply_category_plan.py` applies it. One file, so what Zsolt approves is exactly what runs.

```json
{
  "site": "https://aidevme.com",
  "based_on": "aidevme_taxonomy.json",
  "retrieved": "2026-10-26T06:45:31+00:00",
  "new_categories": [
    {"name": "Build AI agents", "slug": "build-ai-agents", "parent": null,
     "reason": "Pillar for AI that runs inside the delivered solution.",
     "description": "Copilot Studio, Microsoft Foundry and agent-ready Dataverse: designing, securing and running AI agents inside Power Platform solutions."}
  ],
  "categories": [
    {"id": 124, "name": "Copilot Studio", "slug": "copilot-studio", "parent": 93, "count": 4,
     "action": "move_to_tag", "tag": "Copilot Studio", "reason": "A product, so it belongs in tags."},
    {"id": 282, "name": "Canvas Apps", "slug": "canvas-app", "parent": 141, "count": 4,
     "action": "reparent", "new_parent": "Pro-code Power Platform", "new_slug": "canvas-apps",
     "reason": "Sub-topic of the Pro-code pillar.",
     "description": "Canvas apps and custom pages built like software: components, delegation, Dataverse patterns and the trade-offs against code apps."},
    {"id": 43, "name": "Power Platform", "slug": "power-platform", "parent": 0, "count": 28,
     "action": "delete", "reason": "Generic: every post is Power Platform, so it filters nothing."}
  ],
  "posts": [
    {"id": 21110, "title": "Nordic Summit 2026 in Billund", "current": ["AI & Copilot", "Power Platform", "Sessions"],
     "proposed": ["Open source and speaking"], "add_tags": ["Copilot Studio"]}
  ]
}
```

## Fields

| Field | Required | Meaning |
| --- | --- | --- |
| `categories[]` | yes | Every existing category, exactly once |
| `categories[].action` | yes | `keep`, `rename`, `reparent`, `merge`, `move_to_tag` or `delete` |
| `categories[].reason` | yes | One sentence |
| `new_name`, `new_slug` | rename (optional on reparent) | The new name and slug |
| `new_parent` | reparent (optional on rename) | Name of the new parent (kept or new category), or `null` for top level |
| `merge_into` | merge | Name of the surviving category, after renames |
| `tag` | move_to_tag | Name of the tag the posts get instead (an existing tag's exact name, or a new one) |
| `description` | keep, rename, reparent; every new category | 120–160 characters, 1–2 sentences |
| `new_categories[]` | no | Categories to create, usually the pillars: `name`, `slug`, `parent` (name or `null`), `description`, `reason` |
| `posts[]` | yes | Every post whose categories change: `current` and `proposed` category **names** after renames, primary first, 1–2 entries; optional `add_tags` |

## Actions

| Action | Effect when applied |
| --- | --- |
| `keep` | Description updated if it changed |
| `rename` | Name, slug (and parent, if given) updated; a 301 when the URL changes |
| `reparent` | Parent (and slug, if given) updated; a 301, because the URL contains the parent path |
| `merge` | Posts get the surviving category; the category is deleted once empty; a 301 to the survivor |
| `move_to_tag` | Posts get the tag; the category is deleted once empty; a 301 to the tag archive |
| `delete` | Posts lose it through the post list; deleted once empty; no redirect unless added by hand |

WordPress category URLs include every parent (`/category/power-apps/canvas-app/`), so a reparent changes the URL
even when the slug stays the same. The default category ("Uncategorized") can't be deleted until another category
is set as the default in **Settings → Writing → Default Post Category**.

Manual redirects for deleted categories that still get traffic go in an optional `redirects` list:
`[{"from": "/category/power-platform/", "to": "/"}]`.
