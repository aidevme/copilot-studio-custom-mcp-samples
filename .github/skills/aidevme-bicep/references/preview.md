# Preview a deployment: snapshot, what-if, preflight

<!-- cspell:ignore bicepparam azd RBAC -->

Purpose: show what a deployment would create or change, without deploying. The local snapshot needs nothing; what-if
signs in to Azure and runs only after the user confirms.

Load [mcp-setup.md](mcp-setup.md) first.

## 1. Local snapshot (no sign-in)

`get_deployment_snapshot` with the absolute path of a `.bicepparam` file returns the predicted resources, outputs
and diagnostics. Its tenant, subscription and resource group inputs are optional: leave them out or pass
placeholders; never pass real IDs. Unresolved values then show as expressions, which is fine for a preview.

Use it to list what would be deployed, check parameters resolve, and compare two versions of a template (same
parameters, both snapshots, diff the predicted resources). That comparison is how you show a refactor changes
nothing.

## 2. What-if (signs in; ask first)

Only when the user asks for what-if or a preflight check against Azure.

1. **Gather** the scope from the file's `targetScope` and, from the user, the resource group, subscription and
   location. Never read them from a file the repository commits, and never write them into one.
2. **Show the exact command** and wait for confirmation:

   | `targetScope` | Command |
   | --- | --- |
   | `resourceGroup` (default) | `az deployment group what-if --resource-group <rg> --template-file <file> --parameters <params> --validation-level Provider` |
   | `subscription` | `az deployment sub what-if --location <location> --template-file <file> --parameters <params> --validation-level Provider` |
   | `managementGroup` | `az deployment mg what-if --location <location> --management-group-id <mg> --template-file <file> --parameters <params> --validation-level Provider` |
   | `tenant` | `az deployment tenant what-if --location <location> --template-file <file> --parameters <params> --validation-level Provider` |

   For an azd project (`azure.yaml` present): `azd provision --preview`.
3. **On a permission error**, offer the same command with `--validation-level ProviderNoRbac` and note that the user
   may lack deployment permissions. Not signed in: suggest `az login`; don't sign in for them.
4. **Report** changes by type: create (`+`), delete (`-`), modify (`~`, with the changed properties), no change
   (`=`), ignore (`*`), deploy (`!`). Put deletes first.

Never run `az deployment ... create`, `--confirm-with-what-if`, or `azd up` / `azd provision` / `azd deploy` without
`--preview`. Deploying is outside this skill.

## 3. Preflight report

For "is this ready to deploy?": validate ([validate.md](validate.md)), snapshot, then what-if if the user confirms.
Report in the reply: summary (status, files, scope), commands run, issues with severity and fix, what-if results,
next steps. Write it to a file (`preflight-report.md`) only when asked, without subscription or tenant IDs, and
don't commit it.
