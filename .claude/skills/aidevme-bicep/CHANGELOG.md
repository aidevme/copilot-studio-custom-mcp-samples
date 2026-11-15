# Changelog

<!-- cspell:ignore aidevme evals Evals bicepparam decompile azd -->
<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->

All notable changes to the **aidevme-bicep** skill: Azure Bicep work through the official Bicep MCP server. Newest
first. Each entry says what changed and why it matters to you; the commit has the detail. The source is
`agent-src/skills/core/delivery/aidevme-bicep/`, synced to `.claude/skills/` and `.github/skills/`.

## 2026-11-15

### Added

- **The skill itself:** one entry point for Bicep work, grounded in the official Bicep MCP server
  (`Azure.Bicep.McpServer`) instead of memory, with the Bicep CLI as fallback. Five workflows: write or change
  templates, validate and format, choose and check Azure Verified Modules, decompile ARM JSON, and preview a
  deployment with a local snapshot or, after you confirm, what-if. It never deploys and keeps API and module
  versions as they are unless you ask.
- **References:** `mcp-setup.md` (setup command, the 14 tools by their names in the source at `399a28a`, CLI
  fallback), `author.md`, `validate.md`, `modules.md`, `decompile.md`, `preview.md`, and `official-skills.md`
  (what was adopted from `azure-deployment-preflight`, `update-avm-modules-in-bicep` and `azure-prepare`, at
  pinned commits).
- **Evals:** 6 cases: adding a resource, validating a repository, checking and updating AVM versions, a what-if
  that waits for confirmation, decompiling ARM, and working without the MCP server.
- **MIT license:** a `LICENSE` file and a `license` field in the frontmatter, so the skill keeps its license when
  it's shared on its own.
