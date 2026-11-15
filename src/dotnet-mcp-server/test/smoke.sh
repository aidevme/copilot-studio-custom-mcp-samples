#!/usr/bin/env bash
# Run the C# MCP server locally and call it with curl
# Commands from the post; replace the placeholders before running.

# --- Part 4: https://aidevme.com/copilot-studio-custom-mcp-server-azure-pro-code/
dotnet build                 # Build succeeded. 0 Warning(s) 0 Error(s)
dotnet run --launch-profile http
curl http://localhost:5201/health     # Healthy

# --- Part 4: https://aidevme.com/copilot-studio-custom-mcp-server-azure-pro-code/
curl -s http://localhost:5201/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"curl","version":"8"}}}'

# --- Part 4: https://aidevme.com/copilot-studio-custom-mcp-server-azure-pro-code/
curl -s http://localhost:5201/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "MCP-Protocol-Version: 2025-11-25" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' | sed -n 's/^data: //p'
