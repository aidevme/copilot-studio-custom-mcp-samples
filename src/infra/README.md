# infra

The shared Azure base for every build path, in one resource group so one delete removes the whole demo.

| Resource | Name | Used by |
| --- | --- | --- |
| Resource group | `rg-aidevme-mcp` | Everything |
| Log Analytics workspace | `log-aidevme-mcp` | Container Apps logs, Application Insights |
| Application Insights | `appi-aidevme-mcp` | Telemetry for the logic app and the servers |
| Key Vault (RBAC) | `kv-aidevme-mcp` | The connector client secret (Part 5) |
| Container Apps environment | `cae-aidevme-mcp` | The Order Management API and the Part 4 C# server |

```sh
./src/infra/deploy-base.sh          # from the repo root, after az login
az group delete --name rg-aidevme-mcp --yes   # when you're done
```

Key Vault and API Management names are global; pass another name if one is taken. The deploy order for the whole
demo is in [DEVELOPER.md](../../DEVELOPER.md#deploy-to-azure).
