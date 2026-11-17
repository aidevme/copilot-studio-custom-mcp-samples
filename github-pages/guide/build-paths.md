# Build paths

<!-- cspell:ignore aidevme apim appsettings vitepress containerapp Dataverse -->

The same three tools, built three ways. Pick the one that fits your team and the systems you already have.

| | Logic Apps Standard | Azure API Management | C# on Container Apps |
| --- | --- | --- | --- |
| Part | 2 | 3 | 4 to 6 |
| You write | Workflows | Policies and an OpenAPI facade | Code |
| Good fit | Low-code teams, connectors to other systems | An existing REST API, central gateway rules | Full control over tools, auth and tests |
| Tier in the demo | WS1 plan | Developer | Consumption |
| Approximate cost | About $175 a month | About $48 a month | Low |

The costs are the examples from the posts. Check the pricing for your region.

## Logic Apps Standard

Three workflows, `find_orders`, `get_order_status` and `create_return`, registered as one MCP server under **Agents →
MCP servers** in the portal. The workflows call the Order Management API with the logic app's managed identity.

- Code: [`src/logic-apps/`](https://github.com/aidevme/copilot-studio-custom-mcp-samples/tree/main/src/logic-apps)
- Endpoint format: `https://<logic-app-name>.azurewebsites.net/api/mcpservers/<server-name>/mcp`
- Authentication: key-based (`X-API-KEY`) for tests, OAuth for production

## Azure API Management

The Order Management API is imported as an agent facade, and API Management exports its operations as MCP tools.
Policies set the customer from the token and attach the gateway's managed identity token for the backend.

- Code: [`src/apim/`](https://github.com/aidevme/copilot-studio-custom-mcp-samples/tree/main/src/apim)
- Endpoint format: `https://<apim-name>.azure-api.net/orders-mcp/mcp`
- Authentication: a subscription key in demo mode, Entra External ID tokens in OAuth mode (Part 5)

## C# on Azure Container Apps

An ASP.NET Core server with `ModelContextProtocol.AspNetCore`, on the MCP protocol version `2025-11-25`. Parts 5 and 6
change some of its files; those versions are in `variants/`.

- Code: [`src/dotnet-mcp-server/`](https://github.com/aidevme/copilot-studio-custom-mcp-samples/tree/main/src/dotnet-mcp-server)
- Endpoint format: `https://<container-app-fqdn>/mcp`
- Authentication: Entra External ID tokens (Part 5)
