#!/usr/bin/env bash
# Test the C# MCP server with MCP Inspector (CLI mode)
# Commands from the post; replace the placeholders before running.

# --- Part 4: https://aidevme.com/copilot-studio-custom-mcp-server-azure-pro-code/
npx -y @modelcontextprotocol/inspector@2.15.0 --cli http://localhost:5201/mcp \
  --transport http --header Contoso-Demo-Customer:CU-3001 \
  --method tools/call --tool-name create_return \
  --tool-arg orderId=SO-10023 --tool-arg lineNumber=2 --tool-arg quantity=1 --tool-arg reason=NoLongerNeeded
