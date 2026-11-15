npx @modelcontextprotocol/inspector --cli "https://<copied-mcp-server-url>" --transport http \
  --header "X-API-KEY: $CONTOSO_MCP_KEY" --header "Contoso-Demo-Customer: CU-3001" \
  --method tools/call --tool-name get_order_status --tool-arg orderId=SO-10023
