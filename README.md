# Custom MCP servers for Copilot Studio: samples

[![MCP contract test](https://github.com/aidevme/copilot-studio-custom-mcp-samples/actions/workflows/contract-test.yml/badge.svg?branch=main)](https://github.com/aidevme/copilot-studio-custom-mcp-samples/actions/workflows/contract-test.yml)
[![License: MIT](https://img.shields.io/github/license/aidevme/copilot-studio-custom-mcp-samples)](LICENSE)
[![.NET 10](https://img.shields.io/badge/.NET-10-512BD4?logo=dotnet&logoColor=white)](https://dotnet.microsoft.com/download/dotnet/10.0)
[![MCP C# SDK 2.4.0](https://img.shields.io/badge/ModelContextProtocol.AspNetCore-2.4.0-004880?logo=nuget&logoColor=white)](https://www.nuget.org/packages/ModelContextProtocol.AspNetCore/2.4.0)
[![MCP protocol 2025-11-25](https://img.shields.io/badge/MCP%20protocol-2025--11--25-informational)](https://modelcontextprotocol.io/specification/2025-11-25)
[![Blog series](https://img.shields.io/badge/aidevme.com-read%20the%20series-0A66C2)](https://aidevme.com/copilot-studio-custom-mcp-servers-when-you-need-one/)

![Custom MCP servers for Copilot Studio: samples](assets/copilot-studio-custom-mcp-samples-social-preview.png)

Sample code for the [aidevme.com](https://aidevme.com) series **Custom MCP servers for Copilot Studio**. One demo,
a Contoso customer service agent that answers order questions and starts returns, is built three ways: with
Logic Apps Standard, Azure API Management and a C# server on Azure Container Apps. Customer sign-in with
Microsoft Entra External ID, tool contract tests and Power Platform ALM scripts complete it.

> [!NOTE]
> **Work in progress.** The folder structure is in place and the samples are being added part by part. The status
> column below shows what's ready.

## The series

| Part | Post | Folder | Status |
| --- | --- | --- | --- |
| 1 | [Copilot Studio Custom MCP Servers: When to Build One and How](https://aidevme.com/copilot-studio-custom-mcp-servers-when-you-need-one/) | [`contract/`](contract/), [`order-api/`](order-api/) | Planned |
| 2 | [Logic Apps Standard MCP Server for Copilot Studio: Low-Code Guide](https://aidevme.com/copilot-studio-custom-mcp-server-logic-apps/) | [`logic-apps/`](logic-apps/) | Planned |
| 3 | [Azure API Management as an MCP Server for Copilot Studio: REST APIs as Tools](https://aidevme.com/copilot-studio-custom-mcp-server-api-management/) | [`apim/`](apim/) | Planned |
| 4 | [Build a Pro-Code MCP Server in C# on Azure for Copilot Studio](https://aidevme.com/copilot-studio-custom-mcp-server-azure-pro-code/) | [`dotnet-mcp-server/`](dotnet-mcp-server/) | Planned |
| 5 | [Securing Custom MCP Servers for Copilot Studio: Customer Sign-In](https://aidevme.com/copilot-studio-custom-mcp-server-security-oauth-entra-id/) | [`identity/`](identity/), [`dotnet-mcp-server/`](dotnet-mcp-server/), [`apim/`](apim/) | Planned |
| 6 | [Copilot Studio MCP Tool Design: Descriptions, Tool Count and Testing](https://aidevme.com/copilot-studio-custom-mcp-tool-design-testing/) | [`contract/`](contract/), [`tests/`](tests/), [`dotnet-mcp-server/`](dotnet-mcp-server/) | Planned |
| 7 | [Governing Custom MCP Servers in Copilot Studio: DLP, ALM and Approval](https://aidevme.com/copilot-studio-custom-mcp-governance-alm/) | [`governance/`](governance/), [`copilot-studio/`](copilot-studio/) | Planned |

## The demo

Contoso is a fictional retailer of home and kitchen appliances. Its customer service agent in Copilot Studio runs on
the Contoso website and handles questions such as "Where is my order SO-10023?" and "The kettle arrived broken, I
want to return it."

The order data lives outside Dataverse, in an order management system with a REST API. Every build path exposes
the same three tools on top of it:

| Tool | Order Management API | Purpose |
| --- | --- | --- |
| `find_orders` | `GET /customers/{customerId}/orders` | The signed-in customer's orders, filtered by status and date |
| `get_order_status` | `GET /orders/{orderId}` | One order: status, lines, carrier, tracking, expected delivery |
| `create_return` | `POST /orders/{orderId}/returns` | Start a return and get the return number (RMA) |

Two rules hold on every path. The customer ID comes from the caller's identity, never from a tool input, and
another customer's order is "not found". Returns are accepted only for delivered orders, within 30 days after
delivery, and the server enforces that, not the model.

## Repository layout

| Folder | Content |
| --- | --- |
| [`contract/`](contract/) | The tool contract every path implements: names, descriptions, input schemas |
| [`order-api/`](order-api/) | The Order Management API with in-memory demo data, and its OpenAPI description |
| [`logic-apps/`](logic-apps/) | Logic Apps Standard workflows as an MCP server |
| [`apim/`](apim/) | API Management: the agent facade, policies, Bicep, telemetry query |
| [`dotnet-mcp-server/`](dotnet-mcp-server/) | The C# MCP server (ASP.NET Core, MCP C# SDK) for Azure Container Apps |
| [`identity/`](identity/) | Entra External ID app registrations for customer sign-in |
| [`copilot-studio/`](copilot-studio/) | Custom connector definitions and the agent and connector solutions |
| [`governance/`](governance/) | Data policy URL patterns, solution export and import, monitoring queries |
| [`tests/`](tests/) | Contract tests that compare a server's `tools/list` with the contract |

Each folder has its own `README.md` with what it needs and how to run it.

## What you need

The tools and cloud resources each part needs are listed in [DEVELOPER.md](DEVELOPER.md#what-you-need).

## Demo data and secrets

- All data is fictional demo data: Contoso, customers such as `CU-3001`, orders such as `SO-10023`, returns such as
  `RMA-5001`.
- The repo contains no keys, secrets or tenant IDs. Settings use placeholders such as `<external-tenant-id>`;
  copy the `*.example` files and fill in your own values locally.

## Contributing

Issues and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for how to report a problem, make a
change and class a tool contract change.

## License

[MIT](LICENSE) © 2026 Zsolt Zombik
