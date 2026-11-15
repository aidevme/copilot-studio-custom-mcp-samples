#Requires -Version 7
<#
.SYNOPSIS
    Checks and runs the Pester 6 tests for the PowerShell scripts in scripts\, without reaching aidevme.com.

.DESCRIPTION
    Run from the repository root. Tests are found anywhere under -Path (default scripts\, so
    scripts\wordpress-scripts\tests\ and any later script group are included); coverage and analysis cover every
    .ps1 under -CoveragePath except files in a tests folder.

    1. Gate: every *.Tests.ps1 under -Path must dot-source BrunoFake.ps1, call Block-LiveNpx and Remove-BrunoFake,
       and must not use "Mock npx" (it doesn't replace npm's npx.ps1 on Windows, so the real Bruno CLI would run).
       Any failure stops the run before a test starts.
    2. Safety net: shadows npx with a function that throws for the whole run, then removes it.
    3. Runs Pester 6 (the newest installed 6.x or later) with NUnit results in -OutDir, and JaCoCo coverage of
       -CoveragePath with -Coverage.
    4. With -Analyze, runs PSScriptAnalyzer on -CoveragePath when it's installed (warns otherwise).

    Exits 1 when the gate, a test or (with -Analyze) an analyzer error fails.

.EXAMPLE
    pwsh -File .claude/skills/aidevme-powershell-test/scripts/run-tests.ps1
    pwsh -File .claude/skills/aidevme-powershell-test/scripts/run-tests.ps1 -Coverage -Analyze
    pwsh -File .claude/skills/aidevme-powershell-test/scripts/run-tests.ps1 -GateOnly
#>
[CmdletBinding()]
param(
    [string] $Path         = 'scripts',             # searched recursively for *.Tests.ps1
    [string] $CoveragePath = 'scripts',             # every .ps1 below it, except tests folders
    [string] $OutDir       = 'temp/pester',          # gitignored
    [switch] $Coverage,
    [switch] $Analyze,
    [switch] $GateOnly
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $Path)) { throw "No tests at $Path. Run the skill's setup workflow first." }
$files = @(Get-ChildItem $Path -Recurse -Filter '*.Tests.ps1' -File)
if ($files.Count -eq 0) { throw "No *.Tests.ps1 files under $Path." }

# Step 1: gate.
$problems = [System.Collections.Generic.List[string]]::new()
foreach ($f in $files) {
    $text = Get-Content $f.FullName -Raw
    if ($text -match '\bMock\s+(-CommandName\s+)?[''"]?npx\b') { $problems.Add("$($f.Name): uses Mock npx, which doesn't replace npx.ps1. Use Use-FakeBruno.") }
    foreach ($needed in 'BrunoFake.ps1', 'Block-LiveNpx', 'Remove-BrunoFake') {
        if (-not $text.Contains($needed)) { $problems.Add("$($f.Name): missing $needed (see assets/tests/Script.Tests.ps1).") }
    }
}
if ($problems.Count -gt 0) {
    $problems | ForEach-Object { Write-Host "GATE: $_" -ForegroundColor Red }
    exit 1
}
Write-Host "Gate: OK ($($files.Count) test file(s))" -ForegroundColor Green
if ($GateOnly) { return }

# The scripts under test, for coverage and analysis.
$sources = @(Get-ChildItem $CoveragePath -Recurse -File -Filter '*.ps1' |
    Where-Object { $_.Name -notlike '*.Tests.ps1' -and $_.FullName -notmatch '[\\/]tests[\\/]' } |
    ForEach-Object FullName)

# Step 3 needs Pester 6.
$pester = Get-Module -ListAvailable Pester | Where-Object Version -ge ([version]'6.0.0') | Sort-Object Version -Descending | Select-Object -First 1
if (-not $pester) { throw "Pester 6 isn't installed. Run: Install-Module Pester -MinimumVersion 6.0.0 -Scope CurrentUser" }
Import-Module $pester.Path -Force
Write-Host "Pester $($pester.Version)" -ForegroundColor Cyan

New-Item -ItemType Directory -Path $OutDir -Force | Out-Null
$outFull = (Resolve-Path $OutDir).Path

# Step 2: safety net for the whole run.
Set-Item function:global:npx -Value { throw "Unfaked npx call during the test run: npx $args" }
try {
    $config = New-PesterConfiguration
    $config.Run.Path               = $Path
    $config.Run.PassThru           = $true
    $config.Output.Verbosity       = 'Detailed'
    $config.TestResult.Enabled     = $true
    $config.TestResult.OutputFormat = 'NUnitXml'
    $config.TestResult.OutputPath  = Join-Path $outFull 'test-results.xml'
    if ($Coverage) {
        $config.CodeCoverage.Enabled      = $true
        $config.CodeCoverage.Path         = $sources
        $config.CodeCoverage.OutputFormat = 'JaCoCo'
        $config.CodeCoverage.OutputPath   = Join-Path $outFull 'coverage.xml'
    }
    $result = Invoke-Pester -Configuration $config
}
finally {
    Remove-Item function:global:npx -ErrorAction SilentlyContinue
}

$failed = $result.Result -ne 'Passed'
Write-Host ("Tests: {0} passed, {1} failed, {2} skipped. Results: {3}" -f $result.PassedCount, $result.FailedCount, $result.SkippedCount, $config.TestResult.OutputPath.Value) -ForegroundColor $(if ($failed) { 'Red' } else { 'Green' })
if ($Coverage -and $result.CodeCoverage) {
    Write-Host ("Coverage: {0:N1}% of {1} commands. Report: {2}" -f $result.CodeCoverage.CoveragePercent, $result.CodeCoverage.CommandsAnalyzedCount, $config.CodeCoverage.OutputPath.Value) -ForegroundColor Cyan
}

# Step 4: static analysis.
if ($Analyze) {
    if (Get-Module -ListAvailable PSScriptAnalyzer) {
        $findings = @($sources | ForEach-Object { Invoke-ScriptAnalyzer -Path $_ })
        $findings | Format-Table Severity, RuleName, ScriptName, Line, Message -AutoSize -Wrap | Out-Host
        if (@($findings | Where-Object Severity -eq 'Error').Count -gt 0) { $failed = $true }
        Write-Host "PSScriptAnalyzer: $($findings.Count) finding(s)" -ForegroundColor Cyan
    }
    else { Write-Warning 'PSScriptAnalyzer is not installed; skipped. Install-Module PSScriptAnalyzer -Scope CurrentUser' }
}

if ($failed) { exit 1 }
