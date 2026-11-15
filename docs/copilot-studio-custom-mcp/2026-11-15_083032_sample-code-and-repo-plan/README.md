<!-- cspell:ignore aidevme Contoso APIM Entra ciamlogin Kusto Bicep RMA oid azd pac -->

# Research: sample code and repository plan for "Custom MCP servers for Copilot Studio"

Research run, 2026-11-15. Scope: all code in the seven drafts of the series (posts 50–56 in
`.content/wordpress-posts/`), a plan for the sample repository the posts promise, and what has to be provisioned
to build and test it. Sources: the drafts only. Nothing here was compiled, deployed or checked against Microsoft
Learn in this run. Facts that the drafts themselves mark `[VERIFY]` stay open.

## The short answer

- **The posts hold 85 code blocks.** About half are repo files or most of one (43). The rest are fragments (5),
  commands to keep as scripts or tests (18) and sample output (19). All of them are extracted under
  [samples/](samples/), with an index that gives each block's role and target path: [samples/INDEX.md](samples/INDEX.md).
- **The repo name and three folders are already fixed in the drafts:** `aidevme/copilot-studio-custom-mcp-samples`,
  with `logic-apps/` (Part 2), `apim/` (Part 3) and `dotnet-mcp-server/` (Part 4). Six posts carry
  `[ZSOLT: create the repo and confirm the URL]`.
- **The biggest missing piece is the Order Management API itself.** Parts 2 and 3 call it, Part 1 says "the full
  API … will live in one sample repository", but no post shows its code. It has to be written before the Logic Apps
  and API Management paths can run end to end.
- **The demo data and two key files differ between parts.** Settle these before you publish the repo, or readers
  will find code that doesn't match the post they came from (see [Inconsistencies](#inconsistencies-to-resolve)).
- **Minimum cloud footprint:** one Azure subscription in the workforce tenant, one Entra External ID tenant, and
  a Power Platform tenant with Dev, Test and Prod environments that have Copilot Studio. Running all three build
  paths at the same time costs at least about $223 a month in list prices before Container Apps and Copilot
  Credits (Logic Apps WS1 about $175 + API Management Developer about $48, both as stated in the drafts).

## What's in this folder

| Path | Content |
| --- | --- |
| `README.md` | This file: gaps, inconsistencies, repo plan and provisioning list |
| `samples/INDEX.md` | One row per code block: source line in the post, language, role, target path in the repo |
| `samples/part-1/` … `samples/part-7/` | The blocks, copied exactly as they stand in the drafts, one file each |

## The code in the posts, by part

| Part | Post | Blocks | What's complete enough to commit |
| --- | --- | --- | --- |
| 1 | 50 hub | 8 | The tool contract as MCP tool definitions; a Learn-style custom connector |
| 2 | 51 Logic Apps | 12 | `create_return/workflow.json`, `parameters.json`, `host.json`, `.vscode/mcp.json`; trigger schemas of all three tools |
| 3 | 52 API Management | 9 | The agent-facade OpenAPI file (250 lines), Bicep for the MCP server and the passthrough, three policies, a KQL query, curl smoke test |
| 4 | 53 C# on Container Apps | 31 | `.csproj`, `Program.cs`, `OrderStore.cs`, `OrderTools.cs`, customer context, return policy resource, appsettings, Dockerfile, probes, deploy commands, connector |
| 5 | 54 Security | 6 | Entra External ID registrations (Azure CLI), JWT validation and ownership checks in C#, the API Management policy with `validate-jwt` |
| 6 | 55 Tool design | 11 | "Before" and "after" tool lists, `OrderTools.cs` with annotations, agent instructions, a PowerShell contract test and its GitHub Actions job |
| 7 | 56 Governance | 8 | DLP URL patterns (PowerShell), `pac` export/import script, deployment settings, Node contract check, Agent 365 hunting query |

## Gaps: code the posts rely on but don't show

1. **Order Management API (the backend).** Needed: the three operations from Part 1 (`GET
   /customers/{customerId}/orders`, `GET /orders/{orderId}`, `POST /orders/{orderId}/returns`), the full OpenAPI 3.0
   file (Part 3 shows only the agent facade without `{customerId}`), in-memory demo data, the internal endpoint
   `GET /customers/by-identity/{oid}` that the Part 3 policy calls, and the `Contoso-Customer-Id` header that API
   Management sets. It must accept Entra tokens from managed identities, because the Logic Apps HTTP actions
   (`ManagedServiceIdentity`, audience `OrderApi_Audience`) and the API Management policy
   (`authentication-managed-identity`) both call it that way.
2. **The other two Logic Apps workflows.** Only `create_return` is complete. `find_orders` and `get_order_status`
   exist as trigger schemas and one HTTP action. Also missing: `connections.json` (if any), `local.settings.json`
   template and the logic app's infrastructure.
