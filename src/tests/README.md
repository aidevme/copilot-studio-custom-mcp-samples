# tests

Contract tests that check a server's `tools/list` against the tool contract ([`src/contract/`](../contract/)).

- `contract/`:
  - `Test-McpToolContract.ps1`: the rules a Copilot Studio agent depends on, such as descriptions, `readOnlyHint`
    and no identity inputs (Part 6)
  - `check-tool-contract.js`: classifies the changes between two `tools/list` snapshots (Part 7)
  - `compare-with-contract.mjs`: strict check that a server's `tools/list` matches `src/contract/tools.json`
    exactly, descriptions and input schema constraints included
  - `inspector.sh`: MCP Inspector commands
- `http/`: raw MCP requests from Part 1, and in `http/responses/` the real responses of the Part 4 C# server

```sh
# Strict check against a running server
curl -s -X POST http://localhost:5080/mcp -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' -H 'MCP-Protocol-Version: 2025-11-25' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' > tools-list.txt
node src/tests/contract/compare-with-contract.mjs src/contract/tools.json tools-list.txt
```

Posts: [Part 1](https://aidevme.com/copilot-studio-custom-mcp-servers-when-you-need-one/), [Part 6](https://aidevme.com/copilot-studio-custom-mcp-tool-design-testing/) and [Part 7](https://aidevme.com/copilot-studio-custom-mcp-governance-alm/).
