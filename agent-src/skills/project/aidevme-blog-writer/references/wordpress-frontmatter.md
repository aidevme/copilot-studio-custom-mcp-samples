# WordPress frontmatter and Markdown rules

<!-- cspell:ignore aidevme Dataverse jetpack -->

Drafts live in `.content/wordpress-posts/<slug>/index.md` with images in `.content/wordpress-posts/<slug>/images/`. The frontmatter is
structured for a future WordPress REST API publishing script; until that exists, it doubles as the manual
publishing checklist.

## Frontmatter

```yaml
---
title: "Connecting Claude Code to the Dataverse MCP Server"
slug: claude-code-dataverse-mcp-server
status: draft                     # draft | ready — the script maps "ready" to a WordPress draft for final review
excerpt: "How to connect Claude Code to the Dataverse MCP server, what the tools can do, and the security settings to check first."
categories: [mcp]                                 # 1 primary (+ ≤ 1 secondary) existing category slug
tags: [Claude Code, Dataverse, MCP Server]        # existing tag names; new ones flagged in the review
featured_image: images/featured.png
featured_image_alt: "Claude Code connected to Dataverse through the MCP server"
post_type: guide                  # deep-dive | guide | news-analysis | lessons-learned | release | personal
reading_time_min: 15
sources_checked: 2026-10-22
new_tags: []                      # tags that don't exist yet, for explicit approval
---
```

| Field | Required | Rule |
| --- | --- | --- |
| `title` | yes | Key terms first; see the SEO checklist |
| `slug` | yes | Unique — check that `https://aidevme.com/<slug>/` doesn't already exist |
| `status` | yes | Always `draft` from this skill; the user changes it |
| `excerpt` | yes | ≤ 155 characters |
| `categories` | yes | 1 primary + ≤ 1 secondary existing slug; never `power-platform` by default |
| `tags` | yes | 3–6, existing names preferred |
| `featured_image`, `featured_image_alt` | yes | Path relative to the post folder |
| `post_type`, `reading_time_min`, `sources_checked` | yes | Reading time ≈ words ÷ 230 |
| `new_tags` | no | Only when a new tag is genuinely needed |

## Live taxonomy lookup

```bash
# Categories: name, slug, parent, post count
curl -s "https://aidevme.com/wp-json/wp/v2/categories?per_page=100&_fields=id,name,slug,parent,count"

# Tags, most used first (repeat with &page=2 … if needed)
curl -s "https://aidevme.com/wp-json/wp/v2/tags?per_page=100&orderby=count&order=desc&_fields=id,name,slug,count"

# Check a slug isn't taken (empty array = free)
curl -s "https://aidevme.com/wp-json/wp/v2/posts?slug=<slug>&_fields=id,link"

# Recent posts, for internal links
curl -s "https://aidevme.com/wp-json/wp/v2/posts?per_page=20&_fields=title,link,date"
```

Rules (owned by **aidevme-blog-optimization** — categories are pillars, tags are products): pick the most
specific existing category that matches the post's pillar as primary, add a secondary only when the post
genuinely serves a second pillar; don't add "Power Platform" by default; don't use empty or legacy categories (`blog`, `features`, `portfolio`, `uncategorized`); match existing tag
spelling exactly (e.g. "Claude Code", "MCP Server", "PAC CLI").

## Markdown rules for WordPress

- Don't put the title as `#` in the body; start with the opening paragraph. Body headings start at `##`.
- Don't write a manual table of contents — published posts show a generated one. *(Assumption: verify against
  the theme/plugin before the publishing script is built.)*
- Fenced code blocks always declare a language (`bash`, `json`, `powershell`, `typescript`, `csharp`, `xml`).
- Tables: GitHub-flavoured Markdown, header row required, no merged cells. The Markdown table is the source;
  `scripts/export_tables.py` writes each one to `tables/<NN>-<heading>.html` as a WordPress table block, with
  every row (header included) as `<td>` cells in `<tbody>`:
  `<figure class="wp-block-table"><table class="has-fixed-layout"><tbody><tr><td>…</td></tr></tbody></table></figure>`.
  Inline bold, italics, code and links become HTML. Re-run the script after editing a table.
- **Mermaid doesn't render on WordPress:** export diagrams to SVG/PNG in `images/` and reference the image;
  keep the `.mmd` source next to it.
- Images: relative paths (`images/name.png`) with alt text; the script uploads them to the media library.
- Callouts: a bold label at the start of a paragraph (`**Current status:** …`) — no HTML or plugin shortcodes.
- Links: absolute URLs for external links; full `https://aidevme.com/<slug>/` for internal ones.

## Post folder

```text
.content/wordpress-posts/<slug>/
├── index.md
├── images/
│   ├── featured.png
│   ├── <diagram>.mmd
│   └── <diagram>.svg
└── tables/                  only when the post has tables
    ├── 01-<heading>.html     one WordPress table block per table, in post order
    └── 02-<heading>.html
```
