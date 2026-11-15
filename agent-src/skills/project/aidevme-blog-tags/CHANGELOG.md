# Changelog

<!-- cspell:ignore aidevme evals Evals difflib Dataverse Retag Zsolt -->
<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->

All notable changes to the **aidevme-blog-tags** skill: auditing and optimizing the WordPress tags of aidevme.com.
Newest first. Each entry says what changed and why it matters to you; the commit has the detail. The source is
`agent-src/skills/project/aidevme-blog-tags/`, synced to `.claude/skills/` and `.github/skills/`.

## 2026-11-01

### Changed

- **Post folders moved:** the evaluation prompts now use `.content/wordpress-posts/<slug>/`.

## 2026-10-27

### Added

- **MIT license:** a `LICENSE` file, so the skill keeps its license when it's shared on its own.

## 2026-10-26

### Changed

- **Categories come with description and link.** `fetch_taxonomy.py` and `fetch_taxonomy.js` also retrieve each
  category's description and URL, so the new aidevme-blog-categories skill can reuse the same taxonomy file.

## 2026-10-25

### Added

- **The skill itself:** retrieve → analyze → optimize → apply for the blog's tags, with the taxonomy rule
  (categories are pillars, tags are products), the five pillars, 25 canonical product tags and the targets (3–6
  tags per post, 3+ posts per tag, 120–160 character descriptions, no near-duplicates). Every run is saved in a new
  folder under `.research/aidevme-blog-tags/`.
- **Retrieval:** `scripts/fetch_taxonomy.js` for the browser console and `scripts/fetch_taxonomy.py` for a local
  shell, both paginating with `X-WP-TotalPages` into one `aidevme_taxonomy.json`. They send a browser user agent,
  because the site firewall answers 406 to short ones.
- **Analysis:** `scripts/analyze_tags.py` writes `tag_analysis.json` and a summary: inventory, thin and unused tags,
  near-duplicates (normalized names, known aliases, difflib ≥ 0.85), category and pillar clashes, spelling against
  the canonical list, `-2` slugs, missing and off-length descriptions, generic tags, posts outside 3–6 tags,
  co-occurring pairs, stale tags and a count sanity check.
- **Plan and spreadsheet:** the `tag_plan.json` format in [references/plan-format.md](references/plan-format.md),
  and `scripts/plan_to_xlsx.py`, which writes `tag_plan.xlsx` (Plan, Descriptions, Retag, Redirects),
  `redirects.csv` for the Redirection plugin and before/after numbers, and checks the plan against the targets.
- **Apply:** `scripts/apply_tag_plan.py`, which Zsolt runs with credentials from `AIDEVME_WP_USER` and
  `AIDEVME_WP_APP_PASSWORD`. It dry-runs by default, needs `--apply` to write, deletes only tags without posts
  after a typed `DELETE`, and logs every request to `tag_changes.log`. Manual WordPress click paths are the
  alternative.
- **Evals:** four cases that should trigger the skill and two that shouldn't.
