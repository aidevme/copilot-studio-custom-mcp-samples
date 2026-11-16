// Part 3: the API Management instance that mcp-server.bicep and mcp-passthrough.bicep build on.
// Developer tier (about $48 a month, billed per hour); the Consumption tier doesn't support MCP servers.
// Provisioning takes 30 to 60 minutes.
targetScope = 'resourceGroup'

@description('Azure region for all resources.')
param location string = resourceGroup().location

@description('API Management names are global. Change it if apim-aidevme-orders is taken.')
param serviceName string = 'apim-aidevme-orders'

@description('Shown in the developer portal and used for notifications.')
param publisherEmail string

param publisherName string = 'AIDevMe demo'

@description('Base URL of the Order Management API (the backend).')
param orderApiBaseUrl string

@description('App ID URI of the Order Management API registration, for the managed identity token.')
param orderApiAppIdUri string

@description('Entra External ID tenant ID and subdomain, for validate-jwt (Parts 3 and 5). Placeholders until Part 5.')
param externalTenantId string = '<external-tenant-id>'
param externalTenantSubdomain string = '<external-tenant-subdomain>'

@description('Client ID of the "AIDevMe Orders MCP API" registration in the External ID tenant (Part 5).')
param ordersMcpApiClientId string = '<orders-mcp-api-client-id>'

@description('The one fixed customer of the demo-mode policy. Dev instance only.')
param demoCustomerId string = 'CU-3001'

var tags = {
  project: 'copilot-studio-custom-mcp-samples'
  purpose: 'demo'
  part: '3'
}

resource apim 'Microsoft.ApiManagement/service@2025-09-01-preview' = {
  name: serviceName
  location: location
  tags: tags
  sku: {
    name: 'Developer'
    capacity: 1
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    publisherEmail: publisherEmail
    publisherName: publisherName
  }
}

// Named values the policies in ../policies reference. The policies use two spellings for some of them (see
// PLAN.md), so both exist until the posts are aligned.
var namedValues = {
  'orders-api-base-url': orderApiBaseUrl
  'orders-api-app-id-uri': orderApiAppIdUri
  'orders-api-client-id': ordersMcpApiClientId
  'orders-mcp-api-client-id': ordersMcpApiClientId
  'external-id-tenant-id': externalTenantId
  'external-tenant-id': externalTenantId
  'external-id-tenant-name': externalTenantSubdomain
  'external-tenant-subdomain': externalTenantSubdomain
  'demo-customer-id': demoCustomerId
}

resource values 'Microsoft.ApiManagement/service/namedValues@2025-09-01-preview' = [for nv in items(namedValues): {
  parent: apim
  name: nv.key
  properties: {
    displayName: nv.key
    value: nv.value
    secret: false
  }
}]

// The product that issues subscription keys to agents (demo mode); mcp-server.bicep binds the MCP server to it.
resource product 'Microsoft.ApiManagement/service/products@2025-09-01-preview' = {
  parent: apim
  name: 'copilot-studio-agents'
  properties: {
    displayName: 'Copilot Studio agents'
    description: 'Subscription keys for Copilot Studio agents that call the AIDevMe MCP servers.'
    subscriptionRequired: true
    approvalRequired: false
    state: 'published'
  }
}

// The agent facade over the Order Management API. mcp-server.bicep exposes its operations as MCP tools.
resource orderApi 'Microsoft.ApiManagement/service/apis@2025-09-01-preview' = {
  parent: apim
  name: 'order-management-api'
  properties: {
    displayName: 'AIDevMe Order Management API'
    path: 'orders'
    protocols: [ 'https' ]
    serviceUrl: orderApiBaseUrl
    subscriptionRequired: true
    format: 'openapi'
    value: loadTextContent('../openapi/orders-agent-facade.yaml')
  }
}

// Every call to the Order Management API carries API Management's managed identity token.
resource orderApiPolicy 'Microsoft.ApiManagement/service/apis/policies@2025-09-01-preview' = {
  parent: orderApi
  name: 'policy'
  properties: {
    format: 'rawxml'
    value: loadTextContent('../policies/order-api-backend.xml')
  }
  dependsOn: [ values ]
}

// MCP tool calls forward the caller's subscription key to this API, so the key's product must include it.
resource orderApiInProduct 'Microsoft.ApiManagement/service/products/apis@2025-09-01-preview' = {
  parent: product
  name: orderApi.name
}

output serviceName string = apim.name
output gatewayUrl string = apim.properties.gatewayUrl
@description('Add this object ID to the Order Management API\'s allowed callers (ALLOWED_CALLERS).')
output managedIdentityObjectId string = apim.identity.principalId
