#!/usr/bin/env bash
# Test the Logic Apps MCP server with MCP Inspector (CLI mode)
# Commands from the post; replace the placeholders before running.

# --- Part 2: https://aidevme.com/copilot-studio-custom-mcp-server-logic-apps/
npx @modelcontextprotocol/inspector --cli "https://<copied-mcp-server-url>" --transport http \
  --header "X-API-KEY: $CONTOSO_MCP_KEY" --header "Contoso-Demo-Customer: CU-3001" --method tools/list

# --- Part 2: https://aidevme.com/copilot-studio-custom-mcp-server-logic-apps/
npx @modelcontextprotocol/inspector --cli "https://<copied-mcp-server-url>" --transport http \
  --header "X-API-KEY: $CONTOSO_MCP_KEY" --header "Contoso-Demo-Customer: CU-3001" \
  --method tools/call --tool-name get_order_status --tool-arg orderId=SO-10023
