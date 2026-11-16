# Official sources this skill borrows from

<!-- cspell:ignore hashicorp azurerm azapi tftest -->

Purpose: record which ideas came from official HashiCorp and Microsoft sources, from which version, and what was
changed. They were read, not installed or copied in whole (HashiCorp's skills are MPL-2.0).

| Source | Path | Read at |
| --- | --- | --- |
| Terraform MCP server ([hashicorp/terraform-mcp-server](https://github.com/hashicorp/terraform-mcp-server)) | `README.md`, `pkg/toolsets/registry.go`, `pkg/tools/registry/` | commit `3e38ca6943992c108b7b83c3a06b0c1b6f4902ac` (2026-11-11) |
| `terraform-style-guide` ([hashicorp/agent-skills](https://github.com/hashicorp/agent-skills)) | `plugins/terraform/skills/terraform-style-guide/SKILL.md` (its `SECURITY.md` was not read) | commit `5e30fa5c867ba6777c37e4206babfd08049c396f` (2026-11-03) |
| `terraform-test` (hashicorp/agent-skills) | `plugins/terraform/skills/terraform-test/SKILL.md` (its `references/` were not read) | same commit |
| `refactor-module` (hashicorp/agent-skills) | `plugins/terraform/skills/refactor-module/SKILL.md` | same commit |
| `azure-verified-modules` (hashicorp/agent-skills) | `plugins/terraform/skills/azure-verified-modules/SKILL.md` | same commit |
| `azure-prepare` ([microsoft/skills](https://github.com/microsoft/skills)) | `.github/plugins/azure-skills/skills/azure-prepare/references/recipes/terraform/`, `recipes/azd/iac-rules.md` | commit `f03ec5392f7a0f3aca12af47477e92f1edf7b44c` (2026-11-13) |

## Terraform MCP server → [mcp-setup.md](mcp-setup.md)

- **Adopted:** the Claude Code setup command, the `registry` toolset and its tool names and inputs, the token
  handling advice.
- **Not adopted:** the HCP Terraform / Terraform Enterprise, private registry and search/import toolsets. Why: they
  need a token and can change workspaces, runs and variables; this skill stays read-only.

## terraform-style-guide → [author.md](author.md)

- **Adopted:** the generation order, file layout, formatting, naming, variable and output rules, `for_each` over
  `count`, version pinning, what to commit, and the review checklist.
- **Changed:** existing version constraints are kept (the source says to use the latest major); latest versions are
  used only for new configurations. Why: versions change only when asked.

## terraform-test → [validate.md](validate.md)

- **Adopted:** the `tests/` layout and `*_unit_test` / `*_integration_test` naming, plan mode by default, mocks,
  `expect_failures`, the `terraform test` options.
- **Changed:** apply-mode tests run only after the user confirms, because they create real resources; `-no-cleanup`
  only on request.

## refactor-module → [modules.md](modules.md)

- **Adopted:** analysis, interface design, the module folder layout, `moved` blocks for state.
- **Not adopted:** `terraform state mv` for older versions and the module README template. Why: this skill never
  changes state; the repository decides its documentation.

## azure-verified-modules → [modules.md](modules.md)

- **Adopted:** the provider version ranges (TFFR3), no provider blocks in modules, and the pointer to the AVM
  specifications.
- **Not adopted:** the full requirement list (615 lines); it's read from the AVM specifications when a module is
  built for AVM.

## azure-prepare → [author.md](author.md), [modules.md](modules.md)

- **Adopted:** the AVM selection order (pattern, resource, utility) and the security requirements (managed identity,
  Key Vault, encrypted and locked state).
- **Not adopted:** the advice to default to azd with Terraform, the `infra/` layout and the deployment hand-off. Why:
  this skill works in the repository's layout and never deploys.

## When updating

Re-read each source at its current commit, compare it with the adopted parts above, and update the SHAs here. Re-check
the MCP tool names and inputs in [mcp-setup.md](mcp-setup.md) and the `allowed-tools` list in `SKILL.md` at the same
time.
