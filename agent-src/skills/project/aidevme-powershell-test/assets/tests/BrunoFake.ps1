# Fakes the Bruno CLI (npx) for Pester tests of the scripts in scripts/. Dot-source it in BeforeAll.
# Pester's Mock can't replace npx on Windows (it resolves to npm's npx.ps1), so these helpers shadow it with a
# global function instead. Every test file must call Block-LiveNpx in BeforeAll and Remove-BrunoFake in AfterAll.

function New-BrunoReport {
    [CmdletBinding()]
    param(
        [int]      $Status = 200,
        [object[]] $Data = @(),
        [int]      $Total = -1,                     # x-wp-total; default: the number of items in -Data
        [int]      $TotalPages = 1,                 # x-wp-totalpages
        [string]   $ErrorMessage                    # sets results[0].error, as when Bruno can't reach the site
    )
    if ($Total -lt 0) { $Total = $Data.Count }
    $result = [ordered]@{
        response = [ordered]@{
            status  = $Status
            headers = [ordered]@{ 'x-wp-total' = "$Total"; 'x-wp-totalpages' = "$TotalPages" }
            data    = $Data
        }
    }
    if ($ErrorMessage) { $result.error = $ErrorMessage }
    ConvertTo-Json -Depth 20 -InputObject @([ordered]@{ results = @($result) })
}

function Use-FakeBruno {
    [CmdletBinding()]
    param(
        # Gets one call object (Request, EnvVars, Report, Location, Arguments) and returns the report JSON
        # (New-BrunoReport) or nothing, in which case no report is written.
        [Parameter(Mandatory)] [scriptblock] $Responder
    )
    $global:BrunoFakeCalls     = [System.Collections.Generic.List[object]]::new()
    $global:BrunoFakeResponder = $Responder
    Set-Item function:global:npx -Value {
        $a = @($args | ForEach-Object { "$_" })
        $envVars = @{}
        for ($i = 0; $i -lt $a.Count; $i++) {
            if ($a[$i] -eq '--env-var' -and $i + 1 -lt $a.Count) {
                $k, $v = $a[$i + 1] -split '=', 2
                $envVars[$k] = $v
            }
        }
        $run    = [array]::IndexOf($a, 'run')
        $report = [array]::IndexOf($a, '--reporter-json')
        $call = [pscustomobject]@{
            Request   = if ($run -ge 0 -and $run + 1 -lt $a.Count) { $a[$run + 1] } else { $null }
            EnvVars   = $envVars
            Report    = if ($report -ge 0 -and $report + 1 -lt $a.Count) { $a[$report + 1] } else { $null }
            Location  = (Get-Location).Path
            Arguments = $a
        }
        $global:BrunoFakeCalls.Add($call)
        $json = & $global:BrunoFakeResponder $call
        if ($null -ne $json -and $call.Report) { Set-Content -LiteralPath $call.Report -Value $json -Encoding utf8 }
    }
}

function Block-LiveNpx {
    # The safety net: any npx call that no test faked fails instead of reaching aidevme.com.
    Set-Item function:global:npx -Value {
        throw "Unfaked npx call in a test: npx $args. Call Use-FakeBruno first; tests must never reach aidevme.com."
    }
}

function Remove-BrunoFake {
    Remove-Item function:global:npx -ErrorAction SilentlyContinue
    Remove-Variable BrunoFakeCalls, BrunoFakeResponder -Scope Global -ErrorAction SilentlyContinue
}
