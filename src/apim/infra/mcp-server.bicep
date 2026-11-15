@description('Name of the existing API Management instance.')
param serviceName string

@description('Resource name of the imported Order Management REST API.')
param backingApiId string = 'order-management-api'

@description('Resource name and URL path of the new MCP server.')
param mcpServerId string = 'orders-mcp'

@description('Existing product that issues subscription keys for agents.')
param productId string = 'copilot-studio-agents'

@description('true: customer tokens (validate-jwt). false: demo mode with a subscription key and one fixed demo customer, dev instance only.')
param useOAuth bool = true

var tools = [
  {
    name: 'find_orders'
    operation: 'find-orders'
    description: 'Lists the signed-in customer\'s AIDevMe orders, newest first. Use it when the customer doesn\'t know the order number.'
  }
  {
    name: 'get_order_status'
    operation: 'get-order-status'
    description: 'Returns the status of one AIDevMe order by its number (for example SO-10023): order lines, carrier, tracking number and expected delivery date.'
  }
  {
    name: 'create_return'
    operation: 'create-return'
    description: 'Starts a return for one line of a delivered AIDevMe order and returns the return number (RMA). Confirm the item, quantity and reason with the customer before calling it.'
  }
]

resource apim 'Microsoft.ApiManagement/service@2025-09-01-preview' existing = {
  name: serviceName
}

resource backingApi 'Microsoft.ApiManagement/service/apis@2025-09-01-preview' existing = {
  parent: apim
  name: backingApiId
}

resource findOrdersOperation 'Microsoft.ApiManagement/service/apis/operations@2025-09-01-preview' existing = {
  parent: backingApi
  name: 'find-orders'
}

// /me/orders -> /customers/{customerId}/orders, with the ID that the MCP-scope policy set.
resource findOrdersPolicy 'Microsoft.ApiManagement/service/apis/operations/policies@2025-09-01-preview' = {
  parent: findOrdersOperation
  name: 'policy'
  properties: {
    format: 'rawxml'
    value: loadTextContent('../policies/find-orders-operation.xml')
  }
}

resource mcpServer 'Microsoft.ApiManagement/service/apis@2025-09-01-preview' = {
  parent: apim
  name: mcpServerId
  properties: {
    type: 'mcp'
    displayName: 'AIDevMe Order Management MCP'
    description: 'Look up the signed-in customer\'s AIDevMe orders, order status and tracking, and start returns.'
    path: mcpServerId
    protocols: [ 'https' ]
    subscriptionRequired: !useOAuth
  }
}

resource mcpTools 'Microsoft.ApiManagement/service/apis/tools@2025-09-01-preview' = [for tool in tools: {
  parent: mcpServer
  name: tool.name
  properties: {
    displayName: tool.name
    description: tool.description
    operationId: resourceId('Microsoft.ApiManagement/service/apis/operations', serviceName, backingApiId, tool.operation)
  }
}]

resource mcpPolicy 'Microsoft.ApiManagement/service/apis/policies@2025-09-01-preview' = {
  parent: mcpServer
  name: 'policy'
  properties: {
    format: 'rawxml'
    value: useOAuth ? loadTextContent('../policies/mcp-server-oauth.xml') : loadTextContent('../policies/mcp-server-demo.xml')
  }
}

resource product 'Microsoft.ApiManagement/service/products@2025-09-01-preview' existing = {
  parent: apim
  name: productId
}

resource productBinding 'Microsoft.ApiManagement/service/products/apis@2025-09-01-preview' = {
  parent: product
  name: mcpServerId
  dependsOn: [ mcpServer ]
}
