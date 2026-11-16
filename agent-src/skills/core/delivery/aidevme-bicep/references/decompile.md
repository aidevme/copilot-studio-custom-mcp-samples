# Convert ARM JSON to Bicep

<!-- cspell:ignore bicepparam decompile decompiled decompiler -->

Purpose: turn an ARM template (`.json`, `.jsonc`, `.arm`) into `.bicep`, and an ARM parameters file into
`.bicepparam`, then clean up what the decompiler leaves behind.

Load [mcp-setup.md](mcp-setup.md) first.

## Workflow

1. **Decompile.** `decompile_arm_template_file` (or `decompile_arm_parameters_file`) with the absolute path. The tool
   returns the generated files; it doesn't write them.
2. **Choose where they go.** Next to the source with the same base name, unless the user says otherwise. Don't
   overwrite an existing `.bicep` file without asking. Keep the ARM file unless the user asks to remove it.
3. **Save, then build** the result ([validate.md](validate.md)). Decompiled code often has warnings; list them.
4. **Clean up when asked:** readable symbolic names instead of generated ones, `parent` instead of string-built
   names, `existing` resources instead of `resourceId()` strings, parameter decorators, and the best practices from
   `get_bicep_best_practices`. Keep the API versions the ARM template used.
5. **Check it's equivalent.** With a parameters file, compare `get_deployment_snapshot` of the cleaned-up Bicep with
   one of the plain decompiled output ([preview.md](preview.md)); report any difference in predicted resources.

The decompiler can't always convert every expression; it says so in diagnostics. Report those lines instead of
guessing a translation.
