# Changelog

<!-- cspell:ignore aidevme evals Evals Dataverse frontmatter cheatsheet marketingskills crawlability -->
<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->

All notable changes to the **aidevme-google-analytics** skill: GA4 analysis of aidevme.com through Google's read-only analytics-mcp server. Newest first. Each entry says what changed and why it
matters to you; the commit has the detail. The source is `agent-src/skills/project/aidevme-google-analytics/`, synced to
`.claude/skills/` and `.github/skills/`.

## 2026-10-27

### Added

- **MIT license:** a `LICENSE` file, so the skill keeps its license when it's shared on its own.

## 2026-10-24

### Added

- **This changelog.** The skill's history in one file, from its commits and the Changelog table that
  `SKILL.md` used to have.

## 2026-10-22

### Added

- **The skill itself**, built on analytics-mcp v0.7.0 (`25cf926`): property resolution by name, a preflight for
  missing tools and auth errors, request defaults (last 28 days against the previous 28), findings-first answers
  with caveats, mapping GA4 page paths to posts, and error recovery. It never reports a number that didn't come
  from a tool call. (92f9494)
- **The analytics-mcp server registered** in the project `.mcp.json`. Credentials come only from your local
  environment variables; setup is in [references/setup.md](references/setup.md). (92f9494)
- **References** for the GA4 schema, report recipes, funnel patterns and gotchas, in `references/`. (92f9494)
- **Evals:** eight cases that should trigger the skill and two that shouldn't. (92f9494)
