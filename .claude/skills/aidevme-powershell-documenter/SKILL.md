---
name: aidevme-powershell-documenter
metadata:
  layer: atomic
  scope: project
  version: 1.0.0
description: |
  Create or update the README.md of a scripts folder in the aidevme-blog repo (scripts/wordpress-scripts/,
  scripts/open-ai-scripts/, any new scripts/<group>/) with detailed technical documentation of every PowerShell
  script in it: purpose, requirements, credentials, how it works, every parameter, output format, stop conditions,
  examples, tests and troubleshooting. Facts come from the code: get-script-facts.ps1 parses each script without
  running it, and test-readme.ps1 checks the README names every script, parameter and Bruno request. A Claude Code
  hook asks for it after a script in scripts/ is written or edited. Use when Zsolt asks to: document a script or a
  scripts folder; create, update or refresh a scripts README; check whether a README is out of date; or after
  creating or changing a .ps1 file in scripts/<group>/. Does NOT change the scripts, write tests (use
  aidevme-powershell-test), document Bruno collections (aidevme-bruno), skills or Python scripts, or run a script
  that reaches aidevme.com or a paid API.
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
argument-hint: "[update <script or folder> | check [folder]]"
---

# aidevme-powershell-documenter

<!-- cspell:ignore aidevme npx Bruno Pester Zsolt markdownlint -->

Keeps `scripts/<group>/README.md` in step with the PowerShell scripts in that folder. The README is the full
technical reference for a reader who has never opened the scripts: what each one does, what it needs, every
parameter, what it writes, when it stops and why, how to run it, how it's tested and what to do when it fails.

## Where things live

| Path | What it is |
| --- | --- |
| `scripts/get-script-facts.ps1` (this skill) | Parses the scripts in a folder (or one script) without running them and prints JSON: help, `#Requires`, parameters with validation and inline comments, Bruno requests with their HTTP method, collections, repo paths, environment variables, external commands, `Read-Host`, every `throw`, and the matching tests |
| `scripts/test-readme.ps1` | Checks that a folder's README names every script, parameter (`-Name`) and Bruno request, and links no deleted script; exits 1 on gaps. `-Path scripts` checks every folder |
| `scripts/readme-hook.ps1` | The Claude Code `PostToolUse` hook (registered in `.claude/settings.json` for Write and Edit): after a `.ps1` directly in `scripts/<group>/` changes, it asks Claude to run this skill for that folder |
| `references/readme-structure.md` | The README layout: section order, the per-script section, tables, where each fact comes from, Markdown rules |
| `scripts/wordpress-scripts/README.md`, `scripts/open-ai-scripts/README.md` (repo) | The two worked examples: seven scripts, and one |

Run the scripts from the repo root, from the synced copy: `.claude/skills/aidevme-powershell-documenter/scripts/`.

## Rules

1. **The code is the source.** Every statement about a script comes from its code, its tests, the Bruno requests
   it runs, or Zsolt. When the comment-based help says something the code doesn't do, the README follows the code
   and the mismatch is reported. Facts about outside systems (API limits, site behavior, prices) need a checked
   source; otherwise mark them `[VERIFY: ...]` (AGENTS.md section 6).
2. **Never run a script to see what it does.** The scripts reach aidevme.com, write to it, or cost money. Read the
   code and the tests instead. Running `get-script-facts.ps1`, `test-readme.ps1` and the Pester tests is fine:
   none of them call the outside world.
3. **Edit only the README.** Never change a script, a test or a Bruno request while documenting. A bug, a
   misleading message or help that `Get-Help` can't see is reported to Zsolt, not fixed.
4. **Keep what people wrote.** Notes, warnings and history in the README (for example "on 2026-11-03 the modified
   dates moved") stay unless the code now contradicts them; say when you change or remove one.
5. **Demo data only.** Examples and JSON samples use invented slugs, IDs and `aidevme.com/demo-post/` links; no
   secrets, client names or real record data (AGENTS.md sections 6 and 8).
6. **Every parameter, every stop.** The parameter table lists every parameter in the facts, and the stop table
   every `throw` that a user can meet. `test-readme.ps1` checks the parameters; the throws are on you.

## Workflows

### update `<script or folder>` (default)

Use it when a script was created or changed (the hook asks for it), or when Zsolt asks to document a folder.
With no README yet, it creates one.

1. **Collect the facts.** From the repo root:

   ```powershell
   pwsh -File .claude/skills/aidevme-powershell-documenter/scripts/get-script-facts.ps1 -Path scripts/<group>
   ```

   Pass one script to look at it alone; pass the folder when the at-a-glance table or the shared sections may
   change.
2. **Read the sources in full**, not only the facts: each changed script, its `tests/<script>.Tests.ps1`, each
   Bruno request it runs (`.bruno/<collection>/<request>.yml`: method, URL, query, body, docs), and the current
   README. For a new script, also read the folder's other scripts to see what it shares with them.
3. **Work out what changed** between the code and the README: new or removed scripts, parameters, defaults,
   allowed values, requests, output fields, credentials, messages, tests. `git diff -- scripts/<group>/<script>`
   shows the latest change when the script is tracked.
4. **Write the README** in the layout of `references/readme-structure.md`, changing only the sections the
   change touches: the at-a-glance row, requirements and credentials, the shared "how it works" steps, the
   script's own section (parameters, output, behavior, stop table, examples), Typical order, Tests (counts and
   coverage table), Troubleshooting rows for new messages, Adding a script, Related. Keep the folder's existing
   style and wording where it's still right.
5. **Check it:**

   ```powershell
   pwsh -File .claude/skills/aidevme-powershell-documenter/scripts/test-readme.ps1 -Path scripts/<group>
   npx --yes markdownlint-cli2 scripts/<group>/README.md
   ```

   `test-readme.ps1` must say `README check: OK`. markdownlint must show no errors except MD013 (line length):
   the repo has no markdownlint config, so the 80-character default applies and every README exceeds it. Then
   read every number and name in the README against the facts once more.
6. **Report** (see Output).

### check `[folder]`

Read-only. Runs `test-readme.ps1` on one folder, or with `-Path scripts` on all of them, then compares each
script's facts with its README section (parameters, defaults, requests, messages, test counts) and lists what's
missing or out of date. Changes nothing; offer **update** for the folders with gaps.

## The hook

`.claude/settings.json` runs `readme-hook.ps1` after every Write and Edit. For a `.ps1` directly in
`scripts/<group>/` (not in `tests/`), it adds a note to the conversation asking for **update** on that script; for
any other file it does nothing. It never edits files and always exits 0.

- During a larger change (a script plus its tests and request), finish the change first and update the README once
  at the end, not after every edit.
- When Zsolt says not to touch the README, don't.
- The hook only sees edits Claude Code makes. Changes made in the editor, by Copilot or by `git pull` aren't seen:
  run **check** for those.

## Output

After **update**: the README sections added or changed (one line each), the `test-readme.ps1` and markdownlint
results, any `[VERIFY: ...]` left in, and the findings about the scripts themselves (help that contradicts the
code, help that `Get-Help` can't see, a misleading message, a parameter without a comment), each with its file and
line, reported, not fixed. After **check**: the gaps per folder, or "up to date".

## References

- `references/readme-structure.md`: the README layout and where each fact comes from
- The tests the README describes: the **aidevme-powershell-test** skill
- The Bruno collections the scripts run: the **aidevme-bruno** skill
- [About comment-based help](https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_comment_based_help)