3. **The rest of the C# project.** Part 5 says "the repo's version adds the records, the demo stores and the return
   policy resource". `OrderTools.cs` uses `Contoso.OrdersMcp.Data` and `Contoso.OrdersMcp.Resources`, so the
   record types and namespaces have to be written to match.
4. **Infrastructure as code.** Part 3's Bicep "needs the `apim` resource from the earlier file", which isn't shown.
   There's no IaC for the logic app, the Container Apps environment (CLI only), Key Vault, Log Analytics or
   Application Insights.
5. **Contract snapshots.** Part 7's Node check compares a baseline and a candidate `tools/list`; the repo needs a
   committed baseline (`contract/tools.json` is the natural one).
6. **Copilot Studio solutions.** Part 7 exports `ContosoOrderMcpConnector` and `ContosoCustomerServiceAgent` from
   Dev. They exist only once you build them in an environment; the unpacked solutions can then go into the repo.

## Inconsistencies to resolve

| Topic | Where it differs | Suggestion |
| --- | --- | --- |
| Demo data | Part 4: `CU-3001` has four orders (`SO-10019`, `SO-10023`, `SO-10031`, `SO-10035`), `CU-3002` owns `SO-10027`. Part 6: `CU-3001` has three, `CU-3002` owns `SO-10040`. Part 2 uses `SO-10099` as another customer's order; Part 3 uses `SO-10024` as a guessable order number | One seed file, `order-api/data/seed.json`, used by the API and the C# server; align Parts 2 and 6 to Part 4 |
| Where the C# server gets its data | Part 6 says "Part 4 replaces the store with calls to the Order Management API"; Part 4 keeps the in-memory store | Correct the sentence in Part 6, or add an `OrderApiClient` option to the C# server |
| `OrderTools.cs` | Part 4 and Part 6 versions differ by about 250 diff lines (annotations, descriptions, error messages) | One final version in the repo; see [code state per part](#code-state-per-part) |
| API Management OAuth policy | Part 3 snippet 4 and Part 5 snippet 5 differ by about 100 diff lines | Keep one policy file; make the other post's snippet an excerpt of it |
| Tool contract | `part-1/01` and `part-6/02` are not the same JSON | Make `contract/tools.json` the single source; regenerate the snippets from it |
| Two contract checks | PowerShell (Part 6) and Node (Part 7) | Keep both if both posts stay as they are; each in `tests/contract/` |
| `host.json` | Part 2's sample sets the SSE-only `AllowCrossWorkerCommunication` setting that the same post says Copilot Studio doesn't need | Leave it out of the repo file, or comment it as SSE only |
| Resource names | `rg-contoso-mcp` and `rg-contoso-orders`; `kv-contoso-mcp` and `kv-contoso-demo` | Pick one naming set (below) and align the posts |
| Placeholders | `{{external-id-tenant-id}}` and `{{external-tenant-id}}`; `{{orders-api-client-id}}` and `{{orders-mcp-api-client-id}}` | One placeholder list in the repo's `README.md` |

## Proposed repository

**`aidevme/copilot-studio-custom-mcp-samples`**, public. License: MIT `[ZSOLT: confirm]`. Default branch `main`.

```text
copilot-studio-custom-mcp-samples/
├── README.md                 # series map: which folder matches which post, placeholders, demo data
├── LICENSE
├── contract/
│   └── tools.json            # the tool contract: names, descriptions, input schemas (Parts 1 and 6)
├── order-api/                # NEW: the backend REST API (ASP.NET Core minimal API)
│   ├── src/                  # three operations, /customers/by-identity/{oid}, Entra auth
│   ├── data/seed.json        # the one demo data set for every path
│   └── openapi/orders-api.yaml
├── logic-apps/               # Part 2 (folder name fixed in the post)
│   ├── src/                  # host.json, parameters.json, find_orders/, get_order_status/, create_return/
│   ├── infra/                # NEW: Bicep for the Standard logic app and its plan
│   ├── test/                 # inspector.sh, smoke.sh, requests.http
│   └── .vscode/mcp.json
├── apim/                     # Part 3 (folder name fixed in the post)
│   ├── openapi/orders-agent-facade.yaml
│   ├── policies/             # mcp-server-oauth.xml, mcp-server-demo.xml, find-orders-operation.xml
│   ├── infra/                # NEW apim.bicep + mcp-server.bicep + mcp-passthrough.bicep
│   ├── queries/latest-tool-calls.kql
│   └── test/smoke.sh
├── dotnet-mcp-server/        # Parts 4–6 (folder name fixed in the post)
│   ├── src/Contoso.OrdersMcp/
│   ├── tests/Contoso.OrdersMcp.Tests/   # NEW: unit tests for ownership and the return window
│   ├── infra/                # deploy-containerapp.sh, probes.yaml (later: Bicep)
│   ├── Dockerfile
│   └── test/                 # smoke.sh, inspector.sh, requests.http
├── identity/
│   └── external-id/register-apps.sh     # Part 5
├── copilot-studio/
│   ├── connectors/           # swagger files from Parts 1, 4, 5 and 7
│   ├── agent-instructions.md # Part 6
│   └── solutions/            # NEW: unpacked solutions once built (Part 7)
├── governance/               # Part 7
│   ├── dlp/Set-McpUrlPatterns.ps1
│   ├── alm/deploy-mcp-solutions.ps1, settings/
│   └── queries/agent365-mcp-hunting.kql
├── tests/contract/           # Test-McpToolContract.ps1 (Part 6), check-tool-contract.js (Part 7)
└── .github/
    ├── workflows/            # build.yml, contract-test.yml (Part 6), bicep-lint.yml
    ├── ISSUE_TEMPLATE/
    └── pull_request_template.md   # Part 7's approval checklist
```

**Conventions:**

- **Each folder has a `README.md`** that says which post it belongs to, what it needs and how to run it locally
  and in Azure.
- **No secrets in the repo.** `.env.example` and `local.settings.example.json` only. Deploy workflows, if you add
  them, sign in with OpenID Connect (a federated credential on an Entra app), not a stored client secret.
- **Demo data only**, the same `Contoso` data as the posts.
- **CI on every pull request:** `dotnet build` and `dotnet test`, the contract test against a locally started C#
  server, `az bicep build` for every Bicep file, markdown lint.
- **Dependabot** for NuGet, npm and GitHub Actions; the posts pin versions (`ModelContextProtocol.AspNetCore`
  2.4.0, .NET 10, `Azure.Monitor.OpenTelemetry.AspNetCore` 1.6.0), so each update should be a reviewed pull
  request that also checks the post.

### Code state per part

The C# server changes across Parts 4, 5 and 6 (demo header → validated customer token → richer tool
descriptions). Three ways to keep posts and repo in step:

