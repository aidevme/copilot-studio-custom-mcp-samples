#!/usr/bin/env bash
# Deploy the C# MCP server to Azure Container Apps (run against a new subscription on 2026-11-15, in North Europe)
# Commands from the post; replace the placeholders before running.
# Run `az containerapp up` from src/dotnet-mcp-server/src/AIDevMe.OrdersMcp/, where the Dockerfile and .csproj are.
# If West Europe refuses new resources, set LOCATION to another region, for example northeurope.

# --- Part 4: https://aidevme.com/copilot-studio-custom-mcp-server-azure-pro-code/
RESOURCE_GROUP="rg-aidevme-mcp"
LOCATION="westeurope"
ENVIRONMENT_NAME="cae-aidevme-mcp"
APP_NAME="aidevme-orders-mcp"

az group create --name $RESOURCE_GROUP --location $LOCATION

az containerapp env create \
  --name $ENVIRONMENT_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

az containerapp up \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $ENVIRONMENT_NAME \
  --source . \
  --ingress external \
  --target-port 8080 \
  --env-vars ASPNETCORE_ENVIRONMENT=Production

# --- Part 4: https://aidevme.com/copilot-studio-custom-mcp-server-azure-pro-code/
APP_FQDN=$(az containerapp show \
  --name $APP_NAME --resource-group $RESOURCE_GROUP \
  --query "properties.configuration.ingress.fqdn" -o tsv)

az containerapp update \
  --name $APP_NAME --resource-group $RESOURCE_GROUP \
  --set-env-vars AllowedHosts=$APP_FQDN \
  --min-replicas 1 --max-replicas 1

curl https://$APP_FQDN/health
