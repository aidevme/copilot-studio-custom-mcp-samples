// Part 2: a Standard logic app on a Workflow Service Plan (WS1), with a system-assigned managed identity that calls
// the Order Management API. The WS1 plan bills per hour (about $175 a month): delete it after a test session.
targetScope = 'resourceGroup'

@description('Azure region for all resources.')
param location string = resourceGroup().location

@description('Short name used in every resource name.')
param prefix string = 'aidevme'

@description('Base URL of the Order Management API, for example https://aidevme-orders-api.<env>.westeurope.azurecontainerapps.io.')
param orderApiBaseUrl string

@description('App ID URI of the Order Management API registration, for example api://<order-api-client-id>.')
param orderApiAudience string

@description('Application Insights connection string from base.bicep. Optional.')
param appInsightsConnectionString string = ''

var tags = {
  project: 'copilot-studio-custom-mcp-samples'
  purpose: 'demo'
  part: '2'
}
var logicAppName = 'logic-${prefix}-orders-mcp'
// Storage account names: 3 to 24 lowercase letters and digits, globally unique.
var storageName = take('st${prefix}logic${uniqueString(resourceGroup().id)}', 24)

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageName
  location: location
  tags: tags
  kind: 'StorageV2'
  sku: { name: 'Standard_LRS' }
  properties: {
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    supportsHttpsTrafficOnly: true
  }
}

resource plan 'Microsoft.Web/serverfarms@2024-04-01' = {
  name: 'asp-${prefix}-logic'
  location: location
  tags: tags
  sku: {
    name: 'WS1'
    tier: 'WorkflowStandard'
  }
  kind: 'elastic'
  properties: {
    maximumElasticWorkerCount: 1
  }
}

var storageConnection = 'DefaultEndpointsProtocol=https;AccountName=${storage.name};AccountKey=${storage.listKeys().keys[0].value};EndpointSuffix=${environment().suffixes.storage}'

resource logicApp 'Microsoft.Web/sites@2024-04-01' = {
  name: logicAppName
  location: location
  tags: tags
  kind: 'functionapp,workflowapp'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: plan.id
    httpsOnly: true
    clientAffinityEnabled: false
    siteConfig: {
      netFrameworkVersion: 'v8.0'
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      functionsRuntimeScaleMonitoringEnabled: false
      appSettings: concat([
        { name: 'APP_KIND', value: 'workflowApp' }
        { name: 'FUNCTIONS_EXTENSION_VERSION', value: '~4' }
        { name: 'FUNCTIONS_WORKER_RUNTIME', value: 'dotnet' }
        { name: 'AzureFunctionsJobHost__extensionBundle__id', value: 'Microsoft.Azure.Functions.ExtensionBundle.Workflows' }
        { name: 'AzureFunctionsJobHost__extensionBundle__version', value: '[1.*, 2.0.0)' }
        { name: 'AzureWebJobsStorage', value: storageConnection }
        { name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING', value: storageConnection }
        { name: 'WEBSITE_CONTENTSHARE', value: toLower(logicAppName) }
        // Read by parameters.json: @appsetting('OrderApi_BaseUrl') and @appsetting('OrderApi_Audience').
        { name: 'OrderApi_BaseUrl', value: orderApiBaseUrl }
        { name: 'OrderApi_Audience', value: orderApiAudience }
      ], empty(appInsightsConnectionString) ? [] : [
        { name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', value: appInsightsConnectionString }
      ])
    }
  }
}

output logicAppName string = logicApp.name
@description('Add this object ID to the Order Management API\'s allowed callers (ALLOWED_CALLERS).')
output managedIdentityObjectId string = logicApp.identity.principalId