| Option | How | Trade-off |
| --- | --- | --- |
| **A. Final state on `main` plus a tag per post** (recommended) | `main` has the Part 6 tools and Part 5 auth, with the demo header kept behind `Demo:AllowDemoHeader` for local runs. Tags `part-4`, `part-5`, `part-6` mark the matching states; each post links its tag | One codebase to maintain; readers of Part 4 see a later state on `main` |
| B. One folder per part | `dotnet-mcp-server/part-4/`, `part-5/`, … | Every post matches exactly; three copies to keep up to date |
| C. Final state only | Posts link `main` | Simplest; Part 4 snippets drift from the code |

## What to provision

### GitHub

| Item | Detail |
| --- | --- |
| Repository | `aidevme/copilot-studio-custom-mcp-samples`, public, MIT, description and topics (`mcp`, `copilot-studio`, `azure-api-management`, `logic-apps`, `azure-container-apps`, `entra-external-id`) |
| Branch protection on `main` | Pull requests required, status checks `build` and `contract-test` |
| Actions | Enabled; Dependabot alerts and version updates; secret scanning and push protection |
| Environment `azure-demo` (optional) | Only if CI deploys: variables `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID` for OIDC, no secrets |

### Azure (workforce tenant)

Suggested naming set, built from the names the posts already use. Region `westeurope` (Parts 3 and 4).

