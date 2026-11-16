#!/usr/bin/env bash
# Deploy the Order Management API to the shared Container Apps environment (src/infra/deploy-base.sh first).
# Run from the repo root. Needs the values printed by register-api-app.sh:
#   ORDER_API_CLIENT_ID=<app id> TENANT_ID=<workforce tenant id> ./src/order-api/infra/deploy-containerapp.sh
# ALLOWED_CALLERS: comma-separated object IDs of the managed identities that may call the API (the logic app and
# API Management). Leave it empty for the first deploy and run the script again once they exist.
set -euo pipefail

RESOURCE_GROUP="${RESOURCE_GROUP:-rg-aidevme-mcp}"
ENVIRONMENT_NAME="${ENVIRONMENT_NAME:-cae-aidevme-mcp}"
APP_NAME="${APP_NAME:-aidevme-orders-api}"
: "${ORDER_API_CLIENT_ID:?Set ORDER_API_CLIENT_ID (register-api-app.sh prints it)}"
: "${TENANT_ID:?Set TENANT_ID (register-api-app.sh prints it)}"
ALLOWED_CALLERS="${ALLOWED_CALLERS:-}"

ENV_VARS=(
  "ASPNETCORE_ENVIRONMENT=Production"
  "Auth__Enabled=true"
  "Auth__TenantId=$TENANT_ID"
  "Auth__ClientId=$ORDER_API_CLIENT_ID"
  "Auth__Audience=api://$ORDER_API_CLIENT_ID"
)
i=0
IFS=',' read -ra CALLERS <<< "$ALLOWED_CALLERS"
for caller in "${CALLERS[@]}"; do
  ENV_VARS+=("Auth__AllowedCallerObjectIds__${i}=${caller}")
  i=$((i + 1))
done

# Builds the image from src/order-api/Dockerfile in a registry it creates, then deploys it.
az containerapp up \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --environment "$ENVIRONMENT_NAME" \
  --source src/order-api \
  --ingress external \
  --target-port 8080 \
  --env-vars "${ENV_VARS[@]}"

# One replica: the demo data lives in memory, so every caller must see the same instance.
az containerapp update --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" \
  --min-replicas 1 --max-replicas 1 -o none

FQDN=$(az containerapp show --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" \
  --query properties.configuration.ingress.fqdn -o tsv)
curl -fsS "https://$FQDN/health" && echo
echo "ORDER_API_BASE_URL=https://$FQDN"
