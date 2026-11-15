# AGENTS.md

Guidance for AI coding agents working in this repository. Humans: start with [README.md](README.md).

## What this repo is

Sample code for the aidevme.com blog series **Custom MCP servers for Copilot Studio** (7 parts). One demo, a Contoso
customer service agent that looks up orders and starts returns, is built three ways:

- `src/logic-apps/`: Logic Apps Standard workflows as an MCP server (Part 2)
- `src/apim/`: Azure API Management exposing a REST API as MCP tools (Part 3)
- `src/dotnet-mcp-server/`: a C# server (ASP.NET Core, `ModelContextProtocol.AspNetCore`) on Azure Container Apps (Parts 4 to 6)

Supporting folders: `src/contract/` (the shared tool contract), `src/order-api/` (backend, not written yet), `src/identity/`
(Entra External ID, Part 5), `src/copilot-studio/` (custom connectors, agent instructions), `src/governance/` (DLP, ALM,
monitoring, Part 7), `src/tests/` (contract tests). Each folder has a `README.md`; read it before changing the folder.

`docs/copilot-studio-custom-mcp/<timestamp>_sample-code-and-repo-plan/` holds the code blocks extracted verbatim
from the blog drafts plus a plan with known gaps and inconsistencies. Treat `docs/` as a read-only reference
snapshot: don't edit the extracted samples to fix the repo; fix the real file in its component folder.

## The code must match the posts

Every file here is quoted in, or promised by, a published post. A reader who copies from the post and then opens the
repo must find the same thing.

- Before changing code, find which part it belongs to (folder README, the `# --- Part N:` comments in scripts, the
  PR template's folder list). If your change makes the post's code wrong, say so in your summary: name the part and
  what in the post must change.
- Keep package versions, API versions, protocol version (`2025-11-25`), ports, resource names and header names as
  they are unless asked. Don't "upgrade" them.
- `src/dotnet-mcp-server/src/` is the **Part 4** state. `src/dotnet-mcp-server/variants/part-5-*` and `part-6-*` are the later
  versions of the changed files; they use different types and are not meant to build on their own. Don't merge them
  into `src/` unless asked.
- Scripts under `*/test/*.sh` are mostly command collections from the posts, with placeholders. They aren't all
  meant to run top to bottom.

## Rules that hold on every build path

1. **The customer ID comes from the caller's identity, never from a tool input.** No tool takes `customerId`,
   `userId` or `email`. Another customer's order returns "not found", not "forbidden".
2. **Business rules are enforced on the server, not left to the model.** Returns only for delivered orders, within
   30 days after delivery.
3. **The tool contract is `src/contract/tools.json`.** Three tools: `find_orders`, `get_order_status`, `create_return`.
   Names, descriptions and input schemas must stay in sync across all paths. Description changes alter how the
   Copilot Studio orchestrator routes, so treat them as behavior changes. Classify contract changes as BREAKING,
   REVIEW or ADDITIVE (see `.github/pull_request_template.md`) and update `src/contract/tools.json` with them.
4. The `Contoso-Demo-Customer` header (`Demo:AllowCustomerHeader`) is a local-testing shortcut. Never enable it in
   anything meant for deployment, and never widen what it can do.

## Data and secrets

- Demo data only: Contoso, customers like `CU-3001`, orders like `SO-10023`, returns like `RMA-5001`. No real names,
  tenants, domains or URLs other than Microsoft/aidevme public docs.
- No keys, client secrets, connection strings, tokens, tenant or subscription IDs. Use placeholders such as
  `<external-tenant-id>`, and `*.example` files for local settings.

## Build and test

Toolchain: .NET 10 SDK, Node.js 22.19+ (MCP Inspector), Azure CLI with Bicep, PowerShell 7, `pac` CLI.

```sh
# C# server (Part 4)
dotnet build src/dotnet-mcp-server/src/Contoso.OrdersMcp
dotnet run --project src/dotnet-mcp-server/src/Contoso.OrdersMcp --urls http://localhost:5080

# Contract test against a running server
pwsh ./src/tests/contract/Test-McpToolContract.ps1 -Endpoint http://localhost:5080/mcp
# Compare two tools/list snapshots; exit 1 on a breaking change
node src/tests/contract/check-tool-contract.js src/contract/tools-before.json src/contract/tools.json

# Bicep
az bicep build --file src/apim/infra/mcp-server.bicep
```

There are no unit tests yet (`src/dotnet-mcp-server/tests/` is a placeholder). Nothing in this repo has been deployed
to Azure as part of CI; don't claim something works in Azure or Copilot Studio unless you ran it there.

CI: `.github/workflows/contract-test.yml` starts the C# server and runs the PowerShell contract test on every push to
`main` or `dev` and on every pull request.

## Writing style

READMEs and comments follow the blog's style: plain, short sentences, sentence-case headings, no marketing words,
tables for reference material. Keep the series table in the root `README.md` (Status column) current when a part's
samples become ready.

## Git

- Work on `dev`; `main` is the published branch. Commit or push only when asked.
- Commit messages: a short imperative subject ("Add …", "Fix …") and a body that says what changed and why.
