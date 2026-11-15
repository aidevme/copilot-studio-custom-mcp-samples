# Changelog

<!-- cspell:ignore aidevme evals Evals Dataverse frontmatter cheatsheet marketingskills crawlability Substack substack repost -->
<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->

All notable changes to the **aidevme-social** skill: social content that promotes aidevme.com and its tools. Newest first. Each entry says what changed and why it
matters to you; the commit has the detail. The source is `agent-src/skills/project/aidevme-social/`, synced to
`.claude/skills/` and `.github/skills/`.

## 2026-11-01

### Changed

- **Post folders moved:** social drafts are now saved in `.content/wordpress-posts/<slug>/`.
  The templates are now in `.content/templates/wordpress-post-template/`.
- **Shorter description:** cut to the 1,024-character limit of the Agent Skills specification, with every trigger
  phrase kept. The explanations of Substack and Medium formats are now only in `SKILL.md`.

## 2026-10-30

### Changed

- **Evals follow the renamed article folder:** the test prompts now point to
  `.content/45-copilot-studio-agent-accounts-governance/`, so they find the article again.

## 2026-10-27

### Added

- **MIT license:** a `LICENSE` file, so the skill keeps its license when it's shared on its own.

## 2026-10-26

### Added

- **Medium stories.** New [references/medium.md](references/medium.md): Mode A cross-posts an aidevme.com article as
  a shorter, story-shaped version (900–1,600 words) imported with a canonical link to the original; Mode B writes a
  Medium-native story (1,200–2,200 words). It covers story shaping, Medium's formatting limits (two heading levels,
  no tables, gists for long code), the voice rules, the deliverables (titles, tags, publication suggestions,
  cross-post note, LinkedIn teaser, placeholder checklist) and a self-check. Drafts are saved as
  `.content/<slug>/medium-article.md` in the format of `.content/template/medium-article.md`; the launch schedule
  adds a day 3–7 Medium cross-post.

## 2026-10-25

### Added

- **Substack posts and Notes.** The skill now writes Substack posts: by default an adapted newsletter version of
  a blog post (400–900 words, three takeaways, one proof, a link to the full article), plus roundups,
  Substack-only pieces and, on request, a full repost with its search risk stated, because Substack has no
  canonical URL setting. Drafts are saved as `.content/<slug>/substack-post.md` in the format of
  `.content/template/substack-post.md`, with Notes at the end. Details in
  [references/substack.md](references/substack.md); limits in
  [references/platform-limits.md](references/platform-limits.md). Two new evals cover an adapted post and a
  full-repost request.

### Changed

- **Scope:** the skill no longer excludes newsletters in general; email sequences and newsletters other than
  Substack stay out.
- **Drafts saved as files, one template per platform.** Every draft goes next to the article as
  `.content/<slug>/<template>.md`, in the format of `.content/template/`: `linkedin-post.md` (hook within ~210
  characters, link in the first comment), `linkedin-article.md` (a newsletter edition, adapted like Substack),
  `twitter-x-post.md` (single post or thread, 280 characters each), `bluesky-post.md` (300 graphemes),
  `substack-post.md` and `facebook-post.md` (only once the Page is confirmed active).
- **LinkedIn newsletter in scope.** The skill writes LinkedIn articles for the "AI-powered Power Platform dev"
  newsletter; SEO title and description and the 1920 × 1080 cover image from LinkedIn Help are in
  [references/platform-limits.md](references/platform-limits.md), with approximate Facebook limits.

## 2026-10-24

### Added

- **This changelog.** The skill's history in one file, from its commits and the Changelog table that
  `SKILL.md` used to have.

## 2026-10-23

### Changed

- **Context file moved** to `.claude/agents/aidevme-context.md`. (8616be0)

## 2026-10-22

### Added

- **The skill itself**, adapted from marketingskills `social` v2.4.0 (`e85f3cb`) for aidevme.com and its developer
  audience: blog-post-first repurposing for LinkedIn, X, Bluesky, Reddit, Hacker News and short-form video, social
  listening with Playwright, and a performance loop through aidevme-google-analytics. Instagram, Facebook and
  Telegram depth was removed. (1ef1d7e)
- **Evals:** eight cases that should trigger the skill and two that shouldn't. (1ef1d7e)
