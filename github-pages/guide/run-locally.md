# Run locally

<!-- cspell:ignore aidevme apim appsettings vitepress containerapp Dataverse -->

The C# server (Part 4) runs on your machine without Azure. Its demo data lives in memory.

## What you need

| Tool | Version |
| --- | --- |
| .NET SDK | 10 |
| Node.js | 22.19 or newer, for MCP Inspector |
| PowerShell | 7, for the contract test |

## Start the server

```sh
dotnet build src/dotnet-mcp-server/src/AIDevMe.OrdersMcp
dotnet run --project src/dotnet-mcp-server/src/AIDevMe.OrdersMcp --urls http://localhost:5080
```

The MCP endpoint is `http://localhost:5080/mcp`.

## Test it

```sh
pwsh ./src/tests/contract/Test-McpToolContract.ps1 -Endpoint http://localhost:5080/mcp
```

For local tool calls without a sign-in, the server accepts the `AIDevMe-Demo-Customer` header, but only when
`Demo:AllowCustomerHeader` is on. `appsettings.Development.json` turns it on; `appsettings.json` keeps it off. Never
turn it on in a deployment.

## Run this site

```sh
npm install
npm run docs:dev
```

The dev server runs at `http://localhost:5173/copilot-studio-custom-mcp-samples/`.
