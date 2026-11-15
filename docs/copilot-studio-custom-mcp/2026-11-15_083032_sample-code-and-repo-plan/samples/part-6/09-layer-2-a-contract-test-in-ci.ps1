<#
.SYNOPSIS
    Checks an MCP server's tools/list against the rules a Copilot Studio agent depends on.
.EXAMPLE
    ./Test-McpToolContract.ps1 -Endpoint http://localhost:5080/mcp
#>
param(
    [Parameter(Mandatory)] [string] $Endpoint,
    [int] $MinDescriptionLength = 40,
    # Inputs that must come from the caller's identity, never from the model.
    [string[]] $IdentityParameters = @('customerId', 'userId', 'email')
)

$ErrorActionPreference = 'Stop'
$headers = @{ Accept = 'application/json, text/event-stream' }
$body = @{ jsonrpc = '2.0'; id = 1; method = 'tools/list'; params = @{} } | ConvertTo-Json -Compress

$raw = Invoke-WebRequest -Uri $Endpoint -Method Post -Headers $headers -ContentType 'application/json' -Body $body
# Streamable HTTP can answer with plain JSON or with an SSE stream; take the JSON either way.
$json = if ($raw.Content -match '(?m)^data: (.+)$') { $Matches[1] } else { $raw.Content }
$tools = ($json | ConvertFrom-Json -Depth 50).result.tools

$failures = [System.Collections.Generic.List[string]]::new()
if (-not $tools) { $failures.Add('tools/list returned no tools') }

foreach ($tool in $tools) {
    $n = $tool.name
    if ($n -notmatch '^[A-Za-z0-9_.-]{1,128}$') { $failures.Add("${n}: name breaks the MCP naming rules") }
    if ([string]::IsNullOrWhiteSpace($tool.description)) {
        $failures.Add("${n}: tool has no description")
    } elseif ($tool.description.Length -lt $MinDescriptionLength) {
        $failures.Add("${n}: description is shorter than $MinDescriptionLength characters")
    }
    if (-not $tool.annotations -or $null -eq $tool.annotations.readOnlyHint) {
        $failures.Add("${n}: readOnlyHint isn't set")
    }

    $props = $tool.inputSchema.properties
    if ($props) {
        foreach ($p in $props.PSObject.Properties) {
            $name = "$n.$($p.Name)"
            $schema = $p.Value
            if ($IdentityParameters -contains $p.Name) { $failures.Add("${name}: identity must come from the caller, not a tool input") }
            if ([string]::IsNullOrWhiteSpace($schema.description)) { $failures.Add("${name}: parameter has no description") }
            if ($schema.type -is [array]) { $failures.Add("${name}: 'type' is an array; Copilot Studio truncates the schema") }
            if ($schema.PSObject.Properties.Name -contains '$ref') { $failures.Add("${name}: `$ref input; Copilot Studio filters the tool out") }
            if ($null -ne $schema.exclusiveMinimum -and $schema.exclusiveMinimum -isnot [bool]) {
                $failures.Add("${name}: integer exclusiveMinimum; Copilot Studio throws System.FormatException")
            }
        }
    }
}

"Checked $(@($tools).Count) tool(s) at $Endpoint"
if ($failures.Count -gt 0) {
    $failures | ForEach-Object { "FAIL  $_" }
    exit 1
}
'PASS  every tool and parameter has a description and a Copilot Studio-safe schema'
