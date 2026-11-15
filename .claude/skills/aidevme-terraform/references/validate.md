# Format, validate and test Terraform

<!-- cspell:ignore tftest tflint -->

Purpose: check configuration locally with Terraform's own commands and the built-in test framework, without signing
in to any cloud account or touching state.

## Format and validate

1. **Format:** `terraform fmt -check -recursive` to report; `terraform fmt -recursive` writes, and only for files
   changed in this task or when the user asks.
2. **Initialise without a backend:** `terraform init -backend=false` (downloads providers and modules, no state, no
   sign-in). Don't change `.terraform.lock.hcl` unless the user asked for a version change; if `init` wants to, stop
   and report.
3. **Validate:** `terraform validate` (add `-json` to parse the diagnostics). Report per folder: errors first, with
   file and line.
4. **Lint (optional):** `tflint` when it's installed and configured in the repository.
5. **Fix only when asked**, or when the errors come from your own change; then repeat 1–3.

Terraform not installed: say so and continue with the review checklist in [author.md](author.md).

## Write tests (HashiCorp `terraform-test`)

- Files in `tests/`, named `*_unit_test.tftest.hcl` for plan mode and `*_integration_test.tftest.hcl` for apply mode.
- **Default to `command = plan`** in every `run` block. Use `mock_provider` (Terraform 1.7+) so unit tests need no
  credentials.
- One scenario per `run` block with a descriptive name; `assert` blocks with specific `error_message`s; negative tests
  with `expect_failures` for validation rules.
- Module sources in tests: local paths and Registry modules only.

## Run tests

- `terraform test` runs every test. Before running, check the files: if any `run` block uses `command = apply` (or no
  `command`, which means apply), it creates and destroys real resources. Then **ask first**, or run only the unit
  tests: `terraform test -filter=<file>` per `*_unit_test.tftest.hcl` file.
- `-verbose` for detail on a failure. Never use `-no-cleanup` unless the user asks.
- Report each run block: pass or fail, and the failing assertion's message.
