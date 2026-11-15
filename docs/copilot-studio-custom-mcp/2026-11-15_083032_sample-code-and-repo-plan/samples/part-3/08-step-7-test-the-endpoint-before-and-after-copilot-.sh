MCP_URL="https://apim-contoso-orders.azure-api.net/orders-mcp/mcp"   # copy from the MCP Servers list
KEY="$(az keyvault secret show --vault-name kv-contoso-demo --name orders-mcp-demo-key --query value -o tsv)"

# 1. initialize: note the Mcp-Session-Id response header, if there is one
curl -si "$MCP_URL" \
  -H "Ocp-Apim-Subscription-Key: $KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"curl-test","version":"1.0.0"}}}'

SESSION="<value of Mcp-Session-Id, or leave empty>"

# 2. tell the server the client is initialized
curl -s "$MCP_URL" \
  -H "Ocp-Apim-Subscription-Key: $KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "MCP-Protocol-Version: 2025-06-18" \
  ${SESSION:+-H "Mcp-Session-Id: $SESSION"} \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized"}'

# 3. list the tools
curl -s "$MCP_URL" \
  -H "Ocp-Apim-Subscription-Key: $KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "MCP-Protocol-Version: 2025-06-18" \
  ${SESSION:+-H "Mcp-Session-Id: $SESSION"} \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'

# 4. call get_order_status as the demo customer CU-3001
curl -s "$MCP_URL" \
  -H "Ocp-Apim-Subscription-Key: $KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "MCP-Protocol-Version: 2025-06-18" \
  ${SESSION:+-H "Mcp-Session-Id: $SESSION"} \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"get_order_status","arguments":{"orderId":"SO-10023"}}}'
