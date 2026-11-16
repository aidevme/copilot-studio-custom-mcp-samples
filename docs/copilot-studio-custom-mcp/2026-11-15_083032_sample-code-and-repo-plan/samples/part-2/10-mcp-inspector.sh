npx @modelcontextprotocol/inspector --cli "https://<copied-mcp-server-url>" --transport http \
  --header "X-API-KEY: $AIDEVME_MCP_KEY" --header "AIDevMe-Demo-Customer: CU-3001" \
  --method tools/call --tool-name get_order_status --tool-arg orderId=SO-10023
