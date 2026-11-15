# Changelog

<!-- cspell:ignore aidevme Yoast evals Evals Dataverse frontmatter cheatsheet marketingskills crawlability -->
<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->

All notable changes to the **aidevme-blog-writer** skill: researching, outlining, writing and packaging aidevme.com articles as WordPress-ready Markdown. Newest first. Each entry says what changed and why it
matters to you; the commit has the detail. The source is `agent-src/skills/project/aidevme-blog-writer/`, synced to
`.claude/skills/` and `.github/skills/`.

## 2026-11-01

### Changed

- **Post folders moved:** articles, tables and images are now written to
  `.content/wordpress-posts/<slug>/`. The templates are now in `.content/templates/wordpress-post-template/`.

## 2026-10-27

### Added

- **MIT license:** a `LICENSE` file, so the skill keeps its license when it's shared on its own.

## 2026-10-24

### Added

- **This changelog.** The skill's history in one file, from its commits and the Changelog table that
  `SKILL.md` used to have.
- **Tables exported as WordPress table blocks.** `scripts/export_tables.py` writes each Markdown table of a draft to
  `.content/<slug>/tables/<NN>-<heading>.html` as a `<figure class="wp-block-table">` block; re-run it after every
  table edit. (24b501c)

### Changed

- **Images come from aidevme-image.** The Illustrate step hands the featured image and illustrations to the new
  skill, which writes the prompt, file name, alt text and description to
  `.content/<slug>/image-generation-prompts.md`. Diagrams still go to aidevme-diagram-mermaid. (ce5f088)

## 2026-10-23

### Added

- **Reference URLs asked for and researched first.** Before writing, the skill always asks for reference URLs;
  the new step 0 fetches every one, summarizes it and builds the article on it, following
  [references/research-and-verification.md](references/research-and-verification.md). One eval covers it.
  (8840bd9)

### Changed

- **Readability measured by aidevme-readability.** The clarity sweep runs its script and fixes the draft until every
  measured Yoast check is green, replacing "split sentences over ~35 words"; the final review reports the overall
  score. (1091707)
- **Context file moved** to `.claude/agents/aidevme-context.md`. (8616be0)

## 2026-10-22

### Added

- **The skill itself:** six post types modelled on published aidevme posts, a verification-first workflow with
  outline and final approval gates, WordPress REST frontmatter with a live taxonomy lookup, editing sweeps and an
  SEO and AI-search checklist. Drafts go to `.content/<slug>/`. (7ccdd6a)
- **Categories and tags by aidevme-blog-optimization's rules:** one primary category and at most one secondary,
  never "Power Platform" by default, 3–6 tags. (7ccdd6a)
- **Evals:** eight cases that should trigger the skill and two that shouldn't. (7ccdd6a)
