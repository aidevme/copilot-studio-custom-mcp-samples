# Contributing

<!-- cspell:ignore AIDevMe Entra Bicep -->

Issues and pull requests are welcome. This repo holds the sample code for the aidevme.com series **Custom MCP
servers for Copilot Studio**, so every change has one extra test: a reader who copies code from a post and then
opens the repo must find the same thing.

## Before you start

- Read the `README.md` of the folder you want to change. It says which post the folder belongs to.
- For the tools you need, see [DEVELOPER.md](DEVELOPER.md).
- For a larger change, open an issue first, so we can agree on it before you write the code.

## Reporting a problem

Open an issue and include:

- the part and the folder, for example "Part 4, `src/dotnet-mcp-server/`"
- what you ran, what you expected and what happened, with the output
- whether the problem is in the repo, the post, or both

Don't paste tokens, keys or tenant IDs into an issue. Replace them with placeholders.

## Making a change

1. Fork the repo and create a branch from `dev`. `main` is the published branch.
2. Make the change in the component folder. Don't edit the extracted samples under `docs/`; they're a read-only
   snapshot of the posts.
3. Build and test it locally (see below).
4. Open a pull request against `dev` and fill in the pull request template.

### Keep the code in step with the posts

- Find the part your change belongs to: the folder README, the `# --- Part N:` comments in scripts, or the folder
  list in the pull request template. If the change makes the post's code wrong, say so in the pull request and what
  in the post must change.
- Keep package versions, API versions, the MCP protocol version (`2025-11-25`), ports, resource names and header
  names as they are, unless the change is about them.
- Dependabot opens a monthly pull request against `dev` for NuGet, Docker and GitHub Actions updates (no major
  versions for NuGet and Docker). Don't merge one without checking which posts quote the changed version, and list
  them for an update.
- `src/dotnet-mcp-server/src/` is the Part 4 state. `src/dotnet-mcp-server/variants/part-5-*` and `part-6-*` hold the later
  versions of the changed files. Don't merge them into `src/`.

### Rules every build path follows

1. **The customer ID comes from the caller's identity, never from a tool input.** No tool takes `customerId`,
   `userId` or `email`. Another customer's order returns "not found", not "forbidden".
2. **Business rules are enforced on the server.** Returns only for delivered orders, within 30 days after
   delivery.
3. **`src/contract/tools.json` is the tool contract.** Names, descriptions and input schemas stay the same on every
   path.
4. **The `AIDevMe-Demo-Customer` header is for local testing only.** Never enable it in anything meant for
   deployment.

### Tool contract changes

The Copilot Studio orchestrator chooses tools by their descriptions, so a description change is a behavior change.
Class every contract change in the pull request:

| Class | What it means | Example |
| --- | --- | --- |
| BREAKING | Agents stop working | A tool or input removed or renamed, an input made required, a type changed |
| REVIEW | Agent behavior can change | A description changed |
| ADDITIVE | Safe for existing agents | A new tool or a new optional input |

Update `src/contract/tools.json` in the same pull request. Ship breaking changes as a new tool or with a deprecation
period, not as an in-place change.

## Build and test

```sh
# C# server (Part 4)
dotnet build src/dotnet-mcp-server/src/AIDevMe.OrdersMcp
dotnet run --project src/dotnet-mcp-server/src/AIDevMe.OrdersMcp --urls http://localhost:5080

# Contract test against the running server
pwsh ./src/tests/contract/Test-McpToolContract.ps1 -Endpoint http://localhost:5080/mcp

# Compare two tools/list snapshots; exits with 1 on a breaking change
node src/tests/contract/check-tool-contract.js src/contract/tools-before.json src/contract/tools.json

# Bicep
az bicep build --file src/apim/infra/mcp-server.bicep
```

The `MCP contract test` workflow runs the contract test on every pull request. Say in the pull request what you
didn't test, for example "not deployed to Azure".

## Demo data and secrets

- **Demo data only:** AIDevMe as the fictional retailer, customers such as `CU-3001`, orders such as `SO-10023`,
  returns such as `RMA-5001`. Example hosts are placeholder `aidevme-samples.com` subdomains such as
  `orders-mcp.aidevme-samples.com`; use your own host when you deploy. No real names, tenants or other domains.
- **No secrets:** no keys, client secrets, connection strings, tokens, tenant or subscription IDs. Use placeholders
  such as `<external-tenant-id>`, and `*.example` files for local settings.

## Style

READMEs and comments use plain, short sentences, sentence-case headings and tables for reference material. Commit
messages have a short imperative subject ("Add …", "Fix …") and a body that says what changed and why.

## License

By contributing, you agree that your contribution is licensed under the [MIT License](LICENSE).
