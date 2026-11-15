# Custom MCP servers for Copilot Studio: samples

[![MCP contract test](https://github.com/aidevme/copilot-studio-custom-mcp-samples/actions/workflows/contract-test.yml/badge.svg?branch=main)](https://github.com/aidevme/copilot-studio-custom-mcp-samples/actions/workflows/contract-test.yml)
[![License: MIT](https://img.shields.io/github/license/aidevme/copilot-studio-custom-mcp-samples)](LICENSE)
[![.NET 10](https://img.shields.io/badge/.NET-10-512BD4?logo=dotnet&logoColor=white)](https://dotnet.microsoft.com/download/dotnet/10.0)
[![MCP C# SDK 2.4.0](https://img.shields.io/badge/ModelContextProtocol.AspNetCore-2.4.0-004880?logo=nuget&logoColor=white)](https://www.nuget.org/packages/ModelContextProtocol.AspNetCore/2.4.0)
[![MCP protocol 2025-11-25](https://img.shields.io/badge/MCP%20protocol-2025--11--25-informational)](https://modelcontextprotocol.io/specification/2025-11-25)
[![Blog series](https://img.shields.io/badge/aidevme.com-read%20the%20series-0A66C2)](https://aidevme.com/copilot-studio-custom-mcp-servers-when-you-need-one/)

![Custom MCP servers for Copilot Studio: samples](assets/copilot-studio-custom-mcp-samples-social-preview.png)

Sample code for the [aidevme.com](https://aidevme.com) series **Custom MCP servers for Copilot Studio**. One demo,
a AIDevMe customer service agent that answers order questions and starts returns, is built three ways: with
Logic Apps Standard, Azure API Management and a C# server on Azure Container Apps. Customer sign-in with
Microsoft Entra External ID, tool contract tests and Power Platform ALM scripts complete it.

> [!NOTE]
> **Work in progress.** The folder structure is in place and the samples are being added part by part. The status
> column below shows what's ready.

## The series

| Part | Post | Folder | Status |
| --- | --- | --- | --- |
| 1 | [Copilot Studio Custom MCP Servers: When to Build One and How](https://aidevme.com/copilot-studio-custom-mcp-servers-when-you-need-one/) | [`src/contract/`](src/contract/), [`src/order-api/`](src/order-api/) | Planned |
| 2 | [Logic Apps Standard MCP Server for Copilot Studio: Low-Code Guide](https://aidevme.com/copilot-studio-custom-mcp-server-logic-apps/) | [`src/logic-apps/`](src/logic-apps/) | Planned |
| 3 | [Azure API Management as an MCP Server for Copilot Studio: REST APIs as Tools](https://aidevme.com/copilot-studio-custom-mcp-server-api-management/) | [`src/apim/`](src/apim/) | Planned |
| 4 | [Build a Pro-Code MCP Server in C# on Azure for Copilot Studio](https://aidevme.com/copilot-studio-custom-mcp-server-azure-pro-code/) | [`src/dotnet-mcp-server/`](src/dotnet-mcp-server/) | Planned |
| 5 | [Securing Custom MCP Servers for Copilot Studio: Customer Sign-In](https://aidevme.com/copilot-studio-custom-mcp-server-security-oauth-entra-id/) | [`src/identity/`](src/identity/), [`src/dotnet-mcp-server/`](src/dotnet-mcp-server/), [`src/apim/`](src/apim/) | Planned |
| 6 | [Copilot Studio MCP Tool Design: Descriptions, Tool Count and Testing](https://aidevme.com/copilot-studio-custom-mcp-tool-design-testing/) | [`src/contract/`](src/contract/), [`src/tests/`](src/tests/), [`src/dotnet-mcp-server/`](src/dotnet-mcp-server/) | Planned |
| 7 | [Governing Custom MCP Servers in Copilot Studio: DLP, ALM and Approval](https://aidevme.com/copilot-studio-custom-mcp-governance-alm/) | [`src/governance/`](src/governance/), [`src/copilot-studio/`](src/copilot-studio/) | Planned |

## The demo

In this demo, AIDevMe is a fictional retailer of home and kitchen appliances. Its customer service agent in Copilot Studio runs on
the AIDevMe website and handles questions such as "Where is my order SO-10023?" and "The kettle arrived broken, I
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

The sample code lives under [`src/`](src/), one folder per component:

| Folder | Content |
| --- | --- |
| [`src/contract/`](src/contract/) | The tool contract every path implements: names, descriptions, input schemas |
| [`src/order-api/`](src/order-api/) | The Order Management API with in-memory demo data, and its OpenAPI description |
| [`src/logic-apps/`](src/logic-apps/) | Logic Apps Standard workflows as an MCP server |
| [`src/apim/`](src/apim/) | API Management: the agent facade, policies, Bicep, telemetry query |
| [`src/dotnet-mcp-server/`](src/dotnet-mcp-server/) | The C# MCP server (ASP.NET Core, MCP C# SDK) for Azure Container Apps |
| [`src/identity/`](src/identity/) | Entra External ID app registrations for customer sign-in |
| [`src/copilot-studio/`](src/copilot-studio/) | Custom connector definitions and the agent and connector solutions |
| [`src/governance/`](src/governance/) | Data policy URL patterns, solution export and import, monitoring queries |
| [`src/tests/`](src/tests/) | Contract tests that compare a server's `tools/list` with the contract |

Each folder has its own `README.md` with what it needs and how to run it.

In detail, with the parts each file belongs to. Folders marked *planned* are empty for now.

```text
copilot-studio-custom-mcp-samples/
├── README.md, DEVELOPER.md, CONTRIBUTING.md, LICENSE
├── src/
│   ├── contract/
│   │   ├── tools.json                    # the tool contract (Parts 1 and 6)
│   │   └── tools-before.json             # the "before" tool list (Part 6)
│   ├── order-api/                        # the Order Management API (planned)
│   │   ├── src/                          # three operations, /customers/by-identity/{oid} (planned)
│   │   ├── data/                         # seed.json, the one demo data set (planned)
│   │   └── openapi/                      # orders-api.yaml (planned)
│   ├── logic-apps/                       # Part 2
│   │   ├── src/                          # host.json, parameters.json, create_return/
│   │   ├── infra/                        # Bicep for the logic app and its plan (planned)
│   │   ├── test/                         # inspector.sh, smoke.sh, requests.http
│   │   └── .vscode/mcp.json
│   ├── apim/                             # Part 3
│   │   ├── openapi/orders-agent-facade.yaml
│   │   ├── policies/                     # OAuth, OAuth with oid header, demo key, find_orders rewrite
│   │   ├── infra/                        # mcp-server.bicep, mcp-passthrough.bicep
│   │   ├── scripts/import-api.sh
│   │   ├── queries/latest-tool-calls.kql
│   │   └── test/smoke.sh
│   ├── dotnet-mcp-server/                # Parts 4 to 6
│   │   ├── src/AIDevMe.OrdersMcp/        # the Part 4 server: Program.cs, Tools/, Data/, Resources/
│   │   ├── variants/                     # part-5-customer-sign-in/, part-6-tool-design/
│   │   ├── tests/AIDevMe.OrdersMcp.Tests/  # unit tests (planned)
│   │   ├── infra/                        # deploy-containerapp.sh, probes.yaml
│   │   ├── test/                         # smoke.sh, inspector.sh
│   │   └── Dockerfile
│   ├── identity/
│   │   └── external-id/register-apps.sh  # Part 5
│   ├── copilot-studio/
│   │   ├── connectors/                   # custom connector definitions (Parts 1, 4, 5 and 7)
│   │   ├── agent-instructions.md         # Part 6
│   │   └── solutions/                    # unpacked solutions (Part 7, planned)
│   ├── governance/                       # Part 7
│   │   ├── dlp/Set-McpUrlPatterns.ps1
│   │   ├── alm/                          # deploy-mcp-solutions.ps1, settings/
│   │   └── queries/agent365-mcp-hunting.kql
│   └── tests/
│       ├── contract/                     # Test-McpToolContract.ps1 (Part 6), check-tool-contract.js (Part 7)
│       └── http/protocol-examples.http   # raw MCP requests (Part 1)
├── docs/                                 # the code blocks from the posts, as a read-only reference
└── .github/                              # contract test workflow, issue forms, pull request template
```

## What you need

The tools and cloud resources each part needs are listed in [DEVELOPER.md](DEVELOPER.md#what-you-need).

## Demo data and secrets

- All order data is fictional demo data: AIDevMe as the retailer, customers such as `CU-3001`, orders such as `SO-10023`, returns such as
  `RMA-5001`.
- The repo contains no keys, secrets or tenant IDs. Settings use placeholders such as `<external-tenant-id>`;
  copy the `*.example` files and fill in your own values locally.

## Contributing

Issues and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for how to report a problem, make a
change and class a tool contract change.

## License

[MIT](LICENSE) © 2026 Zsolt Zombik
