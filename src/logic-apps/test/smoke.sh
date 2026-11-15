#!/usr/bin/env bash
# Call a tool on the Logic Apps MCP server with curl
# Commands from the post; replace the placeholders before running.

# --- Part 2: https://aidevme.com/copilot-studio-custom-mcp-server-logic-apps/
curl -sS -X POST "https://<copied-mcp-server-url>" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "MCP-Protocol-Version: 2025-06-18" \
  -H "X-API-KEY: $CONTOSO_MCP_KEY" \
  -H "Contoso-Demo-Customer: CU-3001" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"create_return","arguments":{"orderId":"SO-10023","lineNumber":1,"quantity":1,"reason":"Damaged","comment":"The kettle arrived with a cracked lid."}}}'
