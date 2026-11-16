# Changelog

<!-- cspell:ignore aidevme evals Evals azurerm azapi tftest hashicorp -->
<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->

All notable changes to the **aidevme-terraform** skill: Terraform work through HashiCorp's official Terraform MCP
server and agent skills. Newest first. Each entry says what changed and why it matters to you; the commit has the
detail. The source is `agent-src/skills/core/delivery/aidevme-terraform/`, synced to `.claude/skills/` and
`.github/skills/`.

## 2026-11-15

### Added

- **The skill itself:** one entry point for Terraform work, with every resource and module checked against current
  Registry docs from HashiCorp's Terraform MCP server (public Registry tools only, no token). Four workflows: write
  and review HCL in HashiCorp's style, format, validate and test, choose and check modules (AVM first for Azure) and
  refactor with `moved` blocks, and `terraform plan` after you confirm. It never applies, destroys, imports or
  touches state, and keeps version constraints as they are unless you ask.
- **References:** `mcp-setup.md` (setup command, the 9 Registry tools and their inputs at `3e38ca6`, fallback),
  `author.md`, `validate.md`, `modules.md`, `plan.md`, and `official-skills.md` (what was adopted from HashiCorp's
  `terraform-style-guide`, `terraform-test`, `refactor-module` and `azure-verified-modules` and Microsoft's
  `azure-prepare`, at pinned commits).
- **Evals:** 6 cases (5 should trigger, 1 should not): writing Azure Terraform, plan without apply, a version report,
  a module refactor with `moved` blocks, tests that ask before apply mode, and a Bicep request that belongs to
  `aidevme-bicep`.
- **MIT license:** a `LICENSE` file and a `license` field in the frontmatter, so the skill keeps its license when
  it's shared on its own.
