# apim

Azure API Management exposing the Order Management API as an MCP server, and proxying the C# server.

- `openapi/`: the agent facade the gateway imports
- `policies/`: OAuth, demo mode and the `find_orders` rewrite
- `infra/`: Bicep for the instance, the MCP server and the passthrough server
- `queries/`: KQL for tool call telemetry
- `test/`: curl smoke test

Post: [Part 3](https://aidevme.com/copilot-studio-custom-mcp-server-api-management/).
