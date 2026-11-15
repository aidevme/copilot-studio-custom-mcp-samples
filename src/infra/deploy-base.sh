#!/usr/bin/env bash
# Shared base: resource group, Log Analytics, Application Insights, Key Vault, Container Apps environment.
# Run from the repo root after `az login`. Creates billable resources; delete them with:
#   az group delete --name rg-aidevme-mcp --yes
set -euo pipefail

RESOURCE_GROUP="${RESOURCE_GROUP:-rg-aidevme-mcp}"
LOCATION="${LOCATION:-westeurope}"

az group create --name "$RESOURCE_GROUP" --location "$LOCATION" -o none

DEPLOYER_ID=$(az ad signed-in-user show --query id -o tsv 2>/dev/null || echo "")

az deployment group create \
  --resource-group "$RESOURCE_GROUP" \
  --template-file src/infra/base.bicep \
  --parameters deployerPrincipalId="$DEPLOYER_ID" \
  --query properties.outputs -o json
