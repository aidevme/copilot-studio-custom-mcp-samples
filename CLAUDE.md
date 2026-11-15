# CLAUDE.md

The project guidance for all coding agents lives in AGENTS.md. Follow it.

@AGENTS.md

## Claude Code notes

- The shell is Windows (PowerShell, with Git Bash available). The `.sh` scripts in this repo target bash; run them
  with the Bash tool, and the `.ps1` scripts with `pwsh`.
- Don't run scripts that create or change Azure, Entra or Power Platform resources (`az`, `pac`, `deploy-*`,
  `register-apps.sh`, `import-api.sh`) without asking first. They bill or change real tenants.
- When a change affects a blog post, end your summary with a short "Post updates" list: part, section, what changes.
