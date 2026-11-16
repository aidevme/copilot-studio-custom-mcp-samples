#!/usr/bin/env bash
# Part 2: deploy the Standard logic app and the three workflows. Run from the repo root after the base and the
# Order Management API exist:
#   ORDER_API_BASE_URL=https://... ORDER_API_AUDIENCE=api://<order-api-client-id> ./src/logic-apps/infra/deploy.sh
# Then register the MCP server in the portal (post Step 3) and add the printed object ID to the API's allowed callers.
# The WS1 plan bills per hour. Remove it after testing:
#   az resource delete -g rg-aidevme-mcp -n asp-aidevme-logic --resource-type Microsoft.Web/serverfarms
#   (after deleting the logic app logic-aidevme-orders-mcp)
set -euo pipefail

RESOURCE_GROUP="${RESOURCE_GROUP:-rg-aidevme-mcp}"
: "${ORDER_API_BASE_URL:?Set ORDER_API_BASE_URL (deploy-containerapp.sh prints it)}"
: "${ORDER_API_AUDIENCE:?Set ORDER_API_AUDIENCE, for example api://<order-api-client-id>}"

APPI=$(az monitor app-insights component show --app appi-aidevme-mcp -g "$RESOURCE_GROUP" \
  --query connectionString -o tsv 2>/dev/null || echo "")

OUTPUTS=$(az deployment group create \
  --resource-group "$RESOURCE_GROUP" \
  --template-file src/logic-apps/infra/main.bicep \
  --parameters orderApiBaseUrl="$ORDER_API_BASE_URL" orderApiAudience="$ORDER_API_AUDIENCE" \
               appInsightsConnectionString="$APPI" \
  --query properties.outputs -o json)
LOGIC_APP=$(echo "$OUTPUTS" | python3 -c "import json,sys;print(json.load(sys.stdin)['logicAppName']['value'])")
MI_OBJECT_ID=$(echo "$OUTPUTS" | python3 -c "import json,sys;print(json.load(sys.stdin)['managedIdentityObjectId']['value'])")

# Zip the project (host.json, parameters.json and one folder per workflow) and deploy it.
ZIP="$(mktemp -d)/workflows.zip"
(cd src/logic-apps/src && zip -qr "$ZIP" host.json parameters.json find_orders get_order_status create_return)
az logicapp deployment source config-zip --name "$LOGIC_APP" --resource-group "$RESOURCE_GROUP" --src "$ZIP" -o none

echo "LOGIC_APP=$LOGIC_APP"
echo "LOGIC_APP_IDENTITY_OBJECT_ID=$MI_OBJECT_ID   # add to ALLOWED_CALLERS of the Order Management API"
