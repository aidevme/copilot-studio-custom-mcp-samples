# Tag plan format (`tag_plan.json`)

<!-- cspell:ignore aidevme Dataverse Billund retag -->

The optimize step writes the plan as JSON. `plan_to_xlsx.py` turns it into the spreadsheet and the redirect CSV,
and `apply_tag_plan.py` applies it. One file, so what you approve is exactly what runs.

```json
{
  "site": "https://aidevme.com",
  "based_on": "aidevme_taxonomy.json",
  "retrieved": "2026-10-25T06:40:24+00:00",
  "tags": [
    {"id": 163, "name": "MCP Server", "slug": "mcp-server", "count": 8, "action": "rename",
     "new_name": "MCP", "new_slug": "mcp", "reason": "Canonical product name; MCP Server is the same topic.",
     "description": "Model Context Protocol (MCP) servers and clients for Power Platform: tool design, Dataverse MCP, transports and deployment, from a pro-code angle."},
    {"id": 412, "name": "Model Context Protocol", "slug": "model-context-protocol", "count": 3,
     "action": "merge", "merge_into": "MCP", "reason": "Same topic as MCP."},
    {"id": 52, "name": "Power Platform", "slug": "power-platform", "count": 18, "action": "delete",
     "reason": "Generic: every post is Power Platform, so the tag filters nothing."},
    {"id": 300, "name": "ALM", "slug": "alm", "count": 5, "action": "move_to_category",
     "category_id": 41, "reason": "ALM is a pillar (ALM and governance), not a product."}
  ],
  "new_tags": [
    {"name": "Custom pages", "slug": "custom-pages", "reason": "Canonical product with 3 posts, no tag yet.",
     "description": "Custom pages in model-driven apps: building them with canvas or code, navigation, and ALM, with examples from real projects."}
  ],
  "posts": [
    {"id": 21110, "title": "Nordic Summit 2026 in Billund", "current": ["Speaking", "Power Platform"],
     "proposed": ["Copilot Studio", "Agent skills", "Claude Code"]}
  ]
}
```

## Fields

| Field | Required | Meaning |
| --- | --- | --- |
| `tags[]` | yes | Every existing tag, exactly once |
| `tags[].action` | yes | `keep`, `rename`, `merge`, `move_to_category`, `delete` or `new_product` |
| `tags[].reason` | yes | One sentence |
| `tags[].new_name`, `new_slug` | rename | The canonical name and slug |
| `tags[].merge_into` | merge | Name of the surviving tag, after renames (an existing or a `new_tags` name) |
| `tags[].category_id` | move_to_category | Category the tag's posts get instead |
| `tags[].description` | keep, rename, new_product | 120–160 characters, 1–2 sentences |
| `new_tags[]` | no | Tags to create: `name`, `slug`, `description`, `reason` |
| `posts[]` | yes | Every post whose tags change: `current` and `proposed` tag **names**, after renames |

## Actions

| Action | Effect when applied |
| --- | --- |
| `keep` | Description updated if it changed |
| `rename` | Name, slug and description updated; a 301 from the old tag URL |
| `merge` | Posts get the target tag instead; the tag is deleted once it has no posts; a 301 to the target |
| `move_to_category` | The tag's posts get `category_id`; the tag is deleted once it has no posts; a 301 to the category |
| `delete` | Removed from posts by the retag list; deleted once it has no posts; no redirect unless the plan adds one |
| `new_product` | An existing tag that isn't on the canonical list but is a real product; kept, and listed for confirmation |

Redirects are derived from the plan: `/tag/<old-slug>/` → `/tag/<new-slug>/` for renames and merges, and
`/tag/<old-slug>/` → `/category/<category-slug>/` for moves. Deleted tags with posts in search results can be
redirected by adding them to `redirects` by hand (`{"from": "/tag/x/", "to": "/"}`).
