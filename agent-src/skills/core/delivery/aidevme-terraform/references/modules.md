# Modules: choose, check versions, AVM, refactor

<!-- cspell:ignore azurerm azapi hashicorp semver -->

Purpose: pick Registry modules (Azure Verified Modules first for Azure), check provider and module versions, follow
the AVM rules when writing an Azure module, and split a configuration into modules without recreating resources.

Load [mcp-setup.md](mcp-setup.md) first.

## Choose a module

1. `search_modules` with a short query (`avm storage account`, `azure key vault`); page with `current_offset`.
2. For Azure, prefer in this order (Microsoft `azure-prepare`, `iac-rules.md`): AVM **pattern** modules
   (`Azure/avm-ptn-...`), then AVM **resource** modules (`Azure/avm-res-...`), then AVM **utility** modules. A
   non-AVM module only when none fits; say why.
3. `get_module_details` with the `module_id` for inputs, outputs and examples; use only documented inputs.
4. Pin the version with `~>` (or exact, if the repository does).

## Check versions (report only)

For each provider in `required_providers`: `get_latest_provider_version`. For each Registry module:
`get_latest_module_version`. Report and change nothing:

| Item | Constraint | Locked | Latest | Status |
| --- | --- | --- | --- | --- |
| `hashicorp/azurerm` | `~> 4.0` | 4.12.0 | 4.20.0 | ✅ within constraint |
| `Azure/avm-res-keyvault-vault/azurerm` | `0.9.0` | — | 0.10.1 | ⚠️ behind |

Updating needs an explicit request: name the targets, confirm, read the changelog between versions, stop on breaking
changes, then `terraform init -upgrade -backend=false` and [validate.md](validate.md).

## Writing an Azure module to AVM rules (HashiCorp `azure-verified-modules`)

Only when the user is building a module meant to meet AVM requirements:

- Providers: `azurerm` `>= 4.0, < 5.0` and/or `azapi` `>= 2.0, < 3.0`, declared in `required_providers` with `~>`.
- No `provider` blocks inside the module; lower snake_case everywhere; variables with `type` and `description`,
  non-nullable defaults for collections, `sensitive` only where needed.
- Read the full requirement list from the AVM module specifications
  (`https://azure.github.io/Azure-Verified-Modules/specs/module-specs/`) before reviewing against it.

## Refactor into modules (HashiCorp `refactor-module`)

1. **Analyse:** group resources by lifecycle and purpose; list what crosses the boundary (inputs, outputs).
2. **Design the interface:** typed, described variables; outputs for what callers need; no over-generic modules.
3. **Move the code** into `modules/<name>/` (`main.tf`, `variables.tf`, `outputs.tf`) and call it from the root.
4. **Keep the state:** add `moved` blocks (Terraform 1.1+) from every old address to its new one, so nothing is
   destroyed and recreated. Never run `terraform state mv`; the user's next plan applies the moves.
5. **Validate** ([validate.md](validate.md)) and, if the user confirms, run a plan ([plan.md](plan.md)): the goal is
   moves only, no create, update or destroy.
