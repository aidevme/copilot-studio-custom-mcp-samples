---
name: aidevme-bicep
metadata:
  layer: orchestration
  scope: core
  version: 1.0.0
description: |
  Azure Bicep work, one entry point: write and change .bicep and .bicepparam files from current best practices,
  resource schemas and Azure Verified Modules (AVM), validate and format them, decompile ARM JSON to Bicep, check
  AVM versions, and preview a deployment (snapshot, or what-if only after confirmation). Uses the official Bicep MCP
  server (Azure.Bicep.McpServer), with the Bicep CLI as fallback. Use when:
  (1) User asks to write, change, review or refactor a Bicep template, module or parameters file
  (2) User asks to validate, lint, build or format Bicep, or why a Bicep file doesn't compile
  (3) User asks to convert an ARM template to Bicep
  (4) User asks which AVM module to use, or whether AVM versions are current
  (5) User asks what a deployment would create or change (snapshot, what-if, preflight)
  Does NOT deploy (no az deployment create, azd up or azd provision), change API or module versions unasked, put
  tenant or subscription IDs or secrets in files, or write Terraform (use aidevme-terraform).
license: MIT
allowed-tools: Bash, PowerShell, Read, Grep, Glob, Edit, Write, WebFetch, AskUserQuestion, mcp__bicep__get_bicep_best_practices, mcp__bicep__list_azure_resource_types, mcp__bicep__get_azure_resource_type_schema, mcp__bicep__list_extension_resource_types, mcp__bicep__get_extension_resource_type_schema, mcp__bicep__list_well_known_extensions, mcp__bicep__list_avm_metadata, mcp__bicep__build_bicep, mcp__bicep__build_bicepparam, mcp__bicep__format_bicep_file, mcp__bicep__get_file_references, mcp__bicep__decompile_arm_template_file, mcp__bicep__decompile_arm_parameters_file, mcp__bicep__get_deployment_snapshot
argument-hint: "[file.bicep | file.bicepparam | folder]"
---

# aidevme-bicep: Azure Bicep with the official Bicep MCP server

<!-- cspell:ignore bicepparam bicepconfig decompile decompiles -->

One entry point for Bicep work. This file holds the shared rules and the routing; each workflow is in a reference
file under `references/`. Load only the reference the request needs.

## Shared rules (every reference)

- **Check the MCP server first.** Load [references/mcp-setup.md](references/mcp-setup.md) once per session. Without
  the server, say so, use the Bicep CLI fallback it describes, and never guess schemas or API versions from memory.
- **Ground every template in the tools,** not memory: `get_bicep_best_practices` before writing, the resource schema
  for every resource type you add or change, `list_avm_metadata` before choosing a module.
- **Never deploy.** No `az deployment ... create`, `--confirm-with-what-if`, `azd up`, `azd provision` or
  `azd deploy`. Previews that sign in to Azure (`what-if`, `azd provision --preview`) run only after the user
  confirms the exact command ([references/preview.md](references/preview.md)).
- **Keep versions as they are.** Don't change a resource API version, AVM module version, `targetScope` or a
  resource name unless the user asks. Report outdated versions; update them only on request.
- **No real identifiers or secrets** in files, prompts to tools, or reports: placeholders such as
  `<subscription-id>`, `@secure()` parameters, Key Vault references, managed identity.
- **Show the change before writing** when it touches more than one file, and validate every file you change
  ([references/validate.md](references/validate.md)) before reporting it done.
- **Follow the repository's own rules** (`AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`) where they're stricter, and
  add any summary section they require (for example a list of blog posts the change affects).

## Routing

| Request | Load |
| --- | --- |
| Set up or check the Bicep MCP server, tool names, CLI fallback | [references/mcp-setup.md](references/mcp-setup.md) |
| Write, change, review or refactor a template, module or `.bicepparam` | [references/author.md](references/author.md) |
| Validate, lint, build, format; fix compile errors and warnings | [references/validate.md](references/validate.md) |
| Pick an AVM module, check or update AVM versions | [references/modules.md](references/modules.md) |
| Convert an ARM template or parameters file to Bicep | [references/decompile.md](references/decompile.md) |
| What would this deploy? Snapshot, what-if, preflight report | [references/preview.md](references/preview.md) |
| Where these workflows came from | [references/official-skills.md](references/official-skills.md) |

### "Check this Bicep" (no specific ask)

Run in order and report one summary: diagnostics and formatting ([validate.md](references/validate.md)), AVM
versions ([modules.md](references/modules.md), report only), and a snapshot when a `.bicepparam` file exists
([preview.md](references/preview.md), local only). Change nothing unless the user then asks.

## Report format

End with a short table per file: file, result (✅ clean, ⚠️ warnings, ❌ errors), and what was changed or found.
List commands that need the user's confirmation separately, with the exact command line.
