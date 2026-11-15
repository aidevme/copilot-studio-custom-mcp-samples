#!/usr/bin/env bash
# Import the agent facade into API Management
# Commands from the post; replace the placeholders before running.

# --- Part 3: https://aidevme.com/copilot-studio-custom-mcp-server-api-management/
RESOURCE_GROUP="rg-contoso-orders"
APIM_NAME="apim-contoso-orders"

az apim api import \
  --resource-group "$RESOURCE_GROUP" \
  --service-name "$APIM_NAME" \
  --api-id order-management-api \
  --path orders \
  --display-name "Contoso Order Management API" \
  --specification-format OpenApi \
  --specification-path ./order-management-agent.yaml \
  --service-url https://orders-api.contoso.com \
  --protocols https \
  --subscription-required true
