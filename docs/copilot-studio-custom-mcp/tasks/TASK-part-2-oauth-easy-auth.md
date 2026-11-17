<!-- cspell:ignore aidevme logicapp authsettings oauth2PermissionScopes preAuthorizedApplications addPassword keyvault MSYS PATHCONV pipefail oid Demiliani Weare uuidgen SPID urlsafe tolower AADSTS apikey wwwroot mcpservers -->

# Task: OAuth with Easy Auth for the Logic Apps MCP server (Part 2, Step 4)

Set up OAuth on the deployed Part 2 logic app, test it without Copilot Studio, and record what the post's open
`[VERIFY]` markers need. The Copilot Studio side (the OAuth 2.0 manual wizard) is in
[TASK-part-2-copilot-studio-agent.md](TASK-part-2-copilot-studio-agent.md), Part C.

| | |
| --- | --- |
| Post | [Part 2](https://aidevme.com/copilot-studio-custom-mcp-server-logic-apps/), Step 4 "OAuth with Easy Auth", Step 6 (OAuth note), Step 7 "OAuth 2.0 (manual)" |
| Learn | [Create remote MCP servers from Standard workflows: Set up OAuth authentication](https://learn.microsoft.com/azure/logic-apps/create-model-context-protocol-server-standard#set-up-oauth-authentication) |
| Builds on | [PROVISIONING.md](../PROVISIONING.md), Phase 9 (the logic app, the MCP server `AIDevMeOrderService`, key-based auth) |
| Tenant | The workforce tenant **AIDevMe Samples** (`SAMPLES_TENANT_ID`). Not the External ID tenant; see "Out of scope" |
| Time | About 45 minutes, plus 15 minutes of tests |
| Cost | None extra. Entra app registrations are free; the WS1 plan keeps billing while it runs |
| Status | 🟡 Run on 2026-11-16: steps 1 to 4, 6 and 7 done; step 5 open (see "Run log"); left in key-based mode (step 8) |

## Run log, 2026-11-16

| Step | Result |
| --- | --- |
| 1 | Workforce tenant and subscription confirmed |
| 2 | Server app, service principal, `api://<server-app-id>`, scope `user_impersonation`; `requestedAccessTokenVersion` left `null` |
| 3 | Client app with the delegated permission, admin consent (`AllPrincipals`, `user_impersonation`) on the first try; secret `logic-mcp-client-secret` in Key Vault, expires 2027-02-14 |
| 4 | Easy Auth written through `authsettingsV2` (same values as the portal table). Checked: enabled, `AllowAnonymous`, issuer, client ID, audience with trailing slash, allowed clients |
| 5 | **Not finished.** The portal stores the method in the deployed `host.json`, see "Where the MCP server keeps its settings". Removing `authentication` made the server accept **both** a Bearer token and the API key. The OAuth-only value is still unknown: set **Method → OAuth** once in the portal and read `host.json` back |
| 6.1 | Azure CLI pre-authorized; token: `ver` `1.0`, `iss` `https://sts.windows.net/<tenant>/`, `aud` `api://<server-app-id>`, `scp` `user_impersonation`. Easy Auth accepted the v1 token against the v2.0 issuer URL |
| 6.2 | See the table in 6.2 |
| 6.3 | The workflow **does** see the caller: `X-MS-CLIENT-PRINCIPAL`, `-ID`, `-NAME` and `-IDP` arrive in the trigger outputs, and `X-MS-CLIENT-PRINCIPAL-ID` equals the caller's object ID. `Authorization` and `X-MS-TOKEN-AAD-ACCESS-TOKEN` don't arrive |
| 7 | Azure CLI removed from `preAuthorizedApplications` and from Easy Auth's allowed clients; only the Copilot Studio client is left |
| 8 | Portal's `host.json` restored (`"authentication": {"type": "apikey"}`), logic app restarted. Key: `200`; Bearer token: `401` `McpServerRequestUnauthorized`; nothing: `401`. Smoke test reaches the tools |

### Where the MCP server keeps its settings

The portal writes two files into the deployed `site/wwwroot`, and the repo has neither:

| File | Content written by the portal |
| --- | --- |
| `host.json` | `extensions.workflow.McpServerEndpoints`: `{"enable": true, "authentication": {"type": "apikey"}}` for **Key-based** |
| `mcpservers.json` | `{"mcpServers": [{"name": "AIDevMeOrderService", "description": "…", "tools": [{"name": "create_return"}, {"name": "find_orders"}, {"name": "get_order_status"}]}]}` |

Read or change them through Kudu (`https://<logic-app>.scm.azurewebsites.net/api/vfs/site/wwwroot/host.json`, Bearer
token for `management.azure.com`, `If-Match: *` on `PUT`), then restart the logic app. Consequence for the repo:
`deploy.sh` zip-deploys the repo's `host.json`, which has no `McpServerEndpoints`, so a redeploy changes the
authentication mode, and may remove `mcpservers.json`. Not tested yet.

| `McpServerEndpoints.authentication` | API key | Bearer token | No credentials |
| --- | --- | --- | --- |
| `{"type": "apikey"}` (portal, Key-based) | `200` | `401` `McpServerRequestUnauthorized` | `401` |
| Missing (`{"enable": true}` only) | `200` | `200` | `401` `DirectApiInvalidAuthorizationScheme` |
| Portal, **OAuth** | Not tested | Not tested | Not tested |

## What you end up with

| Item | Name | Purpose |
| --- | --- | --- |
| Server app registration | `AIDevMe Logic Apps MCP Server` | The audience of the tokens. Exposes the scope `user_impersonation` |
| Client app registration | `AIDevMe Logic Apps MCP Copilot Studio` | The client that Copilot Studio uses in the OAuth 2.0 manual wizard. Has a client secret |
| Key Vault secret | `logic-mcp-client-secret` in `kv-aidevme-mcp` | The client secret. Never in a file or the terminal |
| Easy Auth | On `logic-aidevme-orders-mcp` | Validates the token: issuer, audience, allowed clients |
| MCP server authentication | **OAuth** on `logic-aidevme-orders-mcp` | Replaces **Key-based** for the whole logic app |

New values for `.env/.env` (add placeholders to `.env/.env.example` too):

| Variable | From step | Used by |
| --- | --- | --- |
| `LOGIC_MCP_SERVER_APP_ID` | 2.1 | Easy Auth, the scope in the Copilot Studio wizard, the test token |
| `LOGIC_MCP_SCOPE_ID` | 2.2 | The client's API permission, the pre-authorized test client |
| `LOGIC_MCP_CLIENT_APP_ID` | 3.1 | Easy Auth allowed clients, the Copilot Studio wizard |

## Before you start

- [ ] Phase 9 of PROVISIONING.md is done, and the key-based smoke test passes:
      `bash src/logic-apps/test/smoke.sh` with `MCP_URL` set.
- [ ] You can sign in to the workforce tenant as an admin who can create app registrations and grant admin consent.
- [ ] You hold **Key Vault Secrets Officer** on `kv-aidevme-mcp` (Phase 3 gives it to the deployer).
- [ ] Bash from the repo root (Git Bash on Windows), with `.env/.env` loaded:

  ```sh
  set -a; source .env/.env; set +a
  export MSYS_NO_PATHCONV=1      # Git Bash only: keeps /subscriptions/... paths intact
  RG=rg-aidevme-mcp
  LOGIC_APP=logic-aidevme-orders-mcp
  LOGIC_HOST=$(az logicapp show -n $LOGIC_APP -g $RG --query defaultHostName -o tsv | tr -d '\r')
  MCP_URL="https://$LOGIC_HOST/api/mcpservers/AIDevMeOrderService/mcp"
  ```

- [ ] Know the trade-off: authentication is set **once per logic app**. After step 5, the API key stops working, so
      `.vscode/mcp.json`, `test/smoke.sh`, `test/requests.http` and the Copilot Studio **API key** connection all fail
      until you switch back (step 8). Do Part A and Part B of the Copilot Studio task **before** this task.

## Step 1: Sign in to the workforce tenant

```sh
az login --tenant "$SAMPLES_TENANT_ID"
az account set --subscription "$AZURE_SUBSCRIPTION_ID"
[ "$(az account show --query tenantId -o tsv)" = "$SAMPLES_TENANT_ID" ] && echo "tenant OK" || echo "wrong tenant"
```

**Check:** `tenant OK`.

## Step 2: Create the server app registration

The portal steps from the post (Step 4, "The app registration") map to these commands. The result is the same:
single tenant, no redirect URI, Application ID URI `api://<server-app-id>`, scope `user_impersonation`.

### 2.1 Register the app and its service principal

```sh
LOGIC_MCP_SERVER_APP_ID=$(az ad app create --display-name "AIDevMe Logic Apps MCP Server" \
  --sign-in-audience AzureADMyOrg --query appId -o tsv)
az ad sp create --id "$LOGIC_MCP_SERVER_APP_ID" -o none
echo "LOGIC_MCP_SERVER_APP_ID=$LOGIC_MCP_SERVER_APP_ID"     # copy into .env/.env
```

Portal equivalent: **Entra ID → App registrations → New registration**, name as above, **Accounts in this
organizational directory only**, redirect URI empty, **Register**.

### 2.2 Set the Application ID URI and the scope

`user_impersonation` is the default scope that the Logic Apps MCP server expects. Another name needs an override in
`host.json` (see Learn), so keep this one.

```sh
LOGIC_MCP_SCOPE_ID=$(python -c "import uuid; print(uuid.uuid4())")   # uuidgen isn't in Git Bash
OBJ=$(az ad app show --id "$LOGIC_MCP_SERVER_APP_ID" --query id -o tsv)
BODY=$(cat <<EOF
{
  "identifierUris": ["api://$LOGIC_MCP_SERVER_APP_ID"],
  "api": {
    "oauth2PermissionScopes": [{
      "id": "$LOGIC_MCP_SCOPE_ID",
      "value": "user_impersonation",
      "type": "User",
      "isEnabled": true,
      "adminConsentDisplayName": "Access the AIDevMe order service",
      "adminConsentDescription": "Allows the app to call the AIDevMe order service MCP server on behalf of the signed-in user.",
      "userConsentDisplayName": "Access the AIDevMe order service",
      "userConsentDescription": "Allows the app to call the AIDevMe order service on your behalf."
    }]
  }
}
EOF
)
az rest --method patch --uri "https://graph.microsoft.com/v1.0/applications/$OBJ" \
  --headers "Content-Type=application/json" --body "$BODY"
echo "LOGIC_MCP_SCOPE_ID=$LOGIC_MCP_SCOPE_ID"               # copy into .env/.env
```

Portal equivalent: the app → **Expose an API → Application ID URI → Add** (keep the default `api://<app-id>`) →
**Add a scope**, name `user_impersonation`, **Admins and users**, the display names above, **Enabled**.

**Check:**

```sh
az ad app show --id "$LOGIC_MCP_SERVER_APP_ID" \
  --query "{uri:identifierUris, scopes:api.oauth2PermissionScopes[].value, tokenVersion:api.requestedAccessTokenVersion}" -o json
```

Expect `uri` `["api://<server-app-id>"]`, `scopes` `["user_impersonation"]`, and `tokenVersion` `null` (the Learn
steps leave it unset; see Troubleshooting if Easy Auth rejects the issuer).

You now have the three values the post names: the tenant ID (`SAMPLES_TENANT_ID`), the client ID
(`LOGIC_MCP_SERVER_APP_ID`) and the Application ID URI (`api://$LOGIC_MCP_SERVER_APP_ID`).

## Step 3: Create the client app registration for Copilot Studio

The Copilot Studio OAuth 2.0 manual wizard asks for a client ID and secret. They belong to a **client**
registration, not to the server registration (post, Step 7).

### 3.1 Register the client and grant it the scope

```sh
LOGIC_MCP_CLIENT_APP_ID=$(az ad app create --display-name "AIDevMe Logic Apps MCP Copilot Studio" \
  --sign-in-audience AzureADMyOrg --query appId -o tsv)
az ad sp create --id "$LOGIC_MCP_CLIENT_APP_ID" -o none
az ad app permission add --id "$LOGIC_MCP_CLIENT_APP_ID" \
  --api "$LOGIC_MCP_SERVER_APP_ID" --api-permissions "$LOGIC_MCP_SCOPE_ID=Scope"
sleep 20                                                    # let the service principals replicate
az ad app permission admin-consent --id "$LOGIC_MCP_CLIENT_APP_ID"
echo "LOGIC_MCP_CLIENT_APP_ID=$LOGIC_MCP_CLIENT_APP_ID"     # copy into .env/.env
```

If `admin-consent` fails right away, wait another 20 seconds and run it again (same as PROVISIONING.md, 2.2).

**Check:**

```sh
SPID=$(az ad sp show --id "$LOGIC_MCP_CLIENT_APP_ID" --query id -o tsv)
az rest --method get --uri "https://graph.microsoft.com/v1.0/oauth2PermissionGrants?\$filter=clientId eq '$SPID'" \
  --query "value[].{consent:consentType, scope:scope}" -o table
```

Expect one grant: `AllPrincipals`, `user_impersonation`.

### 3.2 Create the client secret, straight into Key Vault

Same pattern as PROVISIONING.md, Phase 4. The secret never reaches the terminal or a file. Set `endDateTime` to at
most 90 days from today for a demo.

```sh
set -euo pipefail
TOKEN=$(az account get-access-token --resource-type ms-graph --query accessToken -o tsv)
SECRET=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "https://graph.microsoft.com/v1.0/applications(appId='$LOGIC_MCP_CLIENT_APP_ID')/addPassword" \
  -d '{"passwordCredential":{"displayName":"copilot-studio","endDateTime":"2027-02-14T00:00:00Z"}}' \
  | python -c "import sys,json;print(json.load(sys.stdin)['secretText'])")
unset TOKEN
az keyvault secret set --vault-name kv-aidevme-mcp --name logic-mcp-client-secret --value "$SECRET" \
  --tags app=aidevme-logic-mcp-copilot-studio expires=2027-02-14 -o none
unset SECRET
set +euo pipefail
```

**Check** (metadata only):

```sh
az keyvault secret show --vault-name kv-aidevme-mcp --name logic-mcp-client-secret \
  --query "{name:name, created:attributes.created, tags:tags}" -o json
```

The redirect URI comes later: the Copilot Studio wizard shows the callback URL only after **Create** (Copilot Studio
task, Part C).

## Step 4: Set up Easy Auth on the logic app (Portal)

The portal is the documented way, and it sets all the **Additional checks** in one place.

1. Azure portal → `logic-aidevme-orders-mcp` → **Settings → Authentication → Add identity provider**.
2. **Basics** tab, **Identity provider**: **Microsoft**.
3. **App registration**: choose **Provide the details of an existing app registration**, then:

   | Field | Value |
   | --- | --- |
   | Application (client) ID | `LOGIC_MCP_SERVER_APP_ID` |
   | Client secret | Leave empty. The server registration has no secret; Easy Auth only validates tokens here |
   | Issuer URL | `https://login.microsoftonline.com/<SAMPLES_TENANT_ID>/v2.0` |
   | Allowed token audiences | `api://<LOGIC_MCP_SERVER_APP_ID>/`, **with the trailing slash** |

4. **Additional checks**:

   | Field | Value |
   | --- | --- |
   | Client application requirement | **Allow requests from specific client applications**. Add `LOGIC_MCP_CLIENT_APP_ID`. For step 6, also add the Azure CLI, `04b07795-8ddb-461a-bbee-02f9e1bf7b46`; remove it in step 7 |
   | Identity requirement | **Allow requests from any identity** for the demo. A production server would list specific identities |
   | Tenant requirement | **Allow requests from the issuer tenant** |

5. **App Service authentication settings**, **Restrict access**: **Allow unauthenticated access**. Learn requires
   this for the MCP server; the post explains why it looks wrong.
6. Select **Add**.

**Check** (no secrets in the output):

```sh
SITE="/subscriptions/$AZURE_SUBSCRIPTION_ID/resourceGroups/$RG/providers/Microsoft.Web/sites/$LOGIC_APP"
az rest --method get --uri "$SITE/config/authsettingsV2?api-version=2023-12-01" --query "{
  enabled: properties.platform.enabled,
  unauthenticated: properties.globalValidation.unauthenticatedClientAction,
  issuer: properties.identityProviders.azureActiveDirectory.registration.openIdIssuer,
  clientId: properties.identityProviders.azureActiveDirectory.registration.clientId,
  audiences: properties.identityProviders.azureActiveDirectory.validation.allowedAudiences,
  allowedClients: properties.identityProviders.azureActiveDirectory.validation.defaultAuthorizationPolicy.allowedApplications
}" -o json
```

Expect `enabled: true`, `unauthenticated: AllowAnonymous`, the issuer and client ID above, the audience with the
trailing slash, and both client IDs.

**Known issue** (post, after the Easy Auth table): some users must reapply the settings to fix sign-in errors. Kent
Weare's fix, if step 6 fails with a valid token:

```sh
az webapp auth microsoft update -g $RG -n $LOGIC_APP \
  --client-id "$LOGIC_MCP_SERVER_APP_ID" \
  --issuer "https://login.microsoftonline.com/$SAMPLES_TENANT_ID/v2.0" \
  --allowed-audiences "api://$LOGIC_MCP_SERVER_APP_ID/" --yes
```

## Step 5: Switch the MCP server to OAuth (Portal)

1. `logic-aidevme-orders-mcp` → **Agents → MCP servers → Authentication**.
2. Next to **Method**, select **Edit**, choose **OAuth**, **Save**.

The existing API key is now ignored; key-based calls fail (see step 6.2).

## Step 6: Test without Copilot Studio

### 6.1 Pre-authorize the Azure CLI as a test client

The Azure CLI can get a token for the scope only when the server app pre-authorizes it. This is for the test only;
step 7 removes it.

```sh
OBJ=$(az ad app show --id "$LOGIC_MCP_SERVER_APP_ID" --query id -o tsv)
az rest --method patch --uri "https://graph.microsoft.com/v1.0/applications/$OBJ" \
  --headers "Content-Type=application/json" \
  --body "{\"api\":{\"preAuthorizedApplications\":[{\"appId\":\"04b07795-8ddb-461a-bbee-02f9e1bf7b46\",\"delegatedPermissionIds\":[\"$LOGIC_MCP_SCOPE_ID\"]}]}}"
az login --tenant "$SAMPLES_TENANT_ID" --scope "api://$LOGIC_MCP_SERVER_APP_ID/user_impersonation"
TOKEN=$(az account get-access-token --scope "api://$LOGIC_MCP_SERVER_APP_ID/user_impersonation" --query accessToken -o tsv)
[ -n "$TOKEN" ] && echo "token OK (${#TOKEN} characters)"
```

Don't print the token. To see its claims, decode only the payload and only the claims you need:

```sh
echo "$TOKEN" | python -c "
import sys, json, base64
p = sys.stdin.read().strip().split('.')[1]
d = json.loads(base64.urlsafe_b64decode(p + '=' * (-len(p) % 4)))
print({k: d.get(k) for k in ('aud', 'iss', 'ver', 'scp', 'appid', 'azp')})"
```

Record `aud`, `iss` and `ver`. They answer the issuer question in Troubleshooting.

### 6.2 Expected results

Run each call and note the HTTP status. `H` holds the common headers.

```sh
H=(-H "Content-Type: application/json" -H "Accept: application/json, text/event-stream")
INIT='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"aidevme-test-client","version":"1.0.0"}}}'

# a) No credentials: expect 401
curl -s -o /dev/null -w "no credentials: %{http_code}\n" -X POST "$MCP_URL" "${H[@]}" -d "$INIT"

# b) The old API key: expect 401 (DirectApiInvalidAuthorizationScheme)
curl -s -w "\napi key: %{http_code}\n" -X POST "$MCP_URL" "${H[@]}" -H "X-API-KEY: $AIDEVME_MCP_KEY" -d "$INIT"

# c) Bearer token: expect 200 and an Mcp-Session-Id header
SESSION_ID=$(curl -sS -D - -o /dev/null -X POST "$MCP_URL" "${H[@]}" -H "Authorization: Bearer $TOKEN" -d "$INIT" \
  | tr -d '\r' | awk 'tolower($1) == "mcp-session-id:" { print $2 }')
echo "session id length: ${#SESSION_ID}"

A=(-H "Authorization: Bearer $TOKEN" -H "Mcp-Session-Id: $SESSION_ID" -H "MCP-Protocol-Version: 2025-06-18")
curl -sS -X POST "$MCP_URL" "${H[@]}" "${A[@]}" -d '{"jsonrpc":"2.0","method":"notifications/initialized"}'

# d) tools/list with the token: expect the three tools
curl -sS -X POST "$MCP_URL" "${H[@]}" "${A[@]}" -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' | head -c 400; echo

# e) get_order_status without the demo header: expect "not found" (no customer)
curl -sS -X POST "$MCP_URL" "${H[@]}" "${A[@]}" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"get_order_status","arguments":{"orderId":"SO-10023"}}}'; echo

# f) The same call with the demo header: expect SO-10023 (the header still works under OAuth)
curl -sS -X POST "$MCP_URL" "${H[@]}" "${A[@]}" -H "AIDevMe-Demo-Customer: CU-3001" \
  -d '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"get_order_status","arguments":{"orderId":"SO-10023"}}}'; echo
```

| Call | Expected | Result, 2026-11-16 (`authentication` removed) |
| --- | --- | --- |
| a) No credentials | `401` | ✅ `401` `DirectApiInvalidAuthorizationScheme`: "The request should have a valid authorization header with 'Bearer' scheme." |
| b) API key | `401`, `DirectApiInvalidAuthorizationScheme` | ❌ `200`, the key still works in this mode (see step 5) |
| c) Token, initialize | `200`, session ID of 32 characters, protocol `2025-06-18` | ✅ `200`, 32 characters, `2025-06-18`; `notifications/initialized` `202` |
| d) `tools/list` | `find_orders`, `get_order_status`, `create_return` | ✅ All three |
| e) No demo header | "not found" for `SO-10023` | ✅ "Order not found. Ask the customer to check the order number, or use find_orders." `find_orders`: "The customer isn't signed in…" |
| f) Demo header `CU-3001` | The order `SO-10023` | ✅ `SO-10023`, Delivered, DHL. The demo header still works with a token |

