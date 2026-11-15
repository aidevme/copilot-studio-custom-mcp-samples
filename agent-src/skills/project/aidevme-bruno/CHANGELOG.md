# Changelog

<!-- cspell:ignore aidevme evals Evals opencollection Yoast Zsolt -->
<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->

All notable changes to the **aidevme-bruno** skill: the read-only Bruno collection for the aidevme.com WordPress
REST API. Newest first. Each entry says what changed and why it matters to you; the commit has the detail. The
source is `agent-src/skills/project/aidevme-bruno/`, synced to `.claude/skills/` and `.github/skills/`.

## 2026-11-04

### Changed

- **"List recent media" returns every public media field.** The request in
  [assets/collection/media/001-list-media.yml](assets/collection/media/001-list-media.yml) now asks for all 24 fields
  of the WordPress media schema's view context, plus `featured_media`, `filename`, `filesize` and the fields the
  site's plugins add (`wf_attachment_folders`, `acf`, `jetpack_sharing_enabled`, `jetpack_likes_enabled`,
  `class_list`), and checks that `_links` is left out. Edit-only fields still need credentials and aren't included.

## 2026-11-01

### Changed

- **License field reads `MIT`:** the validator only accepts the plain identifier, so the "(see LICENSE)" note is
  gone. The `LICENSE` file is unchanged.

## 2026-10-30

### Fixed

- **Bruno reports no longer hide `aidevme`:** when `AIDEVME_WP_USER` is set, Bruno CLI 4.3.0 writes `********` for
  that value everywhere in its JSON report, including URLs and tag names. The console shows nothing wrong.
  `bruno-media.yml` no longer passes the two credentials, and `SKILL.md` says how to get a clean report locally.

## 2026-10-29

### Added

- **Media list in GitHub Actions:** `.github/workflows/bruno-media.yml` runs **Media / List recent media** with
  the Bruno CLI on demand. The run summary lists the 20 newest items with dimensions and file sizes; the JSON and
  HTML reports are a run artifact, with the `Authorization` header left out.

### Changed

- **List recent media returns file sizes:** the request now asks for `media_details` (width, height, `filesize`
  in bytes, generated sizes). WordPress ignores nested `_fields` such as `media_details.filesize`, so the whole
  object is requested.

## 2026-10-27

### Added

- **The skill itself:** set up, extend, test and run a Bruno collection for the aidevme.com WordPress REST API
  in OpenCollection YAML, under `.bruno/aidevme-wordpress/`. Four workflows: setup, add an endpoint, write tests,
  run with the Bruno CLI. Read-only by rule: GET only, no credentials in files or chat.
- **The starting collection** in `assets/collection/`: 9 GET requests in 6 folders (API index; recent posts,
  post by slug with Yoast SEO data, search; pages; categories and tags; recent media; drafts with an application
  password), a Production environment, a browser User-Agent for every request (the site firewall answers 406 to
  short ones) and `.env.example`. Every request has a status assertion and shape tests; `smoke` and `auth` tags
  select quick and credentialed runs. Parsed and run with Bruno CLI 4.3.0.
- **`scripts/check_collection.py`:** fails on any method but GET or HEAD, a URL outside `{{baseUrl}}`, a request
  without a status check, a literal credential, a missing browser User-Agent or a duplicate `seq`.
- **References:** `opencollection-format.md` (collection, folder, environment and request formats, script API,
  CLI, with sources) and `wp-rest-endpoints.md` (read endpoints, parameters, pagination headers, error codes).
- **Evals:** 5 cases (4 should trigger, 1 should not): setup, adding a request, refusing a write request and a
  pasted password, a 406 diagnosis, and a Dataverse collection that belongs elsewhere.
- **MIT license:** a `LICENSE` file and a `license` field in the frontmatter, so the skill keeps its license when it's
  shared on its own.
