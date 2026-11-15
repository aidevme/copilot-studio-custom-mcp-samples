# apim

Azure API Management exposing the Order Management API as an MCP server, and proxying the C# server.

- `openapi/`: the agent facade the gateway imports
- `policies/`: OAuth with the customer ID mapped in the gateway (Part 3), OAuth that passes `oid` to the backend (`mcp-server-oauth-oid-header.xml`, Part 5), demo mode and the `find_orders` rewrite
- `scripts/`: importing the facade with the Azure CLI, as shown in the post
- `infra/`: `apim.bicep` (the Developer instance, named values, product and imported facade), `mcp-server.bicep`
  (the MCP server and its tools), `mcp-passthrough.bicep` (a fragment from the post) and `deploy.sh`
- `queries/`: KQL for tool call telemetry
- `test/`: curl smoke test

Deploy: `src/apim/infra/deploy.sh`, after the base and the Order Management API; see
[DEVELOPER.md](../../DEVELOPER.md#deploy-to-azure). It deploys the demo-mode policy unless you set `USE_OAUTH=true`,
which needs the External ID values from Part 5. The Developer tier costs about $48 a month while it exists.

Post: [Part 3](https://aidevme.com/copilot-studio-custom-mcp-server-api-management/).
