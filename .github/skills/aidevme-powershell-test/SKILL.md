---
name: aidevme-powershell-test
metadata:
  layer: atomic
  scope: project
  version: 1.0.0
description: |
  Write, run and maintain Pester 6 unit tests for the PowerShell scripts in scripts/wordpress-scripts/ of the aidevme-blog repo
  (get-published-posts, get-wordpress-categories, -tags, -media, -post-folders, sync-post-folders), which call
  the Bruno CLI against aidevme.com. Tests replace npx with a fake that writes canned Bruno reports, so they never
  reach the site, and run-tests.ps1 gates every test file, runs Pester with NUnit results and JaCoCo coverage,
  and optionally PSScriptAnalyzer. Use when Zsolt asks to: set up Pester or the PowerShell tests; add or write
  tests for a script in scripts/; run the PowerShell tests or coverage; fix a failing Pester test; mock npx,
  Bruno, Read-Host or Test-Path in a test; or refactor a script so it's easier to test. Does NOT call or write to
  aidevme.com from a test, test Bruno collections or requests (use aidevme-bruno), test Python scripts, or change
  a script under test without approval.
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
argument-hint: "[setup | new <script> | run | refactor <script>]"
---

# aidevme-powershell-test

<!-- cspell:ignore aidevme npx Pester PSScriptAnalyzer JaCoCo NUnit Zsolt -->

Unit tests for the PowerShell scripts in `scripts/wordpress-scripts/`. Each script reads (or, for `sync-post-folders.ps1`, writes)
aidevme.com through the Bruno CLI, so the tests swap `npx` for a fake that writes the Bruno report a test needs:
an HTTP error, a second page, a masked value, a missing report. The tests run offline in seconds and need no
credentials.

## Where things live

| Path | What it is |
| --- | --- |
| `assets/tests/BrunoFake.ps1` (this skill) | The fake: `Block-LiveNpx`, `Use-FakeBruno`, `New-BrunoReport`, `Remove-BrunoFake` |
| `assets/tests/Script.Tests.ps1` | Template for a `get-*` script, written for `get-published-posts.ps1` (lines to change are marked `CHANGE`) |
| `assets/tests/sync-post-folders.Tests.ps1` | Worked example for the script that writes: prompt, `-Force`, matching, stop on failure |
| `scripts/run-tests.ps1` | Gate plus runner: run it from the repo root; finds tests anywhere under `scripts/` |
| `references/faking-bruno.md` | Why `Mock npx` fails, the fake's call object, paged scripts, `sync-post-folders.ps1` specifics |
| `references/pester6.md` | Pester 6 changes and patterns that matter here, the runner's configuration |
| `scripts/wordpress-scripts/tests/` (repo) | The working tests: `BrunoFake.ps1` and one `<script>.Tests.ps1` per script. A new script group gets its own `scripts/<group>/tests/` |
| `temp/pester/` (repo, gitignored) | `test-results.xml` (NUnit) and `coverage.xml` (JaCoCo) |

Needs PowerShell 7 and Pester 6.0.0 or later (`Get-Module -ListAvailable Pester`; Windows also ships 3.4.0).
Check each time; don't record it.

## Rules

1. **Never reach aidevme.com.** Every test file dot-sources `BrunoFake.ps1`, calls `Block-LiveNpx` in `BeforeAll`
   and `AfterEach`, `Use-FakeBruno` before running a script, and `Remove-BrunoFake` in `AfterAll`. Never use
   `Mock npx`: on Windows `npx` is npm's `npx.ps1`, and Pester leaves it in place, so the real Bruno CLI runs.
   `run-tests.ps1` refuses test files that break this rule. A test that hits the site is a bug, whatever it does.
2. **No credentials.** Tests never read, create or change a `.env` file and never use real values for
   `AIDEVME_WP_*`; use placeholders such as `demo-user` and remove them in `finally` (AGENTS.md section 8).
3. **Demo data only.** Fixtures use invented posts, slugs and `example.com` links: no client names or real record
   data (AGENTS.md section 6).
