# Official sources this skill borrows from

<!-- cspell:ignore bicepparam azd -->

Purpose: record which ideas came from official Microsoft and GitHub sources, from which version, and what was
changed. They were read, not installed or copied in whole.

| Source | Path | Read at |
| --- | --- | --- |
| Bicep MCP server ([Azure/bicep](https://github.com/Azure/bicep)) | `docs/mcp-tools.md`, `src/Bicep.McpServer.Core/*Tools.cs` | commit `399a28af101749d55d53fa57e20a282775b9acbe` (2026-11-13) |
| `azure-deployment-preflight` ([github/awesome-copilot](https://github.com/github/awesome-copilot)) | `skills/azure-deployment-preflight/SKILL.md` (its `references/` were not read) | commit `8ecd5b17f02fe5fbebf35eccd1867265eded811f` (2026-11-13) |
| `update-avm-modules-in-bicep` ([github/awesome-copilot](https://github.com/github/awesome-copilot)) | `skills/update-avm-modules-in-bicep/SKILL.md` | commit `8ecd5b17f02fe5fbebf35eccd1867265eded811f` (2026-11-13) |
| `azure-prepare` ([microsoft/skills](https://github.com/microsoft/skills)) | `.github/plugins/azure-skills/skills/azure-prepare/references/recipes/bicep/`, `recipes/azd/iac-rules.md` | commit `f03ec5392f7a0f3aca12af47477e92f1edf7b44c` (2026-11-13) |

## Bicep MCP server → [mcp-setup.md](mcp-setup.md)

- **Adopted:** the tool list and names from the source code, the schema version rules, the `dnx` launch command.
- **Changed:** names are taken from the source, not the docs page, because `docs/mcp-tools.md` and Microsoft Learn
  still list older names. Explicit `apiVersion` for existing files, so schemas match the file.

## azure-deployment-preflight → [preview.md](preview.md), [validate.md](validate.md)

- **Adopted:** build before what-if; the scope-to-command table; `--validation-level Provider` with the
  `ProviderNoRbac` fallback; `azd provision --preview` for azd projects; the change-type symbols; the report
  sections; continuing past one file's errors.
- **Changed:** what-if runs only after the user confirms the exact command; the report goes in the reply, and to a
  file only when asked and without IDs; the local `get_deployment_snapshot` comes first. Why: what-if signs in to a
  real tenant, and repository rules ask before any `az` command that touches Azure.

## update-avm-modules-in-bicep → [modules.md](modules.md)

- **Adopted:** scan, look up the latest version on MCR, compare by semver, read docs for breaking changes, pause for
  approval on breaking, security or behaviour changes, validate, report a table with status icons.
- **Changed:** report only by default; updating needs an explicit request and a confirmation; `list_avm_metadata`
  is the first source of versions; a snapshot before and after shows what changes. Why: repositories that quote
  their code in posts must not drift, and versions change only when asked.

## azure-prepare → [author.md](author.md), [modules.md](modules.md)

- **Adopted:** research before generating (`get_bicep_best_practices`, `list_avm_metadata`); the AVM selection order
  (pattern, resource, utility); the security requirements table.
- **Not adopted:** the `infra/` layout, `.azure/deployment-plan.md`, Dockerfile generation and the hand-off to
  `azure-validate` / `azure-deploy`. Why: this skill works in the repository's existing layout and never deploys.

## When updating

Re-read each source at its current commit, compare it with the adopted parts above, and update the SHAs here. Re-check
the MCP tool names in [mcp-setup.md](mcp-setup.md) and the `allowed-tools` list in `SKILL.md` at the same time.
