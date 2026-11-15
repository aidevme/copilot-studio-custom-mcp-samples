#!/usr/bin/env bash
# Register the Order Management API in your workforce tenant, so managed identities can request a token for it.
# The App ID URI is the audience the logic app (OrderApi_Audience) and API Management ({{orders-api-app-id-uri}})
# ask for. Run once after `az login` to the workforce tenant; prints the values deploy-containerapp.sh needs.
set -euo pipefail

DISPLAY_NAME="${DISPLAY_NAME:-AIDevMe Order Management API}"

APP_ID=$(az ad app list --display-name "$DISPLAY_NAME" --query "[0].appId" -o tsv)
if [ -z "$APP_ID" ]; then
  APP_ID=$(az ad app create --display-name "$DISPLAY_NAME" --sign-in-audience AzureADMyOrg --query appId -o tsv)
fi
az ad app update --id "$APP_ID" --identifier-uris "api://$APP_ID"
az ad sp show --id "$APP_ID" -o none 2>/dev/null || az ad sp create --id "$APP_ID" -o none

echo "ORDER_API_CLIENT_ID=$APP_ID"
echo "ORDER_API_AUDIENCE=api://$APP_ID"
echo "TENANT_ID=$(az account show --query tenantId -o tsv)"