4. **Output goes to `$TestDrive`.** Always pass `-OutFile`, `-PostsFile` and `-FoldersFile`; a `get-*` script with
   no `-OutFile` overwrites the real JSON under `.content\`. `sync-post-folders.ps1` writes its reports to
   `temp\post-folder-reports`; tests use post IDs from 900001 up and remove `9000*.json` afterwards.
5. **Test behaviour, not implementation.** Assert the output file, the recorded Bruno calls (request, `--env-var`
   values, folder) and the thrown message. Don't assert on `Write-Host` text.
6. **The scripts are the spec.** If a test shows a script is wrong, report it; don't change the script to make a
   test pass without Zsolt's approval (see **refactor**).

## Workflows

### setup

1. Check Pester: `Get-Module -ListAvailable Pester`. Without 6.x, give Zsolt
   `Install-Module Pester -MinimumVersion 6.0.0 -Scope CurrentUser`; don't install it unasked.
2. Create `scripts/wordpress-scripts/tests/` (the `tests` folder next to the scripts) and copy `assets/tests/BrunoFake.ps1` into it. If a `BrunoFake.ps1` is already there,
   compare it with the asset and report the difference instead of overwriting it.
3. Add a first test file with **new** (`get-published-posts.ps1` is the simplest) and run **run**.
4. Confirm `temp/` is ignored: `git check-ignore -v temp/pester`.

### new `<script>`

1. Read the script: its `param()` block, the request(s) it runs, the fields it maps, every `throw`, and whether it
   pages (`--env-var page=`), prompts (`Read-Host`) or writes (`aidevme-wordpress-admin`).
2. Start from `assets/tests/Script.Tests.ps1` for a read script, or `assets/tests/sync-post-folders.Tests.ps1` for
   a write. Save it as `scripts/wordpress-scripts/tests/<script>.Tests.ps1`.
3. Change the lines marked `CHANGE`: script, request, fixture fields, the field list. For paged scripts, replace the
   "more than one page" test with per-page answers (`references/faking-bruno.md`, "Paged scripts").
4. Add one test per `throw` that matters, plus the happy path, the environment restore and the scratch-folder
   cleanup.
5. Run **run**. Every test must pass, and the gate must say `OK`.

### run

From the repo root:

| Goal | Command |
| --- | --- |
| All tests | `pwsh -File .claude/skills/aidevme-powershell-test/scripts/run-tests.ps1` |
| With coverage and analysis | add `-Coverage -Analyze` |
| Gate only (no Pester) | add `-GateOnly` |
| One file while writing it | add `-Path scripts/wordpress-scripts/tests/<script>.Tests.ps1` |

Read failures with `references/pester6.md`. Typical causes:

| Symptom | Cause |
| --- | --- |
| "Unfaked npx call" | the test runs a script before `Use-FakeBruno` |
| Slow tests and real post data in the output | `npx` wasn't faked (`Mock npx` or a missing `BrunoFake.ps1`); stop and fix it, because it reached the site |
| "call depth overflow" | a default mock calls the module-qualified cmdlet; use a `CommandInfo` (`references/faking-bruno.md`) |
| A `$script:` variable is empty inside the fake | the fake is global; use `$global:` or the `$Call` object |
| "Missing ...\.env" in `sync-post-folders.ps1` | the `Test-Path` mock for the admin `.env` is missing |

CI: `.github/workflows/powershell-tests.yml` runs `run-tests.ps1 -Coverage` on `windows-latest` with Pester 6.2.0
for pushes to `dev` and `main` and pull requests that change `scripts/`, `.bruno/` or this skill, and on demand
(Actions → PowerShell tests → Run workflow). The run summary lists the counts, failed tests and line coverage; the
artifact holds `temp/pester/`. The job has no secrets. When a new test needs a file that is gitignored (such as a
`.env`), mock it as the `Test-Path` example does, or the test passes locally and fails in CI.

### refactor `<script>` (only with approval)

The six scripts repeat the same scaffolding: the scratch copy of the collection, clearing and restoring
`AIDEVME_WP_*`, running `npx`, reading the report. Moving it into a module (for example `scripts/wordpress-scripts/AidevmeBruno.psm1`
with `Invoke-BrunoRequest`) would let tests use `Mock Invoke-BrunoRequest -ModuleName AidevmeBruno` and
`Should -Invoke`, and would allow a `-ReportDir` parameter for `sync-post-folders.ps1`.

1. Propose the change for one script, with the tests that will prove it behaves the same.
2. After Zsolt approves: write the tests against the current script first, so they pass before the change.
3. Change the script, run the same tests, and keep the script's documented behaviour and messages.

## Output

After a change: the files added or changed, the gate result, the Pester summary (passed, failed, skipped), the
coverage percentage when measured, any script bug a test found (reported, not fixed), and anything Zsolt has to do
(install Pester or PSScriptAnalyzer, commit).

## References

- `references/faking-bruno.md` and `references/pester6.md`
- Research behind this skill: `.research/2026-11-04_091739_powershell-script-unit-testing.md`
- The collections the scripts call: the **aidevme-bruno** skill
- [Pester docs](https://pester.dev/docs/quick-start)
