# copilot-studio-custom-mcp-samples — Plan and progress

<!-- cspell:ignore aidevme Zsolt Zombik AIDevMe APIM Entra Bicep Dataverse oid evals -->

**Mission.** Give readers of the aidevme.com series **Custom MCP servers for Copilot Studio** (7 parts) working code
that matches the posts: one AIDevMe order-and-returns agent, built with Logic Apps Standard, Azure API Management
and a C# server on Azure Container Apps.

**Owner:** Zsolt Zombik · **Last updated:** 2026-11-15 · **Repo:**
[aidevme/copilot-studio-custom-mcp-samples](https://github.com/aidevme/copilot-studio-custom-mcp-samples)

**Sources:** the gaps, inconsistencies and provisioning list come from the research run in
`docs/copilot-studio-custom-mcp/2026-11-15_083032_sample-code-and-repo-plan/README.md`. Nothing has been deployed
to Azure or tested in Copilot Studio yet.

---

## Built

Legend: ✅ done · 🔄 in progress · ⬜ not started

| Area | What exists | Status |
| --- | --- | --- |
| Repo | Public repo, MIT license, `main` and `dev` branches, README with the series map, social preview image, `.gitignore` | ✅ |
| Guidance | `AGENTS.md` (code must match the posts, the two rules, no secrets) and `CLAUDE.md` pointing to it; PR template with the contract change classes | ✅ |
| Extracted samples | All 85 code blocks from the drafts in `docs/…/samples/`, with `INDEX.md`; read-only reference | ✅ |
| Contract (Parts 1, 6) | `src/contract/tools.json` (three tools) and `tools-before.json` | ✅ |
| C# server (Part 4) | `src/dotnet-mcp-server/src/AIDevMe.OrdersMcp/`: tools, in-memory store with Part 4's demo data, return policy resource, Dockerfile, Container Apps deploy script, probes; builds locally | ✅ |
| C# server (Parts 5, 6) | `src/dotnet-mcp-server/variants/part-5-customer-sign-in/` and `part-6-tool-design/`: the changed files only, not buildable on their own | ✅ |
| API Management (Part 3) | Agent-facade OpenAPI, four policies, `apim.bicep` (instance, named values, product, facade), `mcp-server.bicep`, `deploy.sh`, KQL query, import and smoke scripts; not deployed yet | 🔄 |
| Logic Apps (Part 2) | All three workflows, `host.json`, `parameters.json`, `local.settings.example.json`, `main.bicep` and `deploy.sh`, `.vscode/mcp.json`, test scripts; not deployed yet | 🔄 |
| Identity (Part 5) | `src/identity/external-id/register-apps.sh` | ✅ |
| Copilot Studio | Four connector definitions, `agent-instructions.md` | 🔄 |
| Governance (Part 7) | DLP URL patterns script, `pac` export/import script, deployment settings, Agent 365 hunting query | ✅ |
| Contract tests (Parts 6, 7) | `Test-McpToolContract.ps1`, `check-tool-contract.js`, protocol examples; `contract-test.yml` runs the PowerShell test against the C# server on pushes to `main`/`dev` and on PRs | ✅ |
| Order Management API | `src/order-api/`: ASP.NET Core minimal API with Entra auth for managed identities, `data/seed.json`, full OpenAPI, Dockerfile, register and deploy scripts; tested locally, not deployed yet | ✅ |
| Shared Azure base | `src/infra/base.bicep` and `deploy-base.sh`: Log Analytics, Application Insights, Key Vault, Container Apps environment; deploy order in `DEVELOPER.md` | ✅ |
| Agent layer | `agent-src/` with 16 skills and 1 agent, synced to `.claude/` and `.github/` by `sync.ps1`; parity check clean | ✅ |

---

## Open

### Decisions needed first

- ⬜ **Code state per part:** `src/` = Part 4 plus `variants/` for Parts 5 and 6 is in place. Keep it, or move to
  the final state on `main` with a tag per post (the research run's option A)?
- ⬜ **Demo data:** the C# server uses Part 4's set (`CU-3001`: `SO-10019`, `SO-10023`, `SO-10031`, `SO-10035`;
  `CU-3002`: `SO-10027`). Confirm it, then align Parts 2 (`SO-10099`), 3 (`SO-10024`) and 6 (`SO-10040`) to it.
- ✅ **Order Management API stack:** ASP.NET Core minimal API on .NET 10, demo data in `src/order-api/data/seed.json`.
- ⬜ **CI and Azure:** build and test only, or deploy too (OIDC, no secrets)?
- ⬜ **The one tool contract:** `src/contract/tools.json` is Part 1's version; the C# server differs in 14 places
  (no `pattern`, `minimum`, `maxLength` or `additionalProperties`; other parameter descriptions) and adds `title`
  and `annotations`. Pick one, update the other and the posts, then make the CI step "Compare tools/list with the
  contract" blocking (remove `continue-on-error`).

### Missing code

- ✅ **Order Management API, Logic Apps workflows and Bicep, `apim.bicep`, shared base:** written and checked
  locally (`dotnet build`, `az bicep build`, `bash -n`); none deployed yet.
- ⬜ **API Management forwards tool calls without a token:** the OAuth policy uses `authentication-managed-identity`
  only for the `by-identity` lookup, so with `Auth__Enabled=true` the Order Management API answers `401` to the
  forwarded `find_orders`, `get_order_status` and `create_return` calls. Add `authentication-managed-identity` for
  the backend to the policies (and the Part 3 post), or test Part 3 against the API with auth off.
- ⬜ **Verify on the first deployment:** that importing the facade names the operations `find-orders`,
  `get-order-status` and `create-return`, as `mcp-server.bicep` expects (the facade's operationIds use underscores).
- ⬜ **Order Management API container image:** `docker build` wasn't run locally (no Docker); `az containerapp up`
  builds it in Azure.
- ⬜ **Unit tests:** `src/dotnet-mcp-server/tests/AIDevMe.OrdersMcp.Tests/` for ownership ("not found" for another
  customer's order) and the 30-day return window.
- ⬜ **Copilot Studio solutions:** unpack `AIDevMeOrderMcpConnector` and `AIDevMeCustomerServiceAgent` into
  `src/copilot-studio/solutions/` once they're built in Dev.
- ⬜ **CI:** add `dotnet test`, `az bicep build` for every Bicep file and markdown lint.
- ✅ **Dependabot:** alerts and security updates on; `.github/dependabot.yml` runs monthly version updates for
  NuGet, Docker and GitHub Actions against `dev`, without major versions for NuGet and Docker. Add `src/order-api/`
  once it has a project.

### Inconsistencies between posts and repo

Fix the post or the file so they match; details in the research README.

- ⬜ Part 6 says Part 4 calls the Order Management API; Part 4 keeps the in-memory store.
- ⬜ API Management OAuth policy: Part 3 and Part 5 versions differ; keep one file, make the other an excerpt.
- ⬜ Tool contract: `part-1/01` and `part-6/02` differ; regenerate the snippets from `src/contract/tools.json`.
- ⬜ Part 1's sample responses differ from the server's (`src/tests/http/responses/`): the server returns
  camelCase fields, three order lines and a `DEMO-DHL-…` tracking number; the not-found message is longer. Paste
  the real responses into the post.
- ✅ Part 1's Learn-style connector is in `src/copilot-studio/connectors/learn-example.swagger.yaml`.
- ⬜ `host.json`: Part 2 sets the SSE-only `AllowCrossWorkerCommunication` the post says isn't needed.
- ⬜ Part 3 post: `mcp-server.bicep` now loads the policies from `../policies/` with the repo's file names (it
  pointed to files that didn't exist), and `scripts/import-api.sh` still uses `rg-aidevme-orders` and
  `./order-management-agent.yaml`. Align the post's Bicep and import commands with the repo.
- ⬜ Resource names (`rg-aidevme-mcp` / `rg-aidevme-orders`, `kv-aidevme-mcp` / `kv-aidevme-demo`) and placeholder
  names (`{{external-id-tenant-id}}` / `{{external-tenant-id}}`): pick one set and list it in the README.

### Provisioning and testing

- ⬜ Azure: resource group `rg-aidevme-mcp`, Container Apps, Standard logic app (WS1, about $175 a month), API
  Management Developer (about $48 a month). Deploy per test session and delete afterwards.
- ⬜ Entra External ID tenant, the two app registrations, a user flow, demo customers mapped to `CU-3001` and
  `CU-3002`.
- ⬜ Power Platform: `aidevme-dev`, `aidevme-test`, `aidevme-prod` with Copilot Studio; publisher prefix `cts`.
- ⬜ Run each path end to end, then fill the `[ZSOLT: …]` markers in the posts and mark each part ready in the
  README's Status column.

### Repo

- ✅ GitHub settings: branch protection on `main` (PR required, `mcp-contract` check, applies to admins, no force
  pushes), secret scanning and push protection.
- ⬜ GitHub settings: repository topics.
- ⬜ Line endings: add `.gitattributes` with LF for `*.sh` and `Dockerfile`, so scripts run on Linux.
- ✅ Agent layer: the 9 blog-only skills are removed; 16 skills remain, synced with zero drift.
- ⬜ Agent layer: `aidevme-bruno` and `aidevme-powershell-documenter` still mention the removed blog skills
  (`aidevme-blog-tags`, `-blog-categories`, `-image`, `-google-analytics`), and both target aidevme.com, not this
  repo. Remove them, or clean up the references.
- ⬜ Commit on `dev` and merge to `main`, as `AGENTS.md` asks; the first commits went straight to `main`.

---

## Decisions

Newest first.

| Date | Decision |
| --- | --- |
| 2026-11-15 | `src/dotnet-mcp-server/src/` is the Part 4 state; Parts 5 and 6 live in `variants/` as changed files only |
| 2026-11-15 | `src/contract/tools.json` is the single tool contract; changes are classed BREAKING, REVIEW or ADDITIVE |
| 2026-11-15 | The customer ID comes from the caller's identity, never a tool input; another customer's order is "not found" |
| 2026-11-15 | The `AIDevMe-Demo-Customer` header is for local testing only and never enabled in a deployment |
| 2026-11-15 | `docs/` is a read-only snapshot of the drafts' code; fixes go to the component folders |
| 2026-11-15 | License MIT; demo data and placeholders only, no secrets or tenant IDs |
| 2026-11-15 | Work on `dev`; `main` is the published branch |
