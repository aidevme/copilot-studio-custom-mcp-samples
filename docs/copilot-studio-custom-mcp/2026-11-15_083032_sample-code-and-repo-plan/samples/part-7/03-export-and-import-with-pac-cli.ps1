# deploy-mcp-solutions.ps1 - promote the MCP connector and the agent from Dev to Test.
# Requires Power Platform CLI (pac). Sign in first: pac auth create
param(
    [string] $SourceEnv = "https://contoso-dev.crm4.dynamics.com",
    [string] $TargetEnv = "https://contoso-test.crm4.dynamics.com",
    [string] $Stage     = "test"
)
$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path .\out, .\settings | Out-Null

# 1. Export both solutions as managed from Dev.
pac solution export --name ContosoOrderMcpConnector --environment $SourceEnv `
    --path .\out\ContosoOrderMcpConnector_managed.zip --managed --overwrite
pac solution export --name ContosoCustomerServiceAgent --environment $SourceEnv `
    --path .\out\ContosoCustomerServiceAgent_managed.zip --managed --overwrite

# 2. Generate settings templates once; commit the filled-in files per stage.
if (-not (Test-Path ".\settings\connector.$Stage.json")) {
    pac solution create-settings --solution-zip .\out\ContosoOrderMcpConnector_managed.zip `
        --settings-file ".\settings\connector.$Stage.json"
}
if (-not (Test-Path ".\settings\agent.$Stage.json")) {
    pac solution create-settings --solution-zip .\out\ContosoCustomerServiceAgent_managed.zip `
        --settings-file ".\settings\agent.$Stage.json"
}

# 3. Import the connector solution first: the custom connector must exist
#    before the connection reference that points at it.
pac solution import --environment $TargetEnv --path .\out\ContosoOrderMcpConnector_managed.zip `
    --settings-file ".\settings\connector.$Stage.json" --publish-changes

# 4. Create the MCP connection in the target, put its ID into agent.<stage>.json,
#    then import the agent solution.
pac solution import --environment $TargetEnv --path .\out\ContosoCustomerServiceAgent_managed.zip `
    --settings-file ".\settings\agent.$Stage.json" --publish-changes
