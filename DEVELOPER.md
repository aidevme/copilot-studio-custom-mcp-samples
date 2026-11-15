# Developer guide

<!-- cspell:ignore Entra Bicep aidevme westeurope containerapp apim keyvault -->

What you need to build, run and test the samples. For what the repo contains, start with [README.md](README.md).

## What you need

Not every part needs everything. Each folder's README lists its own prerequisites.

- **Local:** .NET 10 SDK, Node.js 22.19 or newer (MCP Inspector), Azure CLI with Bicep, PowerShell 7, Power
  Platform CLI (`pac`), VS Code with the Azure Logic Apps (Standard) extension.
- **Azure:** a subscription for Container Apps, a Standard logic app and an API Management instance (Developer tier
  or above; the Consumption tier doesn't support MCP servers). These resources bill per hour while they exist, so
  delete them when you're done.
- **Microsoft Entra:** an External ID tenant for customer sign-in (Part 5).
- **Power Platform:** an environment with Copilot Studio; Dev, Test and Prod environments for the ALM part (Part 7).

## Deploy to Azure

Everything goes into one resource group, `rg-aidevme-mcp`, in `westeurope`. Run the scripts from the repo root
after `az login` (Bash, for example Git Bash or the Cloud Shell). Each script prints the values the next one needs.

| Step | Script | Creates | Cost while it exists |
| --- | --- | --- | --- |
| 1 | `src/infra/deploy-base.sh` | Resource group, Log Analytics, Application Insights, Key Vault, Container Apps environment | Low |
| 2 | `src/order-api/infra/register-api-app.sh` | The "AIDevMe Order Management API" app registration in your workforce tenant | Free |
| 3 | `src/order-api/infra/deploy-containerapp.sh` | The Order Management API as a container app, one replica, plus a container registry | Low |
| 4 | `src/logic-apps/infra/deploy.sh` | Part 2: WS1 plan, storage, the Standard logic app and its three workflows | About $175 a month |
| 5 | `src/apim/infra/deploy.sh` | Part 3: API Management (Developer), the facade, named values, product and MCP server | About $48 a month |
| 6 | `src/dotnet-mcp-server/infra/deploy-containerapp.sh` | Part 4: the C# MCP server in the same environment | Low |

```sh
./src/infra/deploy-base.sh
./src/order-api/infra/register-api-app.sh                 # prints ORDER_API_CLIENT_ID and TENANT_ID
ORDER_API_CLIENT_ID=... TENANT_ID=... ./src/order-api/infra/deploy-containerapp.sh   # prints ORDER_API_BASE_URL
ORDER_API_BASE_URL=... ORDER_API_AUDIENCE=api://... ./src/logic-apps/infra/deploy.sh
PUBLISHER_EMAIL=... ORDER_API_BASE_URL=... ORDER_API_CLIENT_ID=... ./src/apim/infra/deploy.sh
```

Steps 4 and 5 print the object ID of the logic app's or API Management's managed identity. Run step 3 again with
`ALLOWED_CALLERS=<id>,<id>`, so the API accepts their tokens. Steps 4 and 5 are independent: deploy one for a test
session, then delete it. Registering the Logic Apps MCP server (Part 2, Step 3) is done in the portal.

Delete everything when you're done:

```sh
az group delete --name rg-aidevme-mcp --yes
```

Key Vault keeps a deleted vault for 7 days; purge it with `az keyvault purge --name kv-aidevme-mcp` if you want to
reuse the name sooner. The app registration from step 2 stays until you delete it in Microsoft Entra.
