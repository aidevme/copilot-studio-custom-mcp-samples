# Azure Verified Modules (AVM) for Bicep

<!-- cspell:ignore bicepparam mcr semver -->

Purpose: choose an AVM module for a resource, and check (and, when asked, update) the AVM module versions a file
uses.

Load [mcp-setup.md](mcp-setup.md) first.

## Choose a module

1. Call `list_avm_metadata` and filter by the resource or pattern you need.
2. Prefer in this order (Microsoft `azure-prepare`, `iac-rules.md`): **pattern** modules (`avm/ptn/...`), then
   **resource** modules (`avm/res/...`), then **utility** modules (`avm/utl/...`). Use a non-AVM module or a plain
   `resource` only when no AVM module fits, and say why.
3. Open the module's documentation link from the metadata (WebFetch) for its parameters; use only documented ones.
4. Reference it as `br/public:avm/res/<service>/<resource>:<version>` with an explicit version, never `latest`.

## Check versions (report only)

1. **Scan** the file for `br/public:avm/...` references and their versions.
2. **Latest version** of each: the versions in `list_avm_metadata`, or the MCR tags list
   `https://mcr.microsoft.com/v2/bicep/avm/res/<service>/<resource>/tags/list` (WebFetch), sorted by semver.
3. **Compare** and report a table; change nothing:

   | Module | Current | Latest | Status | Docs |
   | --- | --- | --- | --- | --- |
   | `avm/res/storage/storage-account` | 0.9.0 | 0.14.1 | ⚠️ behind | [📖](<link>) |
   | `avm/res/key-vault/vault` | 0.11.0 | 0.11.0 | ✅ current | [📖](<link>) |

## Update versions (only when asked)

1. Name the modules and target versions and wait for confirmation.
2. For each update, read the module's changelog or docs between the two versions. **Stop and ask** before applying an
   update with removed or renamed parameters, changed defaults, or security or behaviour changes.
3. Apply the version change and any parameter changes, then validate ([validate.md](validate.md)).
4. If a `.bicepparam` file exists, compare `get_deployment_snapshot` before and after ([preview.md](preview.md)) and
   report any resource that changes.
5. Report the table with an Action column (🔄 updated, ⚠️ needs review, ❌ failed) and a short summary.

If the repository's rules pin module versions (for example because a blog post quotes them), say that the update
makes the post's code different and name what in the post must change.
