# Faking the Bruno CLI in Pester tests

<!-- cspell:ignore aidevme npx Pester -->

Every script in `scripts/wordpress-scripts/` runs Bruno through `& npx @bruno run <request> --env Production [--env-var k=v] --reporter-json <file>`
and then reads the JSON report. A test replaces `npx` and writes the report itself. Checked with PowerShell 7.6.9,
Pester 6.2.0 and npm `npx.ps1` 11.13.0 on Windows (2026-11-04).

## Why not `Mock npx`

On Windows, npm installs `npx.ps1`, so `Get-Command npx` resolves to an **ExternalScript**. Pester 6.2.0's
`Mock npx` and `Mock npx.ps1` both leave it in place: the script under test runs the real Bruno CLI against
aidevme.com. Nothing in the test output says the mock didn't apply, apart from slow tests and real data.

A function wins over an external script in PowerShell's command lookup, so `BrunoFake.ps1` defines a global
`npx` function instead. `scripts/run-tests.ps1` rejects any test file that uses `Mock npx`.

## The helpers in `BrunoFake.ps1`

| Function | What it does |
| --- | --- |
| `Block-LiveNpx` | `npx` throws "Unfaked npx call in a test". Call it in `BeforeAll` and `AfterEach` |
| `Use-FakeBruno { param($Call) … }` | `npx` records the call in `$global:BrunoFakeCalls` and writes what the script block returns to the report path. Return nothing to simulate a missing report |
| `New-BrunoReport` | The report JSON: `-Status`, `-Data`, `-Total` (`x-wp-total`), `-TotalPages` (`x-wp-totalpages`), `-ErrorMessage` (`results[0].error`) |
| `Remove-BrunoFake` | Removes the function and the globals. Call it in `AfterAll`, so your shell's `npx` works again |

Each recorded call has:

| Property | Example |
| --- | --- |
| `Request` | `posts/004-list-all-published-posts.yml` |
| `EnvVars` | `@{ page = '2' }`, `@{ postId = '900001'; postFolderIds = '[5,1]' }` |
| `Report` | the `--reporter-json` path |
| `Location` | the folder Bruno ran in: the scratch copy for reads, `.bruno\aidevme-wordpress-admin` for writes |
| `Arguments` | every argument as a string |

## Scoping trap

Inside the global `npx` function, `$script:` refers to the global scope, not the test file. Share data between
the test and the fake through `$global:` variables (as the templates do), or through the `$Call` object.

## Paged scripts

`get-wordpress-media.ps1`, `get-wordpress-tags.ps1` and `get-wordpress-post-folders.ps1` loop over pages with
`--env-var page=N` (and, for folders, one request per taxonomy). Answer per page:

```powershell
Use-FakeBruno {
    param($Call)
    $page = [int]$Call.EnvVars.page
    New-BrunoReport -Data @(New-Fixture $page) -Total 2 -TotalPages 2
}
```

Then check that `$global:BrunoFakeCalls.Count` is the number of pages, and that duplicates or a short count fail
with the script's "X-WP-Total says" message. The "more than one page" test in `Script.Tests.ps1` applies only to
the scripts that read one page (posts, categories).

## `sync-post-folders.ps1`

- **The admin `.env`.** The script stops unless `.bruno\aidevme-wordpress-admin\.env` exists. Mock `Test-Path` for
  that path and pass every other call to the real cmdlet through a `CommandInfo`:

  ```powershell
  $realTestPath = Get-Command Test-Path -CommandType Cmdlet
  Mock Test-Path { $true } -ParameterFilter { "$Path" -like '*aidevme-wordpress-admin*.env' }
  Mock Test-Path { & $realTestPath @PesterBoundParameters }
  ```

  A default mock that calls `Microsoft.PowerShell.Management\Test-Path` recurses into the mock and fails with a
  call depth overflow. Never read, create or change the real `.env`.
- **The prompt.** `Mock Read-Host { 'yes' }` works (it's a cmdlet). Test that any other answer writes nothing, and
  that `-Force` doesn't ask.
- **Reports in the repo.** The script writes reports to `temp\post-folder-reports\<postId>.<step>.json` in the repo
  (gitignored). Use post IDs from 900001 up so they can't overwrite reports from real runs, and remove
  `9000*.json` in `AfterAll`.
- **What to assert.** The set call's `postFolderIds` keeps every current folder and adds the matched one; reads run
  in the scratch copy, writes in the admin collection; the first non-200 write throws and stops the loop.

## Environment variables

The `get-*` scripts clear `AIDEVME_WP_USER` and `AIDEVME_WP_APP_PASSWORD` for the Bruno run and restore them. To
test it, set a placeholder (`demo-user`), capture `$env:AIDEVME_WP_USER` inside the fake, and check it was empty
there and is back afterwards. Never use real values, and remove the variable in `finally`.
