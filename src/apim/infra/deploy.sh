#!/usr/bin/env bash
# Part 3: deploy API Management, import the agent facade and create the MCP server. Run from the repo root after the
# base and the Order Management API exist:
#   PUBLISHER_EMAIL=you@example.com ORDER_API_BASE_URL=https://... ORDER_API_CLIENT_ID=<app id> \
#     ./src/apim/infra/deploy.sh
# USE_OAUTH=false deploys the demo-mode policy (subscription key, one fixed customer) for a dev instance; the OAuth
# policy needs the External ID values from Part 5.
# The Developer tier bills per hour. Remove it after testing:
#   az apim delete -g rg-aidevme-mcp -n apim-aidevme-orders --yes
set -euo pipefail

RESOURCE_GROUP="${RESOURCE_GROUP:-rg-aidevme-mcp}"
APIM_NAME="${APIM_NAME:-apim-aidevme-orders}"
USE_OAUTH="${USE_OAUTH:-false}"
: "${PUBLISHER_EMAIL:?Set PUBLISHER_EMAIL}"
: "${ORDER_API_BASE_URL:?Set ORDER_API_BASE_URL (deploy-containerapp.sh prints it)}"
: "${ORDER_API_CLIENT_ID:?Set ORDER_API_CLIENT_ID (register-api-app.sh prints it)}"

OUTPUTS=$(az deployment group create \
  --resource-group "$RESOURCE_GROUP" \
  --template-file src/apim/infra/apim.bicep \
  --parameters serviceName="$APIM_NAME" publisherEmail="$PUBLISHER_EMAIL" \
               orderApiBaseUrl="$ORDER_API_BASE_URL" orderApiAppIdUri="api://$ORDER_API_CLIENT_ID" \
  --query properties.outputs -o json)

az deployment group create \
  --resource-group "$RESOURCE_GROUP" \
  --template-file src/apim/infra/mcp-server.bicep \
  --parameters serviceName="$APIM_NAME" useOAuth="$USE_OAUTH" -o none

echo "$OUTPUTS" | python3 -c "
import json,sys
o=json.load(sys.stdin)
print('MCP_SERVER_URL=' + o['gatewayUrl']['value'] + '/orders-mcp/mcp')
print('APIM_IDENTITY_OBJECT_ID=' + o['managedIdentityObjectId']['value'] + '   # add to ALLOWED_CALLERS of the Order Management API')"
