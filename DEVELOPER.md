# Developer guide

<!-- cspell:ignore Entra Bicep -->

What you need to build, run and test the samples. For what the repo contains, start with [README.md](README.md).

## What you need

Not every part needs everything. Each folder's README lists its own prerequisites.

- **Local:** .NET 10 SDK, Node.js 22.19 or newer (MCP Inspector), Azure CLI with Bicep, PowerShell 7, Power
  Platform CLI (`pac`), VS Code with the Azure Logic Apps (Standard) extension.
- **Azure:** a subscription for Container Apps, a Standard logic app and an API Management instance (Developer tier
  or above; the Consumption tier doesn't support MCP servers). These resources bill per hour while they exist, so
  delete them when you're done.
- **Microsoft Entra:** an External ID tenant for customer sign-in (Part 5).
- **Power Platform:** an environment with Copilot Studio; Dev, Test and Prod environments for the ALM part (Part 7).
