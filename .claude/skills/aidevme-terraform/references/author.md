# Write and change Terraform

<!-- cspell:ignore azurerm azapi tfvars hashicorp tfsec checkov tflint -->

Purpose: write new Terraform or change existing configuration in HashiCorp's style, with every resource checked
against current provider docs from the Terraform MCP server.

Load [mcp-setup.md](mcp-setup.md) first.

## Workflow

1. **Read what's there.** `terraform.tf` / `versions.tf` (`required_version`, `required_providers`), the lock file,
   `providers.tf`, variables, and how existing resources are named. Read the folder's README if there is one.
2. **Look up every resource you add or change.** `search_provider_docs` with the provider and the version the
   configuration pins (`provider_version`), then `get_provider_details` with the returned doc ID. Use only arguments
   and blocks in that doc; note deprecated ones.
3. **Prefer a module** when one fits ([modules.md](modules.md)); for Azure, AVM modules first.
4. **Show the change** when more than one file changes, then write it.
5. **Format, validate and run the unit tests** ([validate.md](validate.md)).

## Style (HashiCorp `terraform-style-guide`)

- **Files:** `terraform.tf` (versions), `providers.tf`, `main.tf`, `variables.tf` and `outputs.tf` (alphabetical),
  `locals.tf`. Follow the repository's layout when it already has one.
- **Order of generation:** provider and version constraints, data sources, resources in dependency order, outputs.
- **Formatting:** two spaces, aligned `=` for consecutive arguments; meta-arguments first (`count`, `for_each`),
  then arguments, then blocks, `lifecycle` last.
- **Names:** lowercase with underscores, singular, a descriptive noun without the resource type; `main` when there's
  only one.
- **Variables:** every one has `type` and `description`; `validation` where the values are known; `sensitive = true`
  for secrets, never a default for a secret.
- **Outputs:** every one has `description`; `sensitive = true` for secrets.
- **Multiple instances:** `for_each` over a map or set; `count` only for on/off (`count = var.enabled ? 1 : 0`).
- **Versions:** pinned with `~>`. For a new configuration, the latest provider major from
  `get_latest_provider_version`; for an existing one, keep what's pinned.
- **Never commit** `terraform.tfstate*`, `.terraform/`, `*.tfplan`, `.tfvars` with secrets. Always commit the `.tf`
  files and `.terraform.lock.hcl`.

## Azure specifics

- `azurerm` (`hashicorp/azurerm`) and `azapi` (`Azure/azapi`); `azapi` for resources or properties `azurerm` doesn't
  cover yet. Check both in the docs before choosing.
- Authentication through the environment (Azure CLI login, OIDC, managed identity); no `client_secret`,
  `subscription_id` or `tenant_id` literals in provider blocks. Use variables or `ARM_*` environment variables.
- Security defaults from Microsoft's `azure-prepare` patterns: managed identity, secrets through Key Vault data
  sources, encrypted state with locking (Azure Storage backend, configured by the user).

## Review only

When asked to review, don't edit. Run [validate.md](validate.md), go through the checklist below, and report by
severity (errors, security, style), with file, line and fix.

- [ ] `terraform fmt -check` and `terraform validate` pass
- [ ] Standard file layout
- [ ] Every variable has `type` and `description`; every output has `description`
- [ ] Names are lowercase nouns with underscores
- [ ] Versions pinned explicitly
- [ ] Secrets are `sensitive = true`; no literal credentials or IDs
- [ ] `for_each` rather than `count` for multiple instances

Optional, when installed: `tflint`, `checkov` or `tfsec`. Suggest them; don't install them unasked.
