# dotnet-mcp-server

The pro-code MCP server in C# (ASP.NET Core, MCP C# SDK), hosted on Azure Container Apps.

- `src/AIDevMe.OrdersMcp/`: the server
- `tests/AIDevMe.OrdersMcp.Tests/`: unit tests
- `infra/`: deployment and health probes
- `test/`: curl and MCP Inspector tests
- `variants/`: the Part 5 (customer sign-in) and Part 6 (tool design) versions of the changed files. They use different types from the Part 4 project and aren't merged into it yet, so they don't build on their own.

`src/` is the Part 4 state: in-memory demo orders and the `AIDevMe-Demo-Customer` header for local testing.

Posts: [Part 4](https://aidevme.com/copilot-studio-custom-mcp-server-azure-pro-code/), [Part 5](https://aidevme.com/copilot-studio-custom-mcp-server-security-oauth-entra-id/) and [Part 6](https://aidevme.com/copilot-studio-custom-mcp-tool-design-testing/).
