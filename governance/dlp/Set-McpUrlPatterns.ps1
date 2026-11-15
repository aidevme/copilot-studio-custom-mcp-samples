# dlp-mcp-url-patterns.ps1 - classify custom MCP connectors by host URL in a tenant-level policy.
# Module: Microsoft.PowerApps.Administration.PowerShell
param(
    [Parameter(Mandatory)] [string] $TenantId,
    [string] $PolicyDisplayName = "Contoso - Agents - Production"
)
Import-Module Microsoft.PowerApps.Administration.PowerShell
Add-PowerAppsAccount -Endpoint prod -TenantID $TenantId

# Find the policy GUID (PolicyName is the GUID, not the display name).
$policy = (Get-DlpPolicy).value | Where-Object { $_.displayName -eq $PolicyDisplayName }
if (-not $policy) { throw "Policy '$PolicyDisplayName' not found." }

# Show what is there before changing anything.
Get-PowerAppPolicyUrlPatterns -TenantId $TenantId -PolicyName $policy.name

# Confidential = Business, General = Non-business. The '*' rule is always last.
$UrlPatterns = @{
    rules = @(
        @{
            order                             = 1
            customConnectorRuleClassification = "Confidential"
            pattern                           = "https://mcp-prod.contoso.com*"
        },
        @{
            order                             = 2
            customConnectorRuleClassification = "Blocked"
            pattern                           = "*"
        }
    )
}
New-PowerAppPolicyUrlPatterns -TenantId $TenantId -PolicyName $policy.name -NewUrlPatterns $UrlPatterns
