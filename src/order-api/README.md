# order-api

The AIDevMe Order Management API: the backend REST API that the Logic Apps workflows (Part 2) and API Management
(Part 3) call, with in-memory demo data. ASP.NET Core minimal API on .NET 10.

- `src/AIDevMe.OrderApi/`: the API
- `data/seed.json`: the demo data set, the same orders as the Part 4 C# server
- `openapi/orders-api.yaml`: the full OpenAPI 3.0 description
- `infra/`: register the API in Microsoft Entra and deploy it to Azure Container Apps
- `test/requests.http`: requests for a local run

Post: [Part 1](https://aidevme.com/copilot-studio-custom-mcp-servers-when-you-need-one/).

## Operations

| Method and path | Tool | Notes |
| --- | --- | --- |
| `GET /customers/{customerId}/orders?status=&from=&to=` | `find_orders` | Newest first; `400` for a bad filter |
| `GET /orders/{orderId}` | `get_order_status` | Includes `customerId`, so Logic Apps can check ownership |
| `POST /orders/{orderId}/returns` | `create_return` | `201` and the RMA; `422` when the return policy refuses it |
| `GET /customers/by-identity/{oid}` | — | Internal: External ID `oid` to customer ID, for API Management (Part 3) |
| `GET /health` | — | No authentication |

**Ownership.** When a gateway sends `AIDevMe-Customer-Id` (API Management) or `AIDevMe-Customer-Oid` (Part 5), the
API answers `404` for another customer's order. Without either header, it returns the order with its `customerId`
and the caller checks ownership, as the Logic Apps workflows do.

**Return policy.** Delivered orders only, within 30 days after delivery, an existing line and a quantity from 1 to
what's left to return. Each refusal is a `422` with a code (`not_delivered`, `return_window_closed`,
`line_not_found`, `invalid_quantity`, `invalid_reason`, `comment_too_long`) and a sentence the agent can show.

## Run it locally

```sh
ASPNETCORE_ENVIRONMENT=Development dotnet run --project src/order-api/src/AIDevMe.OrderApi --urls http://localhost:5090
```

`appsettings.Development.json` turns authentication off. Dates in `seed.json` are offsets from the day the API
starts, so `SO-10023` is always inside the return window and `SO-10019` always outside it.

## Authentication in Azure

Callers send a Microsoft Entra token for the API's App ID URI, requested with their managed identity: the logic
app's HTTP actions (`ManagedServiceIdentity`) and API Management (`authentication-managed-identity`). Any app in the
tenant can request such a token, so the API also accepts only the object IDs in `Auth__AllowedCallerObjectIds`.

| Setting | Value |
| --- | --- |
| `Auth__Enabled` | `true` |
| `Auth__TenantId` | Your workforce tenant ID |
| `Auth__ClientId`, `Auth__Audience` | The API registration's client ID and `api://<client-id>` |
| `Auth__AllowedCallerObjectIds__0`, `__1` | The logic app's and API Management's managed identity object IDs |
| `Customers__Identities__<oid>` | Maps a real External ID user to `CU-3001` or `CU-3002` (Part 5) |

The deploy steps are in [DEVELOPER.md](../../DEVELOPER.md#deploy-to-azure).
