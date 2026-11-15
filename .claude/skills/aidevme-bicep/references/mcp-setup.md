# Bicep MCP server setup

<!-- cspell:ignore bicepparam dnx nuget decompile -->

Purpose: connect the official [Bicep MCP server](https://github.com/Azure/bicep/blob/main/docs/mcp-tools.md)
(NuGet package `Azure.Bicep.McpServer`, registry name `io.github.Azure/bicep`), check it's there, and know what to
do when it isn't.

Checked against `Azure/bicep` at commit `399a28a` (2026-11-13): `docs/mcp-tools.md` and the tool classes in
`src/Bicep.McpServer.Core/`. Tool names change between releases; re-check them when updating.

## Is it connected?

- Run `claude mcp list`, or check whether `mcp__bicep__get_bicep_best_practices` is available. These references
  assume the server name `bicep`, so tools are `mcp__bicep__<tool>`; with another name, use that prefix.
- In VS Code, the Bicep extension (0.40.2 or later) provides the server itself; use the tool names it lists.
- Don't run `claude mcp add` or edit MCP configuration yourself; the user does it.

## Setup (Claude Code)

Needs the .NET 10 SDK, which brings `dnx`. The server runs locally over stdio and never deploys anything.

```bash
claude mcp add bicep -- dnx -y Azure.Bicep.McpServer
```

For other clients, the same command and arguments in their MCP configuration:

```json
"bicep": { "type": "stdio", "command": "dnx", "args": ["-y", "Azure.Bicep.McpServer"] }
```

Never put MCP configuration with secrets in a repository file. This server needs none.

## Tools

All read-only (`ReadOnly = true`, `Destructive = false` in the source). Prefix: `mcp__bicep__`.

| Tool | Use it for | Reference |
| --- | --- | --- |
| `get_bicep_best_practices` | Current authoring rules; call before writing Bicep | [author.md](author.md) |
| `list_azure_resource_types` | Resource types and API versions of a provider namespace (`Microsoft.Storage`) | [author.md](author.md) |
| `get_azure_resource_type_schema` | Schema of one type; pass the file's `apiVersion` explicitly | [author.md](author.md) |
| `list_well_known_extensions`, `list_extension_resource_types`, `get_extension_resource_type_schema` | Bicep extensions such as Microsoft Graph | [author.md](author.md) |
| `list_avm_metadata` | All AVM modules: name, description, versions, docs link | [modules.md](modules.md) |
| `build_bicep`, `build_bicepparam` | Compile and return diagnostics (and the ARM JSON) | [validate.md](validate.md) |
| `format_bicep_file` | Formatted content, respecting `bicepconfig.json` | [validate.md](validate.md) |
| `get_file_references` | Modules, parameter files and other files a file depends on | [validate.md](validate.md) |
| `decompile_arm_template_file`, `decompile_arm_parameters_file` | ARM JSON to `.bicep` / `.bicepparam` (returns files to save) | [decompile.md](decompile.md) |
| `get_deployment_snapshot` | Predicted resources from a `.bicepparam` file, no deployment | [preview.md](preview.md) |

**Name differences you may see:** `docs/mcp-tools.md` at `399a28a` still lists `get_bicep_file_diagnostics`, which
the source has replaced with `build_bicep` / `build_bicepparam`. The Microsoft Learn page uses older names
(`get_az_resource_type_schema`, `list_az_resource_types_for_provider`). Use the names the connected server lists.

**Schema versions:** `get_azure_resource_type_schema` without `apiVersion` picks the newest version by date,
including preview. When working on an existing file, always pass the file's own `apiVersion`; ask before suggesting
another one.

## Without the server: Bicep CLI fallback

Say the server isn't connected and show the setup above, then use the CLI. Prefer the standalone `bicep` CLI; the
`az bicep` commands below are local and don't sign in, but if the repository's rules say to ask before any `az`
command, ask once first.

| Instead of | Run |
| --- | --- |
| `build_bicep` | `bicep build <file> --stdout` (or `az bicep build --file <file> --stdout`) |
| `build_bicepparam` | `bicep build-params <file> --stdout` |
| linter diagnostics | `bicep lint <file>` |
| `format_bicep_file` | `bicep format <file> --stdout` (write in place only when asked) |
| `decompile_arm_template_file` | `bicep decompile <file> --stdout` |
| `decompile_arm_parameters_file` | `bicep decompile-params <file> --stdout` |
| best practices, schemas, AVM list | [Bicep best practices](https://learn.microsoft.com/azure/azure-resource-manager/bicep/best-practices), the [template reference](https://learn.microsoft.com/azure/templates/), the [AVM Bicep index](https://azure.github.io/Azure-Verified-Modules/indexes/bicep/), fetched, not recalled |

`get_deployment_snapshot` has no CLI equivalent; say so and offer what-if ([preview.md](preview.md)).
