# Changelog

<!-- cspell:ignore aidevme evals Evals -->
<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->

All notable changes to the **aidevme-powershell-documenter** skill: the README.md of each `scripts/<group>/`
folder, written from the PowerShell scripts in it. Newest first. Each entry says what changed and why it matters to
you; the commit has the detail. The source is `agent-src/skills/project/aidevme-powershell-documenter/`, synced to
`.claude/skills/` and `.github/skills/`.

## 2026-11-05

### Added

- **Two workflows: update and check.** `update <script or folder>` creates or updates `scripts/<group>/README.md`
  from the code, changing only the sections a change touches and keeping notes people wrote; `check [folder]`
  lists what's missing or out of date and changes nothing.
- **Facts from the code, not from memory.** [scripts/get-script-facts.ps1](scripts/get-script-facts.ps1) parses
  each script without running it and lists its help, parameters (type, mandatory, parameter set, default,
  validation, inline comment), Bruno requests with their HTTP method, environment variables, repo paths, every
  `throw` and its tests. It also reads a help block that `Get-Help` can't see, and says so.
- **A coverage check.** [scripts/test-readme.ps1](scripts/test-readme.ps1) fails when a README misses a script, a
  parameter or a Bruno request, or links a script that no longer exists; `-Path scripts` checks every folder.
- **A reminder after every script edit.** [scripts/readme-hook.ps1](scripts/readme-hook.ps1) runs as a Claude
  Code `PostToolUse` hook (in `.claude/settings.json`) and, after Claude writes or edits a `.ps1` in
  `scripts/<group>/` (not in `tests/`), asks for the README update. Edits made outside Claude Code need **check**.
- **One README layout.** [references/readme-structure.md](references/readme-structure.md) sets the section order,
  the per-script section (parameters, output, behavior, stop table, examples), and where each fact comes from,
  taken from the wordpress-scripts and open-ai-scripts READMEs.
- **Evals.** Five cases in [evals/evals.json](evals/evals.json): three that trigger (update after a parameter
  change, a new folder, check all folders) and two that don't (Pester tests, a Bruno request).