### 6.3 Find out what the workflow sees of the caller

This answers the post's main open question (Step "The user is a customer", the `[VERIFY]` on token claims; Step 4
table, "Who the user is").

1. Portal → `logic-aidevme-orders-mcp` → **Workflows → get_order_status → Run history**.
2. Open the run from call f) → **When an HTTP request is received → Show raw outputs**.
3. Look under `headers` for: `Authorization`, `X-MS-CLIENT-PRINCIPAL`, `X-MS-CLIENT-PRINCIPAL-ID`,
   `X-MS-CLIENT-PRINCIPAL-NAME`, `X-MS-TOKEN-AAD-ACCESS-TOKEN`.
4. Record which headers are present and whether `X-MS-CLIENT-PRINCIPAL-ID` equals your user's object ID
   (`az ad signed-in-user show --query id -o tsv`). Don't paste the values anywhere; note yes/no only.

| Header in trigger outputs | Present? | Matches the caller? |
| --- | --- | --- |
| `Authorization` | | — |
| `X-MS-CLIENT-PRINCIPAL` | | |
| `X-MS-CLIENT-PRINCIPAL-ID` | | |
| `X-MS-CLIENT-PRINCIPAL-NAME` | | |

If `X-MS-CLIENT-PRINCIPAL-ID` arrives, a workflow could map the caller's `oid` to a `CU-` ID, as the C# server does
in Part 5. That would be a design change for Part 2 and Part 5; write it down, don't build it in this task.

