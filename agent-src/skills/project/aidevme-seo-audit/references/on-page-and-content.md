# On-page and content criteria

<!-- cspell:ignore aidevme Dataverse Yoast -->

## Titles (Yoast SEO title)

The title has two jobs: match the query and win the click.

- **Key terms first**, then the reason to click (scope, outcome, number, format), brand last if at all.
- **About 50–60 characters** visible; Google truncates by pixel width. Long titles are fine on the page (the H1),
  but the SEO title should front-load the terms.
- **Unique** across the site; aligned with the H1, slug and excerpt.
- Only claim "complete guide", a year or a number when the post delivers it.
- Google rewrites titles that are bloated, keyword-stuffed, repeated boilerplate or out of line with the H1 —
  if the SERP shows a different title, tighten and align.

Patterns for aidevme post types:

| Post type | Pattern | Example |
| --- | --- | --- |
| Deep dive | `[Product/feature]: [what it means / the key angle]` | `Dataverse MCP Server: 15 Tools That Make Power Platform Agent-Ready` |
| Guide / tutorial | `How to [task] in [product]` or `[Product] [task]: Step-by-Step` | `How to Connect Claude Code to the Dataverse MCP Server` |
| News analysis | `[Announcement]: What It Means for [audience]` | `Copilot Code Review in Azure Repos: What It Means for Power Platform Teams` |
| Comparison | `[A] vs [B]: [deciding difference]` | `Canvas Apps vs Code Apps: Which to Build in 2026` |
| Troubleshooting | `[Error/symptom]: Cause and Fix` | `PCF Control Not Rendering in Model-Driven Apps: Cause and Fix` |

## Meta descriptions (Yoast meta description / excerpt)

- 150–160 characters; unique; states what the reader gets and for whom; contains the main term naturally.
- Missing or auto-generated descriptions let Google pick a snippet — flag them.

## Headings

- One H1 (WordPress renders the post title); body headings start at H2; no skipped levels.
- H2s describe the content and use the terms people search for; the first paragraph under each H2 answers it
  (this is also what AI assistants extract).

## URL / slug

- Short, lowercase, hyphenated, meaningful. aidevme's older slugs are full titles (very long) — report as Low
  impact and **don't change published slugs** for SEO alone.

## Images

- Descriptive file names, alt text on every informative image (diagrams: the description of what they show),
  compressed (WebP/AVIF where possible), lazy-loaded below the fold, a featured image with alt text.

## Internal links

- Each post links to 2–5 related aidevme posts with descriptive anchors, and receives links from related posts.
- Flagship guides should be the most-linked posts in their pillar.
- Flag orphans (no inbound internal links), "click here" anchors and links to redirected URLs.

## Content quality and E-E-A-T

| Signal | aidevme check |
| --- | --- |
| Experience | Hands-on detail: real config, errors, screenshots (demo data), lessons — or an honest "based on documentation" note |
| Expertise | Author box with MVP status and role; accurate, sourced claims; Resources section with official links |
| Authoritativeness | Talks, MVP profile, GitHub repos linked; cited by others (backlinks) |
| Trust | Dates (published and updated), About/Contact/Disclaimer pages, HTTPS, no broken links |

## Freshness (fast-moving Microsoft topics)

- Product names: Copilot Studio (not Power Virtual Agents), Dataverse (not CDS), Microsoft Foundry (not Azure AI
  Foundry, except when quoting older docs).
- Preview vs GA statuses and dates still accurate; screenshots match the current UI.
- Posts with outdated facts: recommend a refresh via **aidevme-blog-writer** (keeps the slug, adds an update note).

## Cannibalization

Group posts by primary topic and query. Two posts targeting the same query (e.g. several "Copilot Studio agent"
posts) split clicks and positions. Choose one owner per query, differentiate the others' angle or merge them
(merge = redirect task for **aidevme-blog-optimization**).

## AI-search readiness

- A plain definition of the main subject early in the post.
- Answer-first paragraphs, tables for comparisons and limits, numbered steps, explicit versions and dates.
- A Resources section linking official sources.
- `robots.txt` doesn't block AI crawlers you want to be cited by (decision for Zsolt; report what's set).

## Writing quality flags

Flag stock phrases ("game-changer", "unlock the power of", "in today's fast-paced world", "let's dive in"),
filler intensifiers and broetry; the voice rules live in `.claude/agents/aidevme-context.md`. Treat these as Low
impact for SEO unless they make the content thin or repetitive.
