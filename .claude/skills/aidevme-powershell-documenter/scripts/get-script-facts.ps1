#Requires -Version 7
# cspell:ignore aidevme Bruno usebruno
<#
.SYNOPSIS
    Lists the documentable facts of the PowerShell scripts in one scripts\<group> folder, as JSON.

.DESCRIPTION
    Parses each *.ps1 file directly in the folder (not tests\) with the PowerShell parser, without running it, and
    writes one JSON object per script: comment-based help, #Requires, [CmdletBinding()] settings, every parameter
    (type, mandatory, parameter sets, default, validation, the comment on its line), the Bruno requests it runs and
    their HTTP methods, the .bruno collections and repo paths it names, environment variables, external commands,
    Read-Host prompts, every throw with its line, and the matching tests\<name>.Tests.ps1 with its test names.

    The README is written from these facts plus a full read of each script; the facts are a checklist, so nothing
    a script does is left out and nothing is invented.

.EXAMPLE
    pwsh -File .claude/skills/aidevme-powershell-documenter/scripts/get-script-facts.ps1 -Path scripts/wordpress-scripts
    pwsh -File .claude/skills/aidevme-powershell-documenter/scripts/get-script-facts.ps1 -Path scripts/wordpress-scripts/get-draft-posts.ps1
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $Path,          # a scripts\<group> folder, or one script in it
    [string] $OutFile                               # default: write the JSON to the pipeline
)

$ErrorActionPreference = 'Stop'

$item = Get-Item -LiteralPath $Path
$folder = if ($item.PSIsContainer) { $item.FullName } else { $item.DirectoryName }
$scripts = if ($item.PSIsContainer) { @(Get-ChildItem -LiteralPath $folder -Filter *.ps1 -File | Sort-Object Name) } else { @($item) }
if (-not $scripts) { throw "No .ps1 files directly in $folder (tests\ is skipped)." }

# The repo root: the closest parent folder with a .git entry; Bruno requests are resolved under its .bruno folder.
$repoRoot = $folder
while ($repoRoot -and -not (Test-Path (Join-Path $repoRoot '.git'))) { $repoRoot = Split-Path -Parent $repoRoot }

function Get-ConstantText([System.Management.Automation.Language.Ast] $Ast) {
    if ($Ast -is [System.Management.Automation.Language.StringConstantExpressionAst]) { return $Ast.Value }
    if ($Ast -is [System.Management.Automation.Language.ExpandableStringExpressionAst]) { return $Ast.Value }
    return $null
}

