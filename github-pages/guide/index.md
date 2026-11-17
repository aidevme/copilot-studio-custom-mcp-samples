# Overview

<!-- cspell:ignore aidevme apim appsettings vitepress containerapp Dataverse -->

This site goes with the [aidevme.com](https://aidevme.com) series **Custom MCP servers for Copilot Studio** and its
[sample repository](https://github.com/aidevme/copilot-studio-custom-mcp-samples). The posts explain the design; the
repository has the code; this site shows how the pieces fit and how to run them.

## The demo

AIDevMe is a fictional retailer of home and kitchen appliances. Its customer service agent in Copilot Studio runs on
the AIDevMe website and handles questions such as "Where is my order SO-10023?" and "The kettle arrived broken, I want
to return it."

The order data lives outside Dataverse, in an order management system with a REST API. Every build path exposes the
same three tools on top of it. See [the tool contract](./tool-contract.md).

## Two rules on every path

| Rule | What it means |
| --- | --- |
| The customer comes from the caller's identity | No tool takes a customer ID, user ID or email. Another customer's order returns "not found", not "forbidden" |
| The server enforces business rules | Returns only for delivered orders, within 30 days after delivery. The model can't bypass it |

## Where to start

| You want to | Go to |
| --- | --- |
| Know which part covers what | [The series](./series.md) |
| Pick a build path | [Build paths](./build-paths.md) |
| Run the C# server on your machine | [Run locally](./run-locally.md) |
| Deploy everything to Azure | [Provision Azure](./provisioning.md) |

## Demo data and secrets

All order data is fictional: customers such as `CU-3001`, orders such as `SO-10023`, returns such as `RMA-5001`. The
repository contains no keys, secrets or tenant IDs. Settings use placeholders; copy the `*.example` files and fill in
your own values locally.
