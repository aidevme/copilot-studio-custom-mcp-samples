---
name: aidevme-terraform
metadata:
  layer: orchestration
  scope: core
  version: 1.0.0
description: |
  Terraform work, one entry point: write and change HCL in HashiCorp's style with current provider and module docs,
  validate, format and test it, pick Registry and Azure Verified Modules (AVM), refactor into modules with moved
  blocks, and run terraform plan only after confirmation. Uses HashiCorp's official Terraform MCP server (Registry
  tools) and HashiCorp's agent skills as its rules. Use when:
  (1) User asks to write, change, review or refactor Terraform (.tf, .tfvars, .tftest.hcl)
  (2) User asks to format, validate or test Terraform, or why terraform validate or a test fails
  (3) User asks which provider, resource, module or version to use, or for azurerm / azapi / AVM guidance
  (4) User asks to split a configuration into modules or rename resources without recreating them
  (5) User asks what a change would do (plan)
  Does NOT apply, destroy, import, change state, write to HCP Terraform or Terraform Enterprise, upgrade versions
  unasked, put credentials or IDs in files, or write Bicep (use aidevme-bicep).
license: MIT
allowed-tools: Bash, PowerShell, Read, Grep, Glob, Edit, Write, WebFetch, AskUserQuestion, mcp__terraform__search_provider_docs, mcp__terraform__get_provider_details, mcp__terraform__get_latest_provider_version, mcp__terraform__get_provider_capabilities, mcp__terraform__search_modules, mcp__terraform__get_module_details, mcp__terraform__get_latest_module_version, mcp__terraform__search_policies, mcp__terraform__get_policy_details
argument-hint: "[file.tf | folder]"
---

# aidevme-terraform: Terraform with the official Terraform MCP server

<!-- cspell:ignore azurerm azapi tfvars tftest tflint -->

One entry point for Terraform work. This file holds the shared rules and the routing; each workflow is in a
reference file under `references/`. Load only the reference the request needs.

## Shared rules (every reference)

- **Check the MCP server first.** Load [references/mcp-setup.md](references/mcp-setup.md) once per session. This
  skill uses only the server's public Registry tools. Without the server, say so, fetch the Registry docs instead,
  and never write resource arguments from memory.
- **Ground every resource in current docs:** `search_provider_docs` + `get_provider_details` for each resource or
  data source you add or change, at the provider version the configuration pins.
- **Never change infrastructure or state.** No `terraform apply`, `destroy`, `import`, `state` subcommands,
  `force-unlock`, `taint`, or `terraform test` in apply mode. `terraform plan` and `init` with a backend sign in
  to real accounts: run them only after the user confirms the exact command
  ([references/plan.md](references/plan.md)).
- **Keep versions as they are.** Don't change `required_version`, provider or module version constraints, or the
  lock file unless the user asks. Report newer versions; update only on request.
- **No credentials or real identifiers** in `.tf` or `.tfvars` files, prompts to tools or reports: variables with
  `sensitive = true`, environment variables, managed identity / OIDC, placeholders such as `<subscription-id>`.
  Never commit state, plan files, `.terraform/` or secret `.tfvars`.
- **Show the change before writing** when it touches more than one file, then format, validate and run the unit
  tests ([references/validate.md](references/validate.md)) before reporting it done.
- **Follow the repository's own rules** (`AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`) where they're stricter, and
  add any summary section they require.

## Routing

| Request | Load |
| --- | --- |
| Set up or check the Terraform MCP server, tool names, fallback | [references/mcp-setup.md](references/mcp-setup.md) |
| Write, change or review `.tf` / `.tfvars` (style, providers, variables, outputs) | [references/author.md](references/author.md) |
| Format, validate, lint, write or run `terraform test` | [references/validate.md](references/validate.md) |
| Choose a module, AVM for Azure, check versions, refactor into modules, `moved` blocks | [references/modules.md](references/modules.md) |
| What would this change do? `terraform plan` | [references/plan.md](references/plan.md) |
| Where these workflows came from | [references/official-skills.md](references/official-skills.md) |

### "Check this Terraform" (no specific ask)

Run in order and report one summary: `terraform fmt -check` and `terraform validate`
([validate.md](references/validate.md)), the style checklist ([author.md](references/author.md)), and provider and
module versions against the Registry ([modules.md](references/modules.md), report only). Change nothing unless the
user then asks.

## Report format

End with a short table per folder or file: result (✅ clean, ⚠️ warnings, ❌ errors) and what was changed or found.
List commands that need the user's confirmation separately, with the exact command line.