| Resource | Name | For | Cost note from the drafts |
| --- | --- | --- | --- |
| Subscription | (yours) | Everything below | Set a budget alert |
| Resource group | `rg-contoso-mcp` | All demo resources, so one delete removes them | — |
| Log Analytics workspace + Application Insights | `log-contoso-mcp`, `appi-contoso-mcp` | Telemetry for all three paths (Parts 2, 3, 4) | Pay per GB `[VERIFY]` |
| Key Vault | `kv-contoso-mcp` | Connector client secret (Part 5), Logic Apps MCP key | Small |
| Order Management API host | e.g. a container app `contoso-orders-api` in the same environment | Backend for Parts 2 and 3 | — |
| Container Apps environment | `cae-contoso-mcp` | C# MCP server and the order API | — |
| Container app | `contoso-orders-mcp`, min and max replicas 1 (in-memory store) | Part 4 server | `[VERIFY: Container Apps price for one always-on replica]` |
| Standard logic app + Workflow Service Plan WS1 | `logic-contoso-orders-mcp` | Part 2 | About $175 a month (Learn's illustration, per Part 2) |
| API Management, Developer tier | `apim-contoso-orders` | Part 3; Consumption isn't supported | About $48 a month (Part 3, West Europe list price) |
| Managed identities | System-assigned on the logic app and API Management | Calls to the order API (Parts 2 and 3) | — |
| Entra app registration (workforce) | "Contoso Order Management API", App ID URI | The audience the managed identities request (`OrderApi_Audience`, `{{orders-api-app-id-uri}}`) | — |

The Developer tier and WS1 bill per hour while they exist. Deploy them for a test session and delete them
afterwards if you don't need them running; the Bicep files make that cheap to repeat.

### Microsoft Entra External ID tenant (Part 5)

| Item | Detail |
| --- | --- |
| External tenant | Its own tenant, `https://<tenant-subdomain>.ciamlogin.com`; linked to your subscription for billing `[VERIFY: External ID free tier for the demo's few users]` |
| App registration "Contoso Orders MCP API" | Application ID URI, scopes `Orders.Read` and `Returns.Create`, `accessTokenAcceptedVersion` 2 |
| App registration "Contoso Orders MCP Connector" | Client secret (into `kv-contoso-mcp`), Copilot Studio redirect URL, delegated permissions with admin consent |
| Sign-up and sign-in user flow | The connector app added to it (one user flow per app) |
| Two demo customer accounts | Mapped to `CU-3001` and `CU-3002` through `oid` for the ownership test Part 5 asks for |

### Power Platform and Copilot Studio (Parts 1, 5, 7)

| Item | Detail |
| --- | --- |
| Environments | `contoso-dev`, `contoso-test`, `contoso-prod` (Part 7 uses `contoso-dev.crm4.dynamics.com` and `contoso-test.crm4.dynamics.com`), each with Dataverse and Copilot Studio |
| Licensing | Copilot Studio capacity (Copilot Credits) or a trial for the demo; customer-facing use consumes credits for every tool call (Part 7) `[VERIFY: what your tenant has; trial limits]` |
| Publisher | Prefix `cts` (Part 7, environment variable `cts_OrderMcpHost`) |
| Solutions | `ContosoOrderMcpConnector` (custom MCP connector, environment variable) and `ContosoCustomerServiceAgent` (the agent, connection reference) |
| Data policy | Tenant-level policy "Contoso - Agents - Production" with URL patterns (Part 7); test it in a non-production tenant or environment group first |
| Channel | Custom Website channel for the External ID sign-in test (Part 5) |
| Monthly limit | A consumption limit per agent in the Power Platform admin center (Part 7) |
| Agent 365 (optional) | Only for the BYO server registration and the hunting query in Part 7 |

### Local tools

| Tool | Version in the drafts | For |
| --- | --- | --- |
| .NET SDK | 10.0.300 | C# server and order API |
| Node.js | 22.19.0 or newer | MCP Inspector (`npx`), Part 7 contract check |
| Azure CLI | 2.87.0, plus `containerapp` extension and Bicep | Deploys, Entra registrations |
| PowerShell | 7 | Part 6 contract test, Part 7 scripts |
| Power Platform CLI (`pac`) | — | Part 7 export and import |
| `Microsoft.PowerApps.Administration.PowerShell` | — | Part 7 DLP script |
| VS Code + Azure Logic Apps (Standard) extension + GitHub Copilot | VS Code after 1.102 | Part 2 local workflows and MCP test |
| Docker | — (optional) | Local image build; `az containerapp up` builds in the cloud without it |

## Suggested order of work

1. **Decide** the open questions below, then fix the demo data and the contract (`contract/tools.json`,
   `order-api/data/seed.json`).
2. **Create the repo** with the skeleton, README, license, CI and branch protection.
3. **Build the C# MCP server** from the Part 4–6 code (it runs locally with no Azure), then its unit tests and
   the contract test.
4. **Write the Order Management API** and its full OpenAPI file; deploy it with the C# server to Container Apps.
5. **API Management** (Part 3) and **Logic Apps** (Part 2) against the deployed API.
6. **External ID** (Part 5), then Copilot Studio in Dev, then the solutions and ALM (Part 7).
7. **Fill the `[ZSOLT: …]` markers** in the posts with the screenshots and results from these runs, and replace
   the repo URL markers.

## Questions for Zsolt

1. Code state per part: option A (final state + tags), B (folder per part) or C (final state only)?
2. Should the Order Management API be ASP.NET Core like the MCP server (one language, shared seed data), or do you
   want something else?
3. License: MIT?
4. Should CI deploy to Azure, or do you deploy by hand and CI only builds and tests?
5. Which demo data set wins: Part 4's (four orders for `CU-3001`, `SO-10027` for `CU-3002`) or Part 6's?
6. Run all three paths at the same time for the screenshots, or one after the other to keep the monthly cost down?
