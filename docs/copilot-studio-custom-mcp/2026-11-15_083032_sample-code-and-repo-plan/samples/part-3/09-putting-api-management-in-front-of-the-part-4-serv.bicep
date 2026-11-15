resource proxiedServer 'Microsoft.ApiManagement/service/apis@2025-09-01-preview' = {
  parent: apim
  name: 'orders-mcp-pro-code'
  properties: {
    type: 'mcp'
    displayName: 'Contoso Order Management MCP (pro-code)'
    description: 'Passthrough to the C# MCP server from Part 4.'
    path: 'orders-mcp-pro-code'
    protocols: [ 'https' ]
    serviceUrl: 'https://orders-mcp.<your-container-apps-domain>'
    subscriptionRequired: true
    mcpProperties: {
      transportType: 'streamable'
      endpoints: [
        {
          name: 'message'
          uriTemplate: '/mcp'
        }
      ]
    }
  }
}
