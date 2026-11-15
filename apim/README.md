# apim

Azure API Management exposing the Order Management API as an MCP server, and proxying the C# server.

- `openapi/`: the agent facade the gateway imports
- `policies/`: OAuth with the customer ID mapped in the gateway (Part 3), OAuth that passes `oid` to the backend (`mcp-server-oauth-oid-header.xml`, Part 5), demo mode and the `find_orders` rewrite
- `scripts/`: importing the facade with the Azure CLI
- `infra/`: Bicep for the instance, the MCP server and the passthrough server
- `queries/`: KQL for tool call telemetry
- `test/`: curl smoke test

Post: [Part 3](https://aidevme.com/copilot-studio-custom-mcp-server-api-management/).
