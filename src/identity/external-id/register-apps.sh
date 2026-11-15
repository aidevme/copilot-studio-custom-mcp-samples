#!/usr/bin/env bash
# Register the Contoso Orders MCP API and connector apps in the External ID tenant
# Commands from the post; replace the placeholders before running.

# --- Part 5: https://aidevme.com/copilot-studio-custom-mcp-server-security-oauth-entra-id/
# Azure CLI 2.87.0, Bash (Azure Cloud Shell has uuidgen). Not run against a tenant.
az login --tenant "<external-tenant-id>" --allow-no-subscriptions

# 1. API app: the MCP server as a resource, with v2 access tokens
API_APP_ID=$(az ad app create \
  --display-name "Contoso Orders MCP API" \
  --sign-in-audience AzureADMyOrg \
  --requested-access-token-version 2 \
  --query appId -o tsv)
API_OBJECT_ID=$(az ad app show --id "$API_APP_ID" --query id -o tsv)
az ad app update --id "$API_APP_ID" --identifier-uris "api://$API_APP_ID"

# 2. Two delegated scopes: reading orders and starting returns
READ_ID=$(uuidgen); RETURN_ID=$(uuidgen)
cat > scopes.json <<EOF
{
  "api": {
    "oauth2PermissionScopes": [
      {
        "id": "$READ_ID", "value": "Orders.Read", "type": "Admin", "isEnabled": true,
        "adminConsentDisplayName": "Read the customer's Contoso orders",
        "adminConsentDescription": "Lets the agent list and read the signed-in customer's orders."
      },
      {
        "id": "$RETURN_ID", "value": "Returns.Create", "type": "Admin", "isEnabled": true,
        "adminConsentDisplayName": "Start returns for the customer",
        "adminConsentDescription": "Lets the agent start a return on the signed-in customer's delivered orders."
      }
    ]
  }
}
EOF
az rest --method PATCH \
  --uri "https://graph.microsoft.com/v1.0/applications/$API_OBJECT_ID" \
  --headers "Content-Type=application/json" \
  --body @scopes.json
az ad sp create --id "$API_APP_ID"

# 3. Connector app: the client that Copilot Studio uses
CONNECTOR_APP_ID=$(az ad app create \
  --display-name "Contoso Orders MCP Connector" \
  --sign-in-audience AzureADMyOrg \
  --query appId -o tsv)
az ad sp create --id "$CONNECTOR_APP_ID"
az ad app permission add --id "$CONNECTOR_APP_ID" --api "$API_APP_ID" \
  --api-permissions "$READ_ID=Scope" "$RETURN_ID=Scope"
az ad app permission admin-consent --id "$CONNECTOR_APP_ID"   # customers can't consent in external tenants

# 4. Client secret straight into Key Vault (Key Vault lives in your Azure subscription's tenant)
SECRET=$(az ad app credential reset --id "$CONNECTOR_APP_ID" --append \
           --display-name "copilot-studio" --years 1 --query password -o tsv)
az login --tenant "<workforce-tenant-id>"
az keyvault secret set --vault-name "kv-contoso-mcp" --name "orders-connector-secret" --value "$SECRET" -o none
unset SECRET

# 5. After the wizard shows the callback URL (back in the external tenant):
# az ad app update --id "$CONNECTOR_APP_ID" --web-redirect-uris "<callback URL from Copilot Studio>"
