# Changelog

<!-- cspell:ignore aidevme evals Evals Dataverse frontmatter cheatsheet marketingskills crawlability -->
<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->

All notable changes to the **aidevme-image** skill: featured images and illustrations for aidevme.com posts. Newest first. Each entry says what changed and why it
matters to you; the commit has the detail. The source is `agent-src/skills/project/aidevme-image/`, synced to
`.claude/skills/` and `.github/skills/`.

## 2026-11-01

### Changed

- **Post folders moved:** prompts, images and GitHub URLs now use `.content/wordpress-posts/<slug>/`.
  The templates are now in `.content/templates/wordpress-post-template/`.
- **Shorter description:** cut to the 1,024-character limit of the Agent Skills specification, with every trigger
  phrase kept.

## 2026-10-30

### Changed

- **Evals follow the renamed article folder:** the test prompts now point to
  `.content/45-copilot-studio-agent-accounts-governance/`, so they find the article again.

## 2026-10-27

### Added

- **MIT license:** a `LICENSE` file, so the skill keeps its license when it's shared on its own.

## 2026-10-26

### Added

- **Media library audit.** New `scripts/audit_media.py` lists every file in the aidevme.com media library through
  the public REST API and checks whether each PNG, JPEG or GIF has a WebP or AVIF version with the same base file
  name, and whether WebP and AVIF files stay within the size budget (default 300 KB). It writes
  `media-inventory.csv` and an issue-ready `media-audit.md`. The new weekly `media-audit` workflow runs it and
  reports a `[Media audit]` issue. See "Media library audit" in `SKILL.md`.
- **More fields per image entry:** a one-sentence caption, a link to the entry's prompt section, the file's GitHub
  repo URL (on `main`; the repo is private, so it's a reference, not an image source) and an Azure Blob Storage URL
  built from a base URL defined once at the top of the prompts file. Prompts files also get a Contents list. The
  format is in `.content/template/image-generation-prompts.md`.

## 2026-10-24

### Added

- **This changelog.** The skill's history in one file, from its commits and the Changelog table that
  `SKILL.md` used to have.
- **The skill itself**, adapted from a generic marketing image skill: when to use an AI image, a diagram or a real
  screenshot; sizes per placement (featured image 1200 × 630, in-post, LinkedIn, GitHub); the aidevme palette;
  and a workflow from concept to prompt, alt text, description and a descriptive file name. (ce5f088)
- **A prompt file per post** in `.content/<slug>/image-generation-prompts.md`, in the format of
  `.content/template/image-generation-prompts.md`. Prompting patterns are in
  [references/prompting.md](references/prompting.md). (ce5f088)
- **Image check:** `scripts/check_image.py` checks format, dimensions, aspect ratio and file size for the
  placement (featured image budget 300 KB). (ce5f088)
- **Evals:** three cases that should trigger the skill and one that shouldn't. (ce5f088)
