# Changelog

<!-- cspell:ignore aidevme Yoast evals Evals Dataverse frontmatter cheatsheet marketingskills crawlability -->
<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->

All notable changes to the **aidevme-seo-audit** skill: auditing the search performance of aidevme.com. Newest first. Each entry says what changed and why it
matters to you; the commit has the detail. The source is `agent-src/skills/project/aidevme-seo-audit/`, synced to
`.claude/skills/` and `.github/skills/`.

## 2026-10-27

### Added

- **MIT license:** a `LICENSE` file, so the skill keeps its license when it's shared on its own.

## 2026-10-24

### Added

- **This changelog.** The skill's history in one file, from its commits and the Changelog table that
  `SKILL.md` used to have.

## 2026-10-23

### Added

- **The skill itself**, written for aidevme.com with the marketingskills `seo-audit` method as inspiration: Yoast data
  from the REST API, a layered audit (crawlability, technical, on-page, content, authority), a per-post table, and
  striking-distance and low-CTR workflows. Local and international SEO are left out. (000770f)
- **Every audit saved** as a new file, `.audit/<YYYY-MM-DD_HHmmss>_seo-audit_<scope>.md`. (000770f)
- **Evals:** six cases that should trigger the skill and two that shouldn't. (000770f)

### Changed

- **Readability per post.** Full audits measure every post with the aidevme-readability script and add Readability,
  long-sentence and passive-voice columns to the per-post table; posts that aren't green go to
  aidevme-blog-writer. (1091707)
