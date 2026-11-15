# Setup: Google Analytics MCP server for Claude Code

<!-- cspell:ignore pipx gcloud aidevme analyticsadmin analyticsdata -->

Source: [googleanalytics/google-analytics-mcp](https://github.com/googleanalytics/google-analytics-mcp)
(experimental, Apache-2.0). Checked against v0.7.0 (`25cf926`, 2026-10-21).

The server runs locally over stdio (`pipx run analytics-mcp`) and uses **Application Default Credentials
(ADC)** with the read-only scope `https://www.googleapis.com/auth/analytics.readonly`.

> **Important:** credentials stay on your machine. Never commit the ADC JSON, an OAuth client secret file or a
> `.env` file. The repo's `.gitignore` excludes them, and `.mcp.json` only references environment variables.

## 1. Prerequisites

- Python 3.10+ and [pipx](https://pipx.pypa.io/stable/#install-pipx) (`python -m pip install --user pipx`,
  then `python -m pipx ensurepath`).
- The [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) (`gcloud`).
- A Google Cloud project you can configure, and a Google account with at least **Viewer** access to the
  aidevme.com GA4 property.

## 2. Enable both APIs

In the Google Cloud project, enable:

- [Google Analytics Admin API](https://console.cloud.google.com/apis/library/analyticsadmin.googleapis.com)
  (`analyticsadmin.googleapis.com`) — account, property and custom-definition tools.
- [Google Analytics Data API](https://console.cloud.google.com/apis/library/analyticsdata.googleapis.com)
  (`analyticsdata.googleapis.com`) — reports, funnels, realtime.

```shell
gcloud services enable analyticsadmin.googleapis.com analyticsdata.googleapis.com --project=YOUR_PROJECT_ID
```

Symptom if skipped: `SERVICE_DISABLED` / "API has not been used in project … or it is disabled".

## 3. Create an OAuth client (for user credentials)

1. Google Cloud console → **APIs & Services → OAuth consent screen**: configure it (External or Internal;
   add yourself as a test user if the app is in testing).
2. **APIs & Services → Credentials → Create credentials → OAuth client ID** → application type
   **Desktop app**.
3. Download the client JSON to a path **outside the repository**, for example `~/.config/gcloud/aidevme-ga-client.json`.

See [Manage OAuth clients](https://support.google.com/cloud/answer/15549257).

## 4. Create Application Default Credentials

Pick one. Both include the Analytics read-only and cloud-platform scopes.

**A. User credentials with your OAuth client**

```shell
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/analytics.readonly,https://www.googleapis.com/auth/cloud-platform \
  --client-id-file=PATH_TO_CLIENT_JSON
```

**B. Service-account impersonation** (the service account's email must be added as a Viewer on the GA4
property; your user needs `roles/iam.serviceAccountTokenCreator` on it)

```shell
gcloud auth application-default login \
  --impersonate-service-account=SERVICE_ACCOUNT_EMAIL \
  --scopes=https://www.googleapis.com/auth/analytics.readonly,https://www.googleapis.com/auth/cloud-platform
```

`gcloud` prints `Credentials saved to file: [PATH_TO_CREDENTIALS_JSON]`. Copy that path for step 5.

## 5. Set the environment variables locally (not committed)

The project `.mcp.json` reads these from your environment:

| Variable | Value | Notes |
| --- | --- | --- |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path from step 4 | Required |
| `GOOGLE_PROJECT_ID` | Your Cloud project ID | Used in the upstream README's config examples |
| `GOOGLE_CLOUD_PROJECT` | Same project ID | The variable google-auth itself reads for the project; the upstream README recommends setting it |

**bash / zsh** — add to `~/.bashrc` or `~/.zshrc`:

```shell
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/gcloud/application_default_credentials.json"
export GOOGLE_PROJECT_ID="your-project-id"
export GOOGLE_CLOUD_PROJECT="$GOOGLE_PROJECT_ID"
```

**PowerShell** — add to `$PROFILE`, or set them as user environment variables:

```powershell
[Environment]::SetEnvironmentVariable("GOOGLE_APPLICATION_CREDENTIALS", "$env:APPDATA\gcloud\application_default_credentials.json", "User")
[Environment]::SetEnvironmentVariable("GOOGLE_PROJECT_ID", "your-project-id", "User")
[Environment]::SetEnvironmentVariable("GOOGLE_CLOUD_PROJECT", "your-project-id", "User")
```

Restart the terminal (and VS Code) so Claude Code inherits them.

## 6. How the project `.mcp.json` is picked up

The repository root contains a **project-scoped** `.mcp.json` that registers the server:

```json
{
  "mcpServers": {
    "analytics-mcp": {
      "command": "pipx",
      "args": ["run", "analytics-mcp"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "${GOOGLE_APPLICATION_CREDENTIALS}",
        "GOOGLE_PROJECT_ID": "${GOOGLE_PROJECT_ID}",
        "GOOGLE_CLOUD_PROJECT": "${GOOGLE_CLOUD_PROJECT:-}"
      }
    }
  }
}
```

- Claude Code expands `${VAR}` from your environment when it starts the server; `${VAR:-}` falls back to
  empty. An unset `${VAR}` without a default is reported as a configuration error.
- The first time you open the repo, Claude Code asks you to **approve** the project MCP server. Approve
  `analytics-mcp`. To review or reset that choice later, run `claude mcp reset-project-choices`.
- Alternative: register it only for yourself with
  `claude mcp add analytics-mcp --scope user -e GOOGLE_APPLICATION_CREDENTIALS=… -e GOOGLE_PROJECT_ID=… -- pipx run analytics-mcp`.
  A user-scoped server with the same name takes precedence over the project one.

## 7. Verify with `/mcp`

1. Start Claude Code in the repository and run `/mcp`.
2. `analytics-mcp` should show **connected** with its tools (`get_account_summaries`, `run_report`, …).
3. Ask: *"List my Google Analytics properties."* The skill should call `get_account_summaries` and show
   aidevme.com.

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `analytics-mcp` missing or **failed** in `/mcp` | `pipx` not on PATH (run `pipx --version`), or env vars not set in the shell that launched Claude Code |
| `DefaultCredentialsError` / "Could not automatically determine credentials" | `GOOGLE_APPLICATION_CREDENTIALS` path wrong or unset; rerun step 4 |
| `Request had insufficient authentication scopes` | ADC was created without `analytics.readonly`; rerun step 4 with `--scopes` |
| `SERVICE_DISABLED` | Enable both APIs (step 2) in the project used for quota |
| `PERMISSION_DENIED` on the property | The Google account / service account isn't a user on the GA4 property; add it as Viewer in GA4 Admin → Property access management |
| `invalid_grant` / token expired | Rerun `gcloud auth application-default login …` |
| Quota project warnings | `gcloud auth application-default set-quota-project YOUR_PROJECT_ID` |
