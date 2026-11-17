# The tool contract

<!-- cspell:ignore aidevme apim appsettings vitepress containerapp Dataverse -->

Three tools, defined once in
[`src/contract/tools.json`](https://github.com/aidevme/copilot-studio-custom-mcp-samples/blob/main/src/contract/tools.json).
Names, descriptions and input schemas are the same on every build path.

| Tool | Order Management API | Purpose |
| --- | --- | --- |
| `find_orders` | `GET /customers/{customerId}/orders` | The signed-in customer's orders, filtered by status and date |
| `get_order_status` | `GET /orders/{orderId}` | One order: status, lines, carrier, tracking, expected delivery |
| `create_return` | `POST /orders/{orderId}/returns` | Start a return and get the return number (RMA) |

`find_orders` calls the API with the customer ID from the caller's identity. It isn't a tool input.

## Why descriptions count

The Copilot Studio orchestrator picks a tool by its description. Changing a description changes how the agent routes,
so treat it as a behavior change, not a text edit.

## Classify every change

| Class | What changed | Effect |
| --- | --- | --- |
| BREAKING | A tool removed or renamed; an input removed, renamed or made required; a type changed | Agents stop working. Ship it as a new tool or with a deprecation period |
| REVIEW | A description changed | The orchestrator routes on descriptions, so agent behavior can change |
| ADDITIVE | A new tool or a new optional input | Safe for existing agents, but a new tool appears in every agent with "Allow all" |

Update `src/contract/tools.json` with every change, and name the class in the pull request.

## Checks

```sh
# Contract test against a running server
pwsh ./src/tests/contract/Test-McpToolContract.ps1 -Endpoint http://localhost:5080/mcp

# Compare two tools/list snapshots; exit 1 on a breaking change
node src/tests/contract/check-tool-contract.js src/contract/tools-before.json src/contract/tools.json
```

CI runs the contract test against the C# server on every push to `main` or `dev` and on every pull request.
