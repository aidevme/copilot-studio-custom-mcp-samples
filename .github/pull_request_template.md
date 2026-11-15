## What this changes

<!-- One or two sentences: what changes and why. Link the issue if there is one: Closes #123 -->

## Where

<!-- Tick every folder this pull request touches. -->

- [ ] `src/contract/`: tool contract (Parts 1 and 6)
- [ ] `src/order-api/`: Order Management API and demo data
- [ ] `src/logic-apps/`: Logic Apps Standard (Part 2)
- [ ] `src/apim/`: API Management (Part 3)
- [ ] `src/dotnet-mcp-server/`: C# server on Container Apps (Parts 4 to 6)
- [ ] `src/identity/`: Entra External ID (Part 5)
- [ ] `src/copilot-studio/`: connectors and solutions
- [ ] `src/governance/`: data policies, ALM, monitoring (Part 7)
- [ ] `src/tests/`, `.github/`: contract tests and workflows

**Post the change belongs to:** <!-- e.g. Part 4. Does the post's code still match? If not, say what must change in the post. -->

## Checks

- [ ] Builds and runs locally (`dotnet build`, `az bicep build`, or the folder's own README steps)
- [ ] Contract test passes, or the contract change is described below
- [ ] Demo data only: Contoso customers, orders and returns from `src/order-api/data/`; no real names, tenants or URLs
- [ ] No secrets: no keys, client secrets, connection strings or tokens; placeholders such as `<external-tenant-id>` instead
- [ ] Folder `README.md` updated if setup, commands or behavior changed
- [ ] Package and API versions in the change match the post, or the post is listed for an update

## Tool contract changes

<!-- Fill this in only if a tool's name, description, inputs or behavior changes. Delete it otherwise. -->

| Tool | Change | Class |
| --- | --- | --- |
| `tool_name` | What changed | BREAKING / REVIEW / ADDITIVE |

<!--
BREAKING: tool removed or renamed, input removed, renamed or made required, type changed. Agents stop working.
REVIEW:   description changed. The orchestrator routes on descriptions, so agent behavior can change.
ADDITIVE: new tool or new optional input. Safe for existing agents, but a new tool appears in every agent with "Allow all".
-->

- [ ] `src/contract/tools.json` updated to the new `tools/list` output
- [ ] Read or write and side effects stated for every new tool (reversible? financial impact?)
- [ ] The customer ID still comes from the caller's identity, never from a tool input; other customers' orders return "not found"
- [ ] Business rules (delivered orders only, 30-day return window) are enforced on the server, not left to the model
- [ ] Breaking changes ship as a new tool or with a deprecation period, not as an in-place change

## How it was tested

<!-- Commands you ran and what they returned: curl, MCP Inspector, the contract test, Copilot Studio test pane.
     Say what you didn't test, for example "not deployed to Azure". -->
