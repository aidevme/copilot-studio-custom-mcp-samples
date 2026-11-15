# Changelog

<!-- cspell:ignore aidevme evals Evals npx Pester JaCoCo NUnit PSScriptAnalyzer -->
<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->

All notable changes to the **aidevme-powershell-test** skill: Pester 6 unit tests for the PowerShell scripts in
`scripts/`. Newest first. Each entry says what changed and why it matters to you; the commit has the detail. The
source is `agent-src/skills/project/aidevme-powershell-test/`, synced to `.claude/skills/` and `.github/skills/`.

## 2026-11-04

### Added

- **The tests run in GitHub Actions.** `.github/workflows/powershell-tests.yml` runs `run-tests.ps1 -Coverage` on
  Windows for pushes and pull requests that change `scripts/`, `.bruno/` or this skill, writes the results to the
  run summary and uploads `temp/pester/`. The `run` section says how to keep a test CI-safe when it needs a
  gitignored file.
- **Tests that never reach aidevme.com.** [assets/tests/BrunoFake.ps1](assets/tests/BrunoFake.ps1) replaces `npx`
  with a function that records each Bruno call (request, `--env-var` values, folder) and writes the report a test
  asks for. `Mock npx` can't do this on Windows, because `npx` is npm's `npx.ps1`; any `npx` call a test didn't fake
  fails.
- **Four workflows: setup, new, run and refactor.** `setup` creates `scripts/tests/`, `new <script>` writes the tests
  for one script, `run` runs them, and `refactor` proposes moving the shared Bruno code into a module, only with
  your approval.
- **Templates for both kinds of script.** [assets/tests/Script.Tests.ps1](assets/tests/Script.Tests.ps1) covers a
  `get-*` script: field mapping, paging stop, the X-WP-Total check, HTTP and request errors, missing and masked
  reports, the `AIDEVME_WP_*` restore and scratch-folder cleanup.
  [assets/tests/sync-post-folders.Tests.ps1](assets/tests/sync-post-folders.Tests.ps1) covers the script that
  writes: folder matching, the `yes` prompt and `-Force`, already-in-folder skips and stopping at the first failed
  write.
- **A runner with a gate.** [scripts/run-tests.ps1](scripts/run-tests.ps1) refuses test files that use `Mock npx`
  or skip the fake, then runs Pester 6 with NUnit results and, with `-Coverage`, JaCoCo coverage in `temp/pester/`.
  `-Analyze` adds PSScriptAnalyzer when it's installed.
- **References.** [references/faking-bruno.md](references/faking-bruno.md) covers the `npx.ps1` trap, paged
  scripts and mocking `Test-Path` and `Read-Host` for `sync-post-folders.ps1`.
  [references/pester6.md](references/pester6.md) lists the Pester 6 changes that matter here and the runner's
  configuration.
- **Evals.** [evals/evals.json](evals/evals.json) has 9 prompts: 6 that should trigger the skill and 3 that belong
  to `aidevme-bruno`, `aidevme-docs-maintenance` or no PowerShell skill.

### Changed

- **The scripts and their tests live in `scripts/wordpress-scripts/`.** The tests are in
  `scripts/wordpress-scripts/tests/`. `run-tests.ps1` now finds `*.Tests.ps1` anywhere under `scripts/` and measures
  coverage on every `.ps1` there outside `tests` folders, so a later script group works without new parameters. The
  `sync-post-folders.ps1` example asks git for the repo root, so it finds `temp/post-folder-reports` at any folder
  depth.
