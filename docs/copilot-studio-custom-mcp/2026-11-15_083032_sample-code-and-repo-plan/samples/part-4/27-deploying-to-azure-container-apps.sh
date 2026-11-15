RESOURCE_GROUP="rg-contoso-mcp"
LOCATION="westeurope"
ENVIRONMENT_NAME="cae-contoso-mcp"
APP_NAME="contoso-orders-mcp"

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
