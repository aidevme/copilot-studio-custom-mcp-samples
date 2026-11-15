# Changelog

<!-- cspell:ignore aidevme Yoast yoastseo evals Evals Dataverse frontmatter cheatsheet marketingskills crawlability -->
<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->

All notable changes to the **aidevme-readability** skill: measuring and fixing the Yoast SEO readability checks for aidevme.com posts. Newest first. Each entry says what changed and why it
matters to you; the commit has the detail. The source is `agent-src/skills/project/aidevme-readability/`, synced to
`.claude/skills/` and `.github/skills/`.

## 2026-11-01

### Changed

- **Post folders moved:** the draft path in the usage notes is now
  `.content/wordpress-posts/<slug>/index.md`.
- **Shorter description:** cut to the 1,024-character limit of the Agent Skills specification, with every trigger
  phrase kept. The numeric limits of each check are now only in `SKILL.md`.

## 2026-10-30

### Changed

- **Evals follow the renamed article folder:** the test prompts now point to
  `.content/45-copilot-studio-agent-accounts-governance/`, so they find the article again.

## 2026-10-27

### Added

- **MIT license:** a `LICENSE` file, so the skill keeps its license when it's shared on its own.

## 2026-10-24

### Added

- **This changelog.** The skill's history in one file, from its commits and the Changelog table that
  `SKILL.md` used to have.

## 2026-10-23

### Added

- **The skill itself:** all nine checks of Yoast's readability analysis with their green, orange and red limits
  from the yoastseo 3.3.0 scoring spec, the stricter cornerstone limits and the overall penalty-point score. The
  limits that used to sit in aidevme-context and aidevme-blog-writer now live here. (1091707)
- **Readability script:** `scripts/readability.py` measures seven of the nine checks on a Markdown draft or a
  published post (through the WordPress REST API) and lists what each failing check flagged. Word complexity needs
  Yoast Premium's word list, so you read it in Yoast. (1091707)
- **Fix order and rewrite patterns** for passive voice, long sentences, subheadings, paragraphs, transition words
  and sentence beginnings, in [references/rewrite-patterns.md](references/rewrite-patterns.md). (1091707)
- **Evals:** four cases that should trigger the skill and two that shouldn't. (1091707)