## Step 7: Clean up the test client

```sh
OBJ=$(az ad app show --id "$LOGIC_MCP_SERVER_APP_ID" --query id -o tsv)
az rest --method patch --uri "https://graph.microsoft.com/v1.0/applications/$OBJ" \
  --headers "Content-Type=application/json" --body '{"api":{"preAuthorizedApplications":[]}}'
unset TOKEN SESSION_ID
az login --tenant "$SAMPLES_TENANT_ID"     # back to a normal session
```

Portal: Easy Auth → **Edit** the Microsoft provider → remove `04b07795-8ddb-461a-bbee-02f9e1bf7b46` from **Allowed
client applications**, keep `LOGIC_MCP_CLIENT_APP_ID`.

## Step 8: Switch back to key-based (when you need the key again)

1. **Agents → MCP servers → Authentication → Method → Edit → Key-based → Save**.
2. Generate a new key if the old one expired; update `AIDEVME_MCP_KEY` in `.env/.env`.
3. Leave Easy Auth in place, or turn it off: **Authentication → Edit → App Service authentication: Disabled**.

**Check:** `bash src/logic-apps/test/smoke.sh` (with `MCP_URL` set) returns `RMA-…` again.

## Record the results

Fill these in, then update the post and PROVISIONING.md.

| Question | Post location | Answer, 2026-11-16 |
| --- | --- | --- |
| Does the token need `requestedAccessTokenVersion: 2` for the v2.0 issuer? | Step 4, Easy Auth table | No. A v1 token (`iss` `sts.windows.net`) was accepted with the issuer `https://login.microsoftonline.com/<tenant>/v2.0` |
| Does "Allow unauthenticated access" behave as the post reads it (the MCP endpoint checks the token)? | Step 4, `[VERIFY]` after the table | Yes. Easy Auth lets the request through, and the MCP endpoint answers `401` without a token |
| Do workflows receive the caller's claims or Easy Auth headers? | "The user is a customer", `[VERIFY]`; Step 4 table, "Who the user is" | Yes: `X-MS-CLIENT-PRINCIPAL`, `X-MS-CLIENT-PRINCIPAL-ID` (the caller's object ID), `-NAME`, `-IDP`. Not the token itself |
| Does the demo header still work under OAuth? | "The user is a customer" | Yes (test f) |
| Exact error text without credentials | Step 6, OAuth note | `401` `DirectApiInvalidAuthorizationScheme`, "The provided authorization token is not valid. The request should have a valid authorization header with 'Bearer' scheme." |
| Error text of a token in Key-based mode | Step 6 | `401` `McpServerRequestUnauthorized`, "The authentication credentials are not valid." |
| What does **Method → OAuth** write to `host.json`? | Step 4, Step 5 of this task | Open. Needs one portal click |

