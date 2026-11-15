# Terraform MCP server setup

<!-- cspell:ignore hashicorp TFE toolsets toolset azurerm -->

Purpose: connect HashiCorp's official [Terraform MCP server](https://github.com/hashicorp/terraform-mcp-server),
check it's there, and know what to do when it isn't.

Checked against `hashicorp/terraform-mcp-server` at commit `3e38ca6` (2026-11-11): `README.md`,
`pkg/toolsets/registry.go` and `pkg/tools/registry/`. Tool names change between releases; re-check them when
updating.

## Is it connected?

- Run `claude mcp list`, or check whether `mcp__terraform__search_provider_docs` is available. These references
  assume the server name `terraform`, so tools are `mcp__terraform__<tool>`; with another name, use that prefix.
- Don't run `claude mcp add` or edit MCP configuration yourself; the user does it.

## Setup (Claude Code): public Registry only (default)

Needs Docker. This is HashiCorp's documented command; without a token, the server's default `registry` toolset is
the only one with working tools, which is all this skill uses.

```bash
claude mcp add terraform -s user -t stdio -- docker run -i --rm hashicorp/terraform-mcp-server
```

Pin an image tag (`hashicorp/terraform-mcp-server:<version>`) if you want the same server every time.

## HCP Terraform or Terraform Enterprise (not used by this skill)

The server can also manage HCP Terraform / Terraform Enterprise workspaces, runs, variables and state when started
with `TFE_ADDRESS` and `TFE_TOKEN` (and `ENABLE_TF_OPERATIONS=true` for destructive tools). This skill doesn't use
those tools and they aren't in its `allowed-tools`. If the user sets it up anyway:

- The token goes in the user's own MCP configuration or environment, never in a repository file (`.mcp.json`,
  `.vscode/mcp.json`, a committed `.env`).
- Suggest `--toolsets=registry` (or `--tools=...`) on the server so only the Registry tools are exposed.

## Tools this skill uses

Toolset `registry`, all read-only. Prefix: `mcp__terraform__`.

| Tool | Inputs | Use it for | Reference |
| --- | --- | --- | --- |
| `search_provider_docs` | `provider_namespace`, `provider_name`, `service_slug`, `provider_document_type`, `provider_version` | Find the doc ID for a resource, data source, guide or function | [author.md](author.md) |
| `get_provider_details` | `provider_doc_id` | Full doc for one resource or data source | [author.md](author.md) |
| `get_provider_capabilities` | `namespace`, `name`, `version` | What a provider offers (resources, data sources, functions) | [author.md](author.md) |
| `get_latest_provider_version` | `namespace`, `name` | Newest provider version | [modules.md](modules.md) |
| `search_modules` | `module_query`, `current_offset` | Find a module and its `module_id` | [modules.md](modules.md) |
| `get_module_details` | `module_id` | Inputs, outputs, examples of one module | [modules.md](modules.md) |
| `get_latest_module_version` | `module_publisher`, `module_name`, `module_provider` | Newest module version | [modules.md](modules.md) |
| `search_policies`, `get_policy_details` | `policy_query` / `terraform_policy_id` | Sentinel and policy libraries in the Registry | [author.md](author.md) |

For Azure: `provider_namespace: hashicorp`, `provider_name: azurerm`; or `Azure` / `azapi`.

## Without the server

Say the server isn't connected and show the setup above. Then fetch the docs (WebFetch) instead of recalling them:

- Provider docs: `https://registry.terraform.io/providers/<namespace>/<name>/<version>/docs/resources/<resource>`
- Module docs: `https://registry.terraform.io/modules/<publisher>/<name>/<provider>/latest`
- AVM Terraform index: `https://azure.github.io/Azure-Verified-Modules/indexes/terraform/`

The local commands in [validate.md](validate.md) work without the server.
