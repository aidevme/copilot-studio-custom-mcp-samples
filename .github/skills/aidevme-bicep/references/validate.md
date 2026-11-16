# Validate, lint and format Bicep

<!-- cspell:ignore bicepparam bicepconfig -->

Purpose: compile Bicep and Bicep parameters files, report their diagnostics, fix what's wrong, and format them.
Local only; nothing signs in to Azure.

Load [mcp-setup.md](mcp-setup.md) first.

## Workflow

1. **Find the files.** The ones named, or every `.bicep` and `.bicepparam` under the folder. For each, call
   `get_file_references` so modules and parameter files are checked with it.
2. **Build.** `build_bicep` for `.bicep`, `build_bicepparam` for `.bicepparam` (CLI fallback in
   [mcp-setup.md](mcp-setup.md)). Collect every diagnostic: code (`BCP…` or linter rule), level, line, message,
   docs link. Don't save the compiled ARM JSON unless asked.
3. **Report** per file, errors first, then warnings, then info. Continue with the other files when one fails.
4. **Fix only when asked**, or when the errors come from your own change. One fix per diagnostic; never silence a
   rule with `#disable-next-line` or a `bicepconfig.json` change unless the user agrees, and then say why in the
   comment.
5. **Format.** `format_bicep_file` returns the formatted content; write it back only when the file was changed in
   this task or the user asks. Formatting an untouched file creates noise in the diff.
6. **Re-build** after any change and report the final state.

## Diagnostic hints

- `BCP081` (missing type metadata) usually means a preview or very new `apiVersion`: report it, don't change the
  version unasked.
- `use-recent-api-versions` warnings are information for the user, not a reason to upgrade.
- Unresolved module paths: check `get_file_references` output and the module alias in `bicepconfig.json`.
- For a diagnostic you don't recognise, follow its docs link (WebFetch) rather than guessing.

## CI

To check every Bicep file in CI, the command per file is `az bicep build --file <file>` (or `bicep build <file>`),
failing on errors. Suggest it; change workflow files only when asked.
