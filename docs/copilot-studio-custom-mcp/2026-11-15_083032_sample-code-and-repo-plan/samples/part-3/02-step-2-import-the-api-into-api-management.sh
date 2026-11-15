RESOURCE_GROUP="rg-aidevme-orders"
APIM_NAME="apim-aidevme-orders"

az apim api import \
  --resource-group "$RESOURCE_GROUP" \
  --service-name "$APIM_NAME" \
  --api-id order-management-api \
  --path orders \
  --display-name "AIDevMe Order Management API" \
  --specification-format OpenApi \
  --specification-path ./order-management-agent.yaml \
  --service-url https://orders-api.aidevme.com \
  --protocols https \
  --subscription-required true
