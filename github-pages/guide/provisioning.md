# Provision Azure

<!-- cspell:ignore aidevme apim appsettings vitepress containerapp Dataverse -->

The full, step-by-step guide is
[`docs/copilot-studio-custom-mcp/PROVISIONING.md`](https://github.com/aidevme/copilot-studio-custom-mcp-samples/blob/main/docs/copilot-studio-custom-mcp/PROVISIONING.md)
in the repository. It records a real run in a new subscription, with the errors and their fixes. This page is the
outline.

## The phases

| Phase | What | How |
| --- | --- | --- |
| 1 | A workforce tenant for the samples and a subscription with a budget | Portal, Azure CLI |
| 2 | An External ID tenant and two app registrations (Part 5) | Portal, `register-apps.sh` |
| 3 | The shared base: Log Analytics, Application Insights, Key Vault, Container Apps environment | `deploy-base.sh` |
| 4 | The connector's client secret, straight into Key Vault | Microsoft Graph |
| 5 | The Order Management API | `register-api-app.sh`, `deploy-containerapp.sh` |
| 6 | A user flow and two demo customers (Part 5) | Portal |
| 7 | Part 4: the C# MCP server | `az containerapp up` |
| 8 | Part 3: API Management | `src/apim/infra/deploy.sh` |
| 9 | Part 2: Logic Apps | `src/logic-apps/infra/deploy.sh`, portal |

## Before you start

- Keep the samples out of your production tenant.
- A new subscription may be refused in some regions, and may have a WS1 quota of 0. The guide shows how to check
  both before you deploy.
- API Management (Developer) and the Logic Apps WS1 plan bill per hour. Deploy them for a test session and delete
  them afterwards.
- Every ID, key and host goes into the local, gitignored `.env/.env`, never into the repository.
