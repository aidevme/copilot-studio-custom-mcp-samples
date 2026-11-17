#!/usr/bin/env bash
# Call a tool on the Logic Apps MCP server with curl: initialize, keep the session ID, then call
# Commands from the post; replace the placeholders before running.

# --- Part 2: https://aidevme.com/copilot-studio-custom-mcp-server-logic-apps/
MCP_URL="https://<copied-mcp-server-url>"

# 1. Initialize and keep the session ID
SESSION_ID=$(curl -sS -D - -o /dev/null -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "X-API-KEY: $AIDEVME_MCP_KEY" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"aidevme-test-client","version":"1.0.0"}}}' \
  | tr -d '\r' | awk 'tolower($1) == "mcp-session-id:" { print $2 }')

# 2. Confirm initialization
curl -sS -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "MCP-Protocol-Version: 2025-06-18" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -H "X-API-KEY: $AIDEVME_MCP_KEY" \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized"}'

# 3. Call create_return
curl -sS -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "MCP-Protocol-Version: 2025-06-18" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -H "X-API-KEY: $AIDEVME_MCP_KEY" \
  -H "AIDevMe-Demo-Customer: CU-3001" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"create_return","arguments":{"orderId":"SO-10023","lineNumber":1,"quantity":1,"reason":"Damaged","comment":"The kettle arrived with a cracked lid."}}}'
