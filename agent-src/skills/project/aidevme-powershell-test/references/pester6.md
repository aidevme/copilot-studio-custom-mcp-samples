# Pester 6: what matters for these tests

<!-- cspell:ignore aidevme Pester JaCoCo Cobertura NUnit -->

Pester 6.2.0 is the stable release on the PowerShell Gallery (2026-09-09). Windows also ships Pester 3.4.0, so
import 6.x explicitly; `scripts/run-tests.ps1` picks the newest installed 6.x or later. Install with
`Install-Module Pester -MinimumVersion 6.0.0 -Scope CurrentUser`.

Sources: [migrating from v5 to v6](https://pester.dev/docs/v6/migrations/v5-to-v6),
[mocking](https://pester.dev/docs/usage/mocking),
[importing tested functions](https://pester.dev/docs/usage/importing-tested-functions),
[PowerShell Gallery](https://www.powershellgallery.com/packages/Pester/6.2.0).

## Changes from Pester 5 that affect you

| Change | What to do |
| --- | --- |
| A call to a mocked command that matches no `-ParameterFilter` now **throws** (v5 ran the real command) | Add an unfiltered default `Mock`, as the `Test-Path` example in `faking-bruno.md` does |
| `Assert-MockCalled` and `Assert-VerifiableMock` were removed | `Should -Invoke`, `Should -InvokeVerifiable` |
| `Set-ItResult -Pending` was removed | `Set-ItResult -Skipped` or `-Inconclusive` |
| v4-style `Invoke-Pester -Script`, `-OutputFile`, `-CodeCoverage` were removed | `New-PesterConfiguration` and `Invoke-Pester -Configuration` |
| Only one of each `BeforeAll`, `BeforeEach`, `AfterEach`, `AfterAll` per block | Merge duplicates |
| Dot-prefixed folders are discovered (`.bruno`, `.content`) | Point `Run.Path` at `scripts` only (the runner's default) |
| Each file is discovered and run before the next | Don't rely on setup from another file; each file dot-sources `BrunoFake.ps1` |
| Empty `-ForEach` data throws | Use `-AllowNullOrEmptyForEach` when empty is legitimate |
| `<...>` in test names is evaluated | Don't put literal angle brackets in `It` names |
| Coverage uses the Profiler tracer; `CoverageGutters` output was removed | JaCoCo (the runner's choice) or Cobertura |
| Supports Windows PowerShell 5.1 and PowerShell 7.4+ | The scripts need 7 (`#Requires -Version 7`) |

New and optional: the `Should-*` assertions (`Should-Be`, `Should-Throw`, …) alongside `Should -Be`. The templates
use `Should -Be` because it works in 5 and 6. `Run.Parallel` and `Mock.Global` are experimental; don't use them.

## Patterns

- **Call the script, don't dot-source it.** The scripts have top-level code, so dot-sourcing runs them. Call
  `& $Sut -OutFile (Join-Path $TestDrive 'out.json')` inside `It`. Pester mocks defined in the test apply to
  cmdlets and functions the script calls (`Read-Host`, `Test-Path`), because a script runs in the caller's
  session state.
- **Always pass the output paths.** Without `-OutFile`, a `get-*` script overwrites the real file under
  `.content\`. Use `$TestDrive`, which Pester removes after the run.
- **Silence output with `*>$null`.** The scripts write progress with `Write-Host` (stream 6) and Bruno's output with
  `Out-Host`.
- **Assert on the thrown message.** The scripts' `throw` messages are specific ("X-WP-Total says", "HTTP 406"), so
  `Should -Throw '*X-WP-Total says 3*'` pins the behaviour.
- **Mock call counts** use `Should -Invoke <cmd> -Times n -Exactly`. In `It` the default scope is the test; in
  `Describe` or `BeforeAll` it's the whole block.
- **`$PesterBoundParameters`** holds the bound parameters inside a mock; `$PSBoundParameters` is overwritten.

## Configuration used by the runner

```powershell
$config = New-PesterConfiguration
$config.Run.Path                  = 'scripts'            # recursive: scripts/wordpress-scripts/tests/
$config.Run.PassThru              = $true
$config.Output.Verbosity          = 'Detailed'
$config.TestResult.Enabled        = $true
$config.TestResult.OutputFormat   = 'NUnitXml'
$config.TestResult.OutputPath     = 'temp/pester/test-results.xml'
$config.CodeCoverage.Enabled      = $true            # with -Coverage
$config.CodeCoverage.Path         = $sources             # every .ps1 under scripts/ outside tests folders
$config.CodeCoverage.OutputFormat = 'JaCoCo'
$config.CodeCoverage.OutputPath   = 'temp/pester/coverage.xml'
Invoke-Pester -Configuration $config
```

## Static analysis

PSScriptAnalyzer isn't installed on every machine; check with `Get-Module -ListAvailable PSScriptAnalyzer` each
time. Install with `Install-Module PSScriptAnalyzer -Scope CurrentUser`. The runner's `-Analyze` runs it on
the same scripts and fails only on `Error` findings. `[VERIFY: current PSScriptAnalyzer version and default rules
before adding it to CI]`
