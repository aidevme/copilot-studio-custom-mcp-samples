APP_FQDN=$(az containerapp show \
  --name $APP_NAME --resource-group $RESOURCE_GROUP \
  --query "properties.configuration.ingress.fqdn" -o tsv)

az containerapp update \
  --name $APP_NAME --resource-group $RESOURCE_GROUP \
  --set-env-vars AllowedHosts=$APP_FQDN \
  --min-replicas 1 --max-replicas 1

curl https://$APP_FQDN/health