$result = foreach ($file in $scripts) {
    $tokens = $null; $errors = $null
    $ast = [System.Management.Automation.Language.Parser]::ParseFile($file.FullName, [ref] $tokens, [ref] $errors)
    $text = Get-Content -LiteralPath $file.FullName -Raw

    # Comment-based help. Get-Help misses a help block glued to a #Requires line (no blank line between them), so
    # such a block is read here directly and reported with visibleToGetHelp = false.
    $help = $ast.GetHelpContent()
    $helpOut = if ($help) {
        [ordered]@{
            visibleToGetHelp = $true
            synopsis    = "$($help.Synopsis)".Trim()
            description = "$($help.Description)".Trim()
            examples    = @($help.Examples | ForEach-Object { "$_".Trim() })
            notes       = "$($help.Notes)".Trim()
            parameters  = $help.Parameters        # .PARAMETER blocks, keyed by upper-case name
        }
    }
    else {
        $block = $tokens | Where-Object { $_.Kind -eq 'Comment' -and $_.Text -match '^<#' -and $_.Text -match '(?m)^\s*\.SYNOPSIS' } |
            Select-Object -First 1
        if ($block) {
            $section = { param($k) @([regex]::Matches($block.Text, "(?ms)^\s*\.$k\b[^\r\n]*\r?\n(.*?)(?=^\s*\.[A-Z]+\b|#>)") |
                                     ForEach-Object { ($_.Groups[1].Value -replace '(?m)^ {4}', '').Trim() }) }
            [ordered]@{
                visibleToGetHelp = $false
                synopsis    = (& $section 'SYNOPSIS') -join "`n"
                description = (& $section 'DESCRIPTION') -join "`n"
                examples    = & $section 'EXAMPLE'
                notes       = (& $section 'NOTES') -join "`n"
                parameters  = [ordered]@{}
            }
        }
    }

    # [CmdletBinding()] on the script's param block
    $binding = [ordered]@{}
    $cb = $ast.ParamBlock.Attributes | Where-Object { $_.TypeName.Name -eq 'CmdletBinding' }
    foreach ($arg in @($cb.NamedArguments)) { if ($arg) { $binding[$arg.ArgumentName] = "$($arg.Argument.Extent.Text)".Trim("'", '"') } }

    # Parameters, with the comment that follows each one on the same line
    $parameters = foreach ($p in @($ast.ParamBlock.Parameters)) {
        if (-not $p) { continue }
        $sets = [System.Collections.Generic.List[string]]::new()
        $mandatory = $false
        $validation = [ordered]@{}
        $aliases = @()
        foreach ($attr in $p.Attributes) {
            if ($attr -isnot [System.Management.Automation.Language.AttributeAst]) { continue }
            switch ($attr.TypeName.Name) {
                'Parameter' {
                    foreach ($na in $attr.NamedArguments) {
                        if ($na.ArgumentName -eq 'Mandatory') { $mandatory = $na.ExpressionOmitted -or "$($na.Argument.Extent.Text)" -match 'true' }
                        if ($na.ArgumentName -eq 'ParameterSetName') { $sets.Add($na.Argument.SafeGetValue()) }
                    }
                }
                'Alias' { $aliases = @($attr.PositionalArguments | ForEach-Object { $_.SafeGetValue() }) }
                default {
                    if ($_ -like 'Validate*' -or $_ -like 'Allow*') {
                        $validation[$_] = @($attr.PositionalArguments | ForEach-Object { $_.Extent.Text.Trim("'", '"') })
                    }
                }
            }
        }
        $line = $p.Extent.EndLineNumber
        $comment = $tokens | Where-Object { $_.Kind -eq 'Comment' -and $_.Extent.StartLineNumber -eq $line -and $_.Extent.StartOffset -gt $p.Extent.EndOffset } |
            Select-Object -First 1
        [ordered]@{
            name          = $p.Name.VariablePath.UserPath
            type          = $p.StaticType.Name
            mandatory     = $mandatory
            parameterSets = @($sets)
            default       = if ($p.DefaultValue) { $p.DefaultValue.Extent.Text } else { $null }
            validation    = $validation
            aliases       = $aliases
            comment       = if ($comment) { $comment.Text.TrimStart('#').Trim() } else { $null }
            line          = $p.Extent.StartLineNumber
        }
    }

    # String constants: Bruno requests, collections and repo paths
    $strings = @($ast.FindAll({ param($n) $n -is [System.Management.Automation.Language.StringConstantExpressionAst] -or
                                           $n -is [System.Management.Automation.Language.ExpandableStringExpressionAst] }, $true) |
                 ForEach-Object { Get-ConstantText $_ } | Where-Object { $_ })
    $collections = @($strings | ForEach-Object { [regex]::Matches($_, '\.bruno[\\/][\w.-]+') | ForEach-Object Value } |
                     ForEach-Object { $_ -replace '/', '\' } | Sort-Object -Unique)
    $requests = foreach ($r in @($strings | Where-Object { $_ -match '^[\w.-]+/[\w./-]+\.yml$' } | Sort-Object -Unique)) {
        $method = $null; $foundIn = $null
        foreach ($c in $collections) {
            $candidate = Join-Path $repoRoot (Join-Path $c $r)
            if (Test-Path -LiteralPath $candidate) {
                $foundIn = $c
                $m = Select-String -LiteralPath $candidate -Pattern '^\s*method:\s*(\w+)' | Select-Object -First 1
                if ($m) { $method = $m.Matches[0].Groups[1].Value.ToUpperInvariant() }
                break
            }
        }
        [ordered]@{ request = $r; collection = $foundIn; method = $method }
    }
    $repoPaths = @($strings | ForEach-Object { [regex]::Matches($_, '(?:\.content|temp|\.research|\.audit)[\\/][\w.\\/<>-]*') | ForEach-Object Value } |
                   ForEach-Object { $_ -replace '/', '\' } | Sort-Object -Unique)

    # Environment variables: $env:X, Get/SetEnvironmentVariable('X'), and names in a foreach over string lists
    $envVars = @(
        [regex]::Matches($text, '\$env:(\w+)') | ForEach-Object { $_.Groups[1].Value }
        [regex]::Matches($text, 'EnvironmentVariable\(\s*[''"](\w+)[''"]') | ForEach-Object { $_.Groups[1].Value }
        [regex]::Matches($text, 'foreach\s*\(\s*\$\w+\s+in\s+((?:[''"][A-Z][A-Z0-9_]+[''"]\s*,?\s*)+)\)') |
            ForEach-Object { [regex]::Matches($_.Groups[1].Value, '[A-Z][A-Z0-9_]+') | ForEach-Object Value }
    ) | Sort-Object -Unique

    # Commands: functions defined in the script vs. what it calls
    $defined = @($ast.FindAll({ param($n) $n -is [System.Management.Automation.Language.FunctionDefinitionAst] }, $true) | ForEach-Object Name)
    $calls = @($ast.FindAll({ param($n) $n -is [System.Management.Automation.Language.CommandAst] }, $true) |
               ForEach-Object { $_.GetCommandName() } | Where-Object { $_ } | Sort-Object -Unique)
    $external = @($calls | Where-Object { $_ -notin $defined -and -not (Get-Command $_ -CommandType Cmdlet, Alias -ErrorAction SilentlyContinue) })

    # Every throw, with its message as written
    $throws = foreach ($t in $ast.FindAll({ param($n) $n -is [System.Management.Automation.Language.ThrowStatementAst] }, $true)) {
        [ordered]@{ line = $t.Extent.StartLineNumber; message = if ($t.Pipeline) { $t.Pipeline.Extent.Text } else { '(rethrow)' } }
    }

    # The matching tests
    $testFile = Join-Path $folder "tests\$($file.BaseName).Tests.ps1"
    $tests = if (Test-Path -LiteralPath $testFile) {
        $names = @([regex]::Matches((Get-Content -LiteralPath $testFile -Raw), '(?m)^\s*It\s+[''"]([^''"]+)[''"]') | ForEach-Object { $_.Groups[1].Value })
        [ordered]@{ file = "tests\$($file.BaseName).Tests.ps1"; count = $names.Count; names = $names }
    }

    [ordered]@{
        script          = $file.Name
        lines           = ($text -split "`n").Count
        parseErrors     = @($errors | ForEach-Object { "line $($_.Extent.StartLineNumber): $($_.Message)" })
        requires        = [ordered]@{
            version = if ($ast.ScriptRequirements.RequiredPSVersion) { "$($ast.ScriptRequirements.RequiredPSVersion)" } else { $null }
            modules = @($ast.ScriptRequirements.RequiredModules | ForEach-Object Name)
            admin   = [bool]$ast.ScriptRequirements.IsElevationRequired
        }
        help            = $helpOut
        cmdletBinding   = $binding
        parameters      = @($parameters)
        brunoRequests   = @($requests)
        collections     = $collections
        repoPaths       = $repoPaths
        envVars         = @($envVars)
        externalCommand = $external
        readHost        = [bool]($calls -contains 'Read-Host')
        throws          = @($throws)
        tests           = $tests
    }
}

$json = ConvertTo-Json -InputObject @($result) -Depth 8
if ($OutFile) { $json | Set-Content -LiteralPath $OutFile -Encoding utf8; Write-Host "Saved facts for $(@($result).Count) script(s) to $OutFile" }
else { $json }
