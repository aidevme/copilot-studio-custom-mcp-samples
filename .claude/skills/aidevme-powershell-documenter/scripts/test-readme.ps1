#Requires -Version 7
# cspell:ignore aidevme Bruno

<#
.SYNOPSIS
    Checks that a scripts\<group>\README.md covers every script in its folder, as get-script-facts.ps1 sees them.

.DESCRIPTION
    For each folder given (or every folder under scripts\ with -Path scripts), checks that README.md exists and
    names every *.ps1 directly in the folder, every parameter of each script (as -Name), and every Bruno request
    the scripts run. Also lists scripts the README links to ([name.ps1](name.ps1)) that no longer exist.

    It checks coverage, not quality: a passing README can still be wrong, so read it against the scripts too.
    Prints "README check: OK" or the gaps, and exits with 1 when there are gaps.

.EXAMPLE
    pwsh -File .claude/skills/aidevme-powershell-documenter/scripts/test-readme.ps1 -Path scripts/wordpress-scripts
    pwsh -File .claude/skills/aidevme-powershell-documenter/scripts/test-readme.ps1 -Path scripts
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $Path           # a scripts\<group> folder, or scripts\ for all of them
)

$ErrorActionPreference = 'Stop'

$root = (Get-Item -LiteralPath $Path).FullName
$folders = if (Get-ChildItem -LiteralPath $root -Filter *.ps1 -File) { @($root) }
           else { @(Get-ChildItem -LiteralPath $root -Directory | Where-Object { Get-ChildItem -LiteralPath $_.FullName -Filter *.ps1 -File } | ForEach-Object FullName) }
if (-not $folders) { throw "No folder with .ps1 files found under $root." }

$facts = Join-Path $PSScriptRoot 'get-script-facts.ps1'
$gaps = [System.Collections.Generic.List[string]]::new()

foreach ($folder in $folders) {
    $name = Split-Path -Leaf $folder
    $readmePath = Join-Path $folder 'README.md'
    if (-not (Test-Path -LiteralPath $readmePath)) { $gaps.Add("${name}: no README.md"); continue }
    $readme = Get-Content -LiteralPath $readmePath -Raw
    if (-not $readme.Trim()) { $gaps.Add("${name}: README.md is empty"); continue }

    foreach ($s in @(& $facts -Path $folder | ConvertFrom-Json)) {
        if ($readme -notmatch [regex]::Escape($s.script)) { $gaps.Add("${name}: $($s.script) is not in the README"); continue }
        foreach ($p in $s.parameters) {
            if ($readme -notmatch "-$([regex]::Escape($p.name))\b") { $gaps.Add("${name}: $($s.script) parameter -$($p.name) is not in the README") }
        }
        foreach ($r in $s.brunoRequests) {
            if ($readme -notmatch [regex]::Escape($r.request)) { $gaps.Add("${name}: $($s.script) request $($r.request) is not in the README") }
        }
    }

    foreach ($m in [regex]::Matches($readme, '\]\(([\w.-]+\.ps1)\)')) {
        if (-not (Test-Path -LiteralPath (Join-Path $folder $m.Groups[1].Value))) { $gaps.Add("${name}: the README links $($m.Groups[1].Value), which doesn't exist") }
    }
}

if ($gaps.Count) {
    Write-Host "README check: $($gaps.Count) gap(s)" -ForegroundColor Yellow
    $gaps | ForEach-Object { Write-Host "  - $_" }
    exit 1
}
Write-Host "README check: OK ($($folders.Count) folder(s))" -ForegroundColor Green
