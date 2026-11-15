# Changelog

<!-- cspell:ignore aidevme evals Evals Zsolt recategorize Recategorize reparent reparented difflib -->
<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->

All notable changes to the **aidevme-blog-categories** skill: auditing the WordPress categories of aidevme.com and
planning the move to the five pillars. Newest first. Each entry says what changed and why it matters to you; the
commit has the detail. The source is `agent-src/skills/project/aidevme-blog-categories/`, synced to
`.claude/skills/` and `.github/skills/`.

## 2026-11-01

### Changed

- **Shorter description:** cut to the 1,024-character limit of the Agent Skills specification, with every trigger
  phrase kept. It now points to related skills with "see", which clears the validator's warning.

## 2026-10-27

### Added

- **MIT license:** a `LICENSE` file, so the skill keeps its license when it's shared on its own.

## 2026-10-26

### Added

- **The skill itself:** retrieve → analyze → plan → apply for the blog's categories, following
  aidevme-blog-optimization's pillars and rules (one primary category, at most one secondary; products are tags).
  Every run is saved in a new folder under `.research/aidevme-blog-categories/`.
- **Retrieval reused from aidevme-blog-tags:** `fetch_taxonomy.py` (or `.js`) fetches categories with description,
  parent and link, plus posts and tags, into one `aidevme_taxonomy.json`.
- **Analysis:** `scripts/analyze_categories.py` writes `category_analysis.json` and a summary: the category tree,
  empty and thin categories, posts in more than two categories or in a category and its parent, product-named
  categories, categories duplicating tags, missing pillars, old names in slugs, descriptions and a count sanity
  check. It reuses aidevme-blog-tags' name normalization and canonical product list.
- **Plan and spreadsheet:** the `category_plan.json` format in
  [references/plan-format.md](references/plan-format.md) (keep, rename, reparent, merge, move to tag, delete, new
  categories, a recategorize list per post), and `scripts/category_plan_to_xlsx.py`, which writes
  `category_plan.xlsx` (Plan, Descriptions, Recategorize, Redirects), `redirects.csv` and before/after numbers.
  Redirects cover reparented categories and children of deleted parents, because category URLs contain the parent
  path.
- **Apply:** `scripts/apply_category_plan.py`, which Zsolt runs with credentials from `AIDEVME_WP_USER` and
  `AIDEVME_WP_APP_PASSWORD`. It dry-runs by default, creates parents before children, deletes only empty
  categories after a typed `DELETE`, never deletes the default category, and logs every request to
  `category_changes.log`.
- **Evals:** three cases that should trigger the skill and two that shouldn't.
