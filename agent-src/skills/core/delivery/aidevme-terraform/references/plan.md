# Plan: what would this change?

<!-- cspell:ignore tfplan tfvars -->

Purpose: show what a change would do with `terraform plan`, which reads real state and signs in to real accounts.
Run only after the user confirms the exact command.

## Workflow

1. **Validate first** ([validate.md](validate.md)); don't plan a configuration that doesn't validate.
2. **Ask for what's needed:** the working directory, the workspace or backend config, the `.tfvars` file. Don't read
   credentials or IDs into the chat, and never write them into a file.
3. **Show the exact commands** and wait for confirmation:

   ```bash
   terraform init            # with the backend; asks for nothing new if already initialised
   terraform plan -input=false -lock=false [-var-file=<file>] [-out=<name>.tfplan]
   ```

   `-lock=false` keeps a read-only plan from blocking others; leave it out if the user prefers. A plan file is
   written only if the user wants one, and never committed.
4. **Report** the summary line (`Plan: X to add, Y to change, Z to destroy`) and the resources by action: **destroy
   and replace first** (`-/+`, with the attribute that forces replacement), then update (`~`), create (`+`), moves.
   For a refactor, anything other than moves is a finding.
5. **Stop there.** Never run `terraform apply`, even with a saved plan, `destroy`, `import`, `state`, `taint`,
   `untaint` or `force-unlock`. If the user wants to apply, they run it themselves.

Not signed in or no backend access: report the error and the likely fix (for Azure, `az login` or the `ARM_*`
environment variables); don't sign in for them.
