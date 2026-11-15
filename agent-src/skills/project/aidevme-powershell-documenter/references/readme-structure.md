# README structure for a scripts folder

<!-- cspell:ignore aidevme Bruno usebruno Pester JaCoCo NUnit markdownlint -->

The layout every `scripts/<group>/README.md` follows. It's taken from the two READMEs that already exist:
`scripts/wordpress-scripts/README.md` (seven scripts) and
`scripts/open-ai-scripts/README.md` (one script). When in doubt,
copy what they do.

## Contents

- [Section order](#section-order)
- [File header](#file-header)
- [Scripts at a glance](#scripts-at-a-glance)
- [Before you start](#before-you-start)
- [How the scripts work](#how-the-scripts-work)
- [One section per script](#one-section-per-script)
- [Tests, Troubleshooting, Adding a script, Related](#tests-troubleshooting-adding-a-script-related)
- [Where each fact comes from](#where-each-fact-comes-from)
- [Markdown rules](#markdown-rules)

## Section order

| # | Section | Required | Notes |
| --- | --- | --- | --- |
| 1 | Comment lines, `# <Folder title>`, intro | Yes | See [File header](#file-header) |
| 2 | `## Scripts at a glance` | Yes | One row per script |
| 3 | `## Before you start` with `### Requirements` and, when a script signs in or uses a key, `### Credentials` (or `### The API key`) | Yes | |
| 4 | `## How every script works` (several scripts) or `## How the script works` (one) | When the scripts share steps, or the one script has more than a few | Numbered steps, then `###` subsections for the non-obvious design decisions ("Why ...") |
| 5 | `## The scripts` with one `###` per script (several scripts), or `## <script>.ps1` (one script) | Yes | See [One section per script](#one-section-per-script) |
| 6 | `## Typical order` | When the scripts depend on each other's output | A numbered list or a code block in run order |
| 7 | `## Tests` | When a `tests/` folder exists | |
| 8 | `## Troubleshooting` | Yes | Message → cause → fix table |
| 9 | `## Adding a script` | Yes | Numbered steps |
| 10 | `## Related` | Yes | Links |

Sections a folder doesn't need are left out, not left empty.

## File header

```markdown
<!-- cspell:ignore <words cspell doesn't know: aidevme, npx, usebruno, product and field names> -->
<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->

# <Folder title, for example "WordPress scripts">

<What the scripts do, in two or three sentences: what they read or write, where the results go, and how they
call the outside world (Bruno CLI and the requests in `.bruno\<collection>\`).>

**<The one rule a reader must not miss, in bold: which scripts write to the live site or cost money, and what to
do before running them. Leave it out when every script is read-only and free.>**
```

The `MD024` line lets each script section repeat subheadings such as `#### Parameters`.

## Scripts at a glance

One table, one row per script, in alphabetical order or in the order they're run:

| Column | Content |
| --- | --- |
| Script | `[name.ps1](name.ps1)` |
| What it does | One phrase; add **(write)** or **(paid)** when it changes the live site or costs money |
| Bruno request | Each request it runs, in backticks; mark the collection when there are several (read, admin) |
| Credentials | `none`, `admin .env`, `OPENAI_API_KEY in .bruno\open-ai\.env`, ... |
| Writes | The output file(s) with their default path, or what it changes |

Under the table: where the requests live, and that tests are in `tests/`.

## Before you start

**Requirements:** a table with Requirement | Why | Check. The check is a command the reader can run
(`$PSVersionTable.PSVersion`, `npx --version`, `Test-Path ...`). Take the rows from the facts:

| Fact | Row |
| --- | --- |
| `requires.version` | PowerShell 7 (or the version) |
| `externalCommand` contains `npx` | Node.js with `npx`, and the Bruno CLI version the script pins (`@usebruno/cli@x.y.z`) |
| `collections` | The repo checked out, with the collection |
| An `.env` file the script tests for | The credentials file |
| `requires.modules` | Each module, with `Get-Module -ListAvailable <name>` |

Then one line on where to run the scripts from (the repo root) and a first example.

**Credentials:** where the values go (the gitignored `.env` file and its variable names, never values), how to
start from `.env.example`, how to check the file is ignored (`git check-ignore -v <path>`), that the script
never reads or prints the values, and the AGENTS.md section 8 warning about pasted secrets.

## How the scripts work

Numbered steps in the order the code runs them, each led by a bold phrase: preparation (scratch copy,
environment variables cleared and restored), the Bruno call (the full `npx` command line with its `--env-var`
options, in a code block), the report checks, the output, the cleanup in `finally`. Name what happens on failure.

Then a `###` per design decision a reader would otherwise question, each with the reason ("Why the scratch copy:
Bruno's masking", "Why the prompt goes in an environment variable", "Paging", "HTTP errors").

## One section per script

Several scripts: `### <name>.ps1` under `## The scripts`, with `####` subheadings. One script: `## <name>.ps1`
with `###` subheadings. Within the section, in this order:

1. **One paragraph:** what it does and anything unusual (signs in, writes, prompts, costs money). Add
   "(writes to the live site)" to the heading of a script that does.
2. **Parameters:** a table with every parameter from the facts, none left out:

   | Parameter | Required | Default | Values | Description |
   | --- | --- | --- | --- | --- |
   | `-OutFile` | No | `.content\...\x.json` | Path | Where to write the JSON |

   - **Required:** `Yes`, `No`, or "One of the two" for parameters in separate parameter sets (say so under
     the table).
   - **Default:** the literal default; when it's `$null` and the code fills it in later (`if (-not $OutFile)
     {...}`), the value the code uses; "Not sent (API default)" when leaving it out means the option isn't passed.
   - **Values:** the `ValidateSet` list, the `ValidateRange`, the `ValidatePattern` in words, `Switch`, `Path`.
   - **Description:** from the inline comment, the `.PARAMETER` help, and what the code does with it.
   - A folder whose scripts only have `-OutFile` can use the shorter Parameter | Default | Description table.
3. **Output:** the file and its shape. For JSON, list the fields in the order the code writes them
   (`[ordered]@{...}`), what each holds, and the sort order, then a JSON example with demo values
   (`demo-post`, `https://aidevme.com/demo-post/`, small IDs). For a file the script saves (an image), the
   format and how it's checked.
4. **Behavior details** the reader needs: paging, matching rules, prompts (`Read-Host`, what to type), what a
   write changes and what it leaves alone, side effects (a new modified date), reports it writes.
5. **Stops when:** a table of condition → message (shortened), one row per `throw` in the facts, in the order a
   run meets them. Group rows that share a cause. Mark which ones happen before any request is sent.
6. **Examples:** a `powershell` code block from the `.EXAMPLE` help plus one example per important parameter
   combination, with demo values and a comment line above each.

## Tests, Troubleshooting, Adding a script, Related

**Tests:** the test files (`tests/<script>.Tests.ps1`, with the count of `It` blocks from the facts), how they
fake the outside world (`BrunoFake.ps1`: no request reaches the site or the paid API; `.env` files are mocked,
never read), a table of what they cover (grouped from the test names), the commands to run them through
`.claude/skills/aidevme-powershell-test/scripts/run-tests.ps1`, where results go (`temp\pester\`), the
PowerShell tests (`.github/workflows/powershell-tests.yml`) workflow, and the note that `Mock npx`
doesn't work on Windows.

**Troubleshooting:** a table Message or symptom | Cause | Fix. One row for each message a user will see in
practice (the `throw` messages, HTTP statuses, Bruno errors), plus symptoms that have no message (a slow test run
that reached the real API).

**Adding a script:** numbered steps: add the request to the collection (and its check), start from the closest
existing script (name which one for which kind), keep the shared safety code, write tests with
**aidevme-powershell-test**, add it to this README.

**Related:** AGENTS.md sections that apply (6 content, 7 live site, 8 credentials), the collections, the skills
that own neighboring work (**aidevme-bruno**, **aidevme-powershell-test**, **aidevme-image** ...), research notes
behind the scripts, and official docs (Bruno CLI, the API reference).

## Where each fact comes from

| README content | Source, in this order |
| --- | --- |
| What a script does | The code, then its `.SYNOPSIS`/`.DESCRIPTION` help (the help can be out of date: the code wins, and the mismatch is reported) |
| Parameters, defaults, allowed values | `get-script-facts.ps1` `parameters`, then the code that uses each one |
| Requests and their HTTP methods | `brunoRequests` (method read from the request YAML); the request file itself for URL, query parameters and body |
| Output fields | The `[ordered]@{...}` or object the code writes |
| Stop conditions and messages | `throws`, quoted from the code |
| Environment variables and files | `envVars`, `collections`, `repoPaths`, and the `Test-Path` checks in the code |
| Test coverage | `tests.names` and the test file |
| Anything else (API limits, site behavior, prices) | A checked source or Zsolt; otherwise `[VERIFY: ...]` |

## Markdown rules

- Write in the repo's style (`.templates/WRITING_STYLE.md`): short sentences, active voice, tables for
  reference material, code in backticks, Windows paths with `\` in prose and commands (the scripts run on
  Windows), forward slashes in links.
- Lines up to about 120 characters; tables can run longer.
- One blockquote per note: two notes in a row trip MD028 (a blank line inside a blockquote); merge them.
- Relative links only, from the README's folder: `[name.ps1](name.ps1)`, `[tests/](tests/)`,
  `../../AGENTS.md`, `../../.bruno/<collection>/`.
- Add every word cspell doesn't know to the `cspell:ignore` line at the top.
- No real secrets, client names or record data; demo values only (AGENTS.md sections 6 and 8).