## Update the post and the repo afterwards

- **Post, Step 4 table, "Allowed token audiences":** the post writes `api://<application-ID-URI>/`. With the default
  Application ID URI that would read `api://api://…`. Change it to `<application-ID-URI>/`, for example
  `api://<server-app-id>/`.
- **Post, Step 7 table, "Scopes":** same issue: `api://<application-ID-URI>/user_impersonation` → `<application-ID-URI>/user_impersonation offline_access`.
- **Post:** replace the `[VERIFY]` markers answered above; keep the External ID one.
- **PROVISIONING.md:** add a Phase 10 "Part 2, OAuth with Easy Auth" with the steps that worked, new rows in "Values to
  record", "Final state" and "Troubleshooting", and the app registrations in "Tear down".
- **`.env/.env.example`:** add `LOGIC_MCP_SERVER_APP_ID=`, `LOGIC_MCP_SCOPE_ID=`, `LOGIC_MCP_CLIENT_APP_ID=`.

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `401` with a valid token, issuer mismatch in the Easy Auth log | v1 token (`iss` `https://sts.windows.net/<tenant>/`) against the v2.0 issuer | Set `api.requestedAccessTokenVersion` to `2` on the server app, get a new token. Record it in the post |
| `401` with a valid token, audience mismatch | Audience without the trailing slash | `api://<server-app-id>/` in **Allowed token audiences** |
| `403` with a valid token | The client isn't in **Allowed client applications** | Add the client's app ID (Copilot Studio client, or the Azure CLI for tests) |
| `401` `DirectApiInvalidAuthorizationScheme` | The MCP server still expects a key, or a key was sent under OAuth | Step 5, or send `Authorization: Bearer` |
| `AADSTS65001` (consent required) on `az account get-access-token` | The Azure CLI isn't pre-authorized | Step 6.1 |
| `AADSTS500011` (resource not found) | The Application ID URI isn't set, or a typo in the scope | Step 2.2 check |
| Sign-in errors after a correct setup | Known Easy Auth issue | `az webapp auth microsoft update` (step 4) |
| `400` "The header 'Mcp-Session-Id' is required" | No session | Initialize first, send `Mcp-Session-Id` |

## Out of scope

- **External ID as issuer.** The post's `[VERIFY]` on whether the MCP endpoint accepts the External ID tenant as
  issuer is a separate test, after this one works. It uses the Part 5 apps in `EXTERNAL_TENANT_ID`.
- **Gating the demo header.** The workflows keep reading `AIDevMe-Demo-Customer`. See "Still open" in PROVISIONING.md.

## Tear down

| What | Command |
| --- | --- |
| Client app registration | `az ad app delete --id "$LOGIC_MCP_CLIENT_APP_ID"` |
| Server app registration | `az ad app delete --id "$LOGIC_MCP_SERVER_APP_ID"` |
| Client secret | `az keyvault secret delete --vault-name kv-aidevme-mcp --name logic-mcp-client-secret` |
| Easy Auth | Deleted with the logic app; or **Authentication → Remove** the provider |
