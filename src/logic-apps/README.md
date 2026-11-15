# logic-apps

Logic Apps Standard workflows exposed as an MCP server.

- `src/`: the workflows `find_orders`, `get_order_status` and `create_return`, `host.json`, `parameters.json`, and
  `local.settings.example.json` for a local run
- `infra/`: `main.bicep` (WS1 plan, storage, the logic app with a managed identity) and `deploy.sh`, which also
  deploys the workflows
- `test/`: MCP Inspector, curl and `.http` tests
- `.vscode/`: `mcp.json` for testing from VS Code

Every workflow reads the customer from the `AIDevMe-Demo-Customer` header (a test stub, see Part 5), calls the
Order Management API with the logic app's managed identity, and answers "not found" for another customer's order.
`find_orders` answers `401` without a customer.

Deploy: `src/logic-apps/infra/deploy.sh`, after the base and the Order Management API; see
[DEVELOPER.md](../../DEVELOPER.md#deploy-to-azure). Then register the MCP server in the portal (post Step 3). The
WS1 plan costs about $175 a month while it exists.

Post: [Part 2](https://aidevme.com/copilot-studio-custom-mcp-server-logic-apps/).
