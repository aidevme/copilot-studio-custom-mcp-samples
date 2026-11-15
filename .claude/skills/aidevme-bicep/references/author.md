# Write and change Bicep

<!-- cspell:ignore bicepparam bicepconfig keyvault -->

Purpose: write a new template, module or `.bicepparam` file, or change an existing one, grounded in the Bicep MCP
server's best practices and resource schemas.

Load [mcp-setup.md](mcp-setup.md) first.

## Workflow

1. **Read what's there.** The file, its `bicepconfig.json`, and `get_file_references` to find the modules and
   parameter files it uses. Note the `targetScope`, every resource type with its `apiVersion`, and naming patterns.
   Read the folder's README if the repository has one.
2. **Load the rules.** Call `get_bicep_best_practices` once per session and apply it. Where the repository's
   existing files follow a different convention, keep the repository's and mention the difference.
3. **Get the schema for every resource you add or change.** `get_azure_resource_type_schema` with the type and the
   `apiVersion` the file already uses. For a new resource, `list_azure_resource_types` for the namespace, then take
   the newest **stable** version (`includePreview: false`) and say which one you chose. Use only properties that are
   in the schema.
4. **Prefer an AVM module** for a new resource when one fits ([modules.md](modules.md)); write a plain `resource`
   when the repository doesn't use AVM or the user asks for it.
5. **Show the change** (a diff or the new file) when more than one file changes, then write it.
6. **Validate** every changed file ([validate.md](validate.md)) and fix what you introduced.

## Rules for the code

- Parameters: `@description` on every parameter and output; `@secure()` for secrets, never a default value for a
  secure parameter; `@allowed` / `@minLength` where the values are known.
- Names: `uniqueString(resourceGroup().id)` style tokens instead of hardcoded globally unique names; no
  environment names or IDs baked in.
- Security defaults from Microsoft's `azure-prepare` patterns: managed identity, HTTPS only, TLS 1.2 or later, no
  public blob access, secrets through Key Vault references, never in outputs.
- Use `existing` resources and `parent` / symbolic references instead of string-built resource IDs.
- `.bicepparam` files hold placeholders (`'<location>'`, `'<external-tenant-id>'`) or `readEnvironmentVariable()`,
  never real tenant, subscription or object IDs.
- Comments only where the reason isn't obvious; keep any section markers the repository uses (for example
  `// --- Part N:` comments that tie code to a post).

## Review only

When asked to review, don't edit. Run [validate.md](validate.md), compare against `get_bicep_best_practices` and the
schemas, and report findings by severity: errors, security, best practice, style. Give the line and the fix for
each.
