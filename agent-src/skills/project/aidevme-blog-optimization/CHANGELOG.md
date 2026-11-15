# Changelog

<!-- cspell:ignore aidevme Zsolt evals Evals -->
<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->

All notable changes to the **aidevme-blog-optimization** skill: positioning, menu and category structure,
homepage, post placement, redirects and site metadata for aidevme.com. Newest first. Each entry says what changed
and why it matters to you; the commit has the detail. The source is
`agent-src/skills/project/aidevme-blog-optimization/`, synced to `.claude/skills/` and `.github/skills/`.

## 2026-11-01

### Changed

- **Post folders moved:** draft paths now point to `.content/wordpress-posts/<slug>/`.

## 2026-10-27

### Added

- **MIT license:** a `LICENSE` file, so the skill keeps its license when it's shared on its own.

## 2026-10-25

### Fixed

- **Neutral wording.** The rule on placeholder numbers asks Zsolt to verify them by name instead of with a
  pronoun.

## 2026-10-24

### Added

- **This changelog.** The skill's history in one file, from its commits. `SKILL.md` keeps its short Changelog
  table.

### Changed

- **Changelog table removed from `SKILL.md`.** This file is now the skill's only history; every row of the
  table was already covered here.

## 2026-10-23

### Changed

- **Context file moved.** The skill reads the shared aidevme context from `.claude/agents/aidevme-context.md`
  instead of `.agents/aidevme-context.md`, now that the context is a read-only subagent. Nothing else in the
  skill changed. (8616be0)

## 2026-10-22

### Added

- **The skill itself**, from Zsolt's blog-optimization spec: the positioning line, the six-pillar menu with a
  Subscribe button, the old-category to pillar mapping and redirect candidates, the rules (categories are
  pillars and tags are products, one URL per topic, redirects before any slug change, never invent numbers), the
  homepage blueprint and visual direction, and four workflows: audit the live site, place a new or draft post,
  update the homepage or menu, and write the Start Here page. (df58183)
- **Every run saved as a new file** in `.research/aidevme-blog-optimization/<YYYY-MM-DD_HHmmss>_<workflow>.md`,
  so earlier audits and proposals are never overwritten. (df58183)
- **Evals:** seven cases that should trigger the skill (site audit, post placement, homepage redesign, category
  merge with redirects, Start Here page, an event on the homepage, an unverified subscriber number) and two that
  shouldn't (writing an article, a GA4 traffic question). (df58183)
