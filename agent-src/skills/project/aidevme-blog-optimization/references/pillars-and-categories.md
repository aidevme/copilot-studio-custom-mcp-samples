# Pillars, menu and categories

<!-- cspell:ignore aidevme Dataverse Yoast -->

## Main menu

At most six top-level items, two levels deep, plus a **Subscribe** button styled as a CTA.

| # | Top level | Second level |
| --- | --- | --- |
| 1 | **Start here** | What AIDevMe covers, most-read guides, learning resources |
| 2 | **Build with AI** (AI-assisted development) | GitHub Copilot, Claude Code, MCP for developers, agent skills and agents.md |
| 3 | **Build AI agents** (AI inside solutions) | Copilot Studio, Microsoft Foundry, Dataverse MCP and agent-ready data, agent architecture |
| 4 | **Pro-code Power Platform** | PCF (React, Fluent UI and Storybook as tags), Power Apps Code Apps, model-driven apps and web resources, canvas apps and custom pages, Power Pages, Dataverse |
| 5 | **ALM and governance** | DevOps and pipelines, infrastructure as code (Terraform), security and data governance |
| 6 | **Open source and speaking** | GitHub tools, sessions and talks, About, MVP, Contact, FAQ |

## Category to pillar mapping

| Old category | New home |
| --- | --- |
| Pcf, Design, Fluent UI, React, Storybook, PCF Tips & Tricks | Pro-code → PCF; sub-topics become tags |
| PowerApps → Overview, Canvas, Model-Driven, Custom Pages, Code Apps | Pro-code, flattened; drop "Overview" |
| AI & Copilot, AI, AI in Development, Developer Productivity | Split between Build with AI and Build AI agents |
| Model Context Protocol | Dev tooling MCP → Build with AI; Dataverse/agent MCP → Build AI agents |
| Claude, GitHub Copilot, Entire.io | Build with AI; Entire.io becomes a tag |
| DevOps, Terraform | ALM and governance |
| Low-Code / Pro-Code | Pro-code Power Platform |
| Featured Post | Not a category; use sticky posts or a flag |
| Portfolio → Sessions, event categories | Open source and speaking |

Before proposing the migration, fetch the live categories (slugs, parents, post counts) — see
[audit-checklist.md](audit-checklist.md) — so every row maps a real category and its post count is known.

## Splitting rule: Build with AI vs Build AI agents

| Question about the post | Pillar |
| --- | --- |
| Does AI help the developer build the solution (coding assistants, dev-time MCP, agent skills)? | Build with AI |
| Does AI run inside the delivered solution (agents, Copilot Studio, Foundry models, agent-ready Dataverse)? | Build AI agents |
| Both | Primary = the reader's main job; the other as secondary |

## Tags

Tags are products and technologies: PCF, Dataverse, MCP, GitHub Copilot, Claude Code, Copilot Studio,
Microsoft Foundry, Power Apps Code Apps, React, Fluent UI, Storybook, Terraform, Azure DevOps, PAC CLI, …
Reuse existing tag spelling from the live taxonomy; merge near-duplicates (e.g. "MCP" / "MCP Server" /
"Model Context Protocol") only with redirects for the tag archives.

## Redirects

Every removed or renamed page, category or slug gets a 301. Order of work: **create redirects → change slugs
→ update menu → clear cache**.

| From | To | Reason | Status |
| --- | --- | --- | --- |
| `/pcf/` | Pro-code → PCF archive | Category merged | candidate |
| `/power-apps/` | Pro-code Power Platform archive | Category flattened | candidate |
| `/overview/` | Pro-code Power Platform archive | "Overview" dropped | candidate |
| `/category/…/azure-ai-foundry-tutorials/` | Microsoft Foundry archive (new slug) | Old product name in slug | candidate |

Tooling: Yoast Premium creates redirects on slug change; otherwise use the Redirection plugin. Test each with
`curl -sI <old-url>` (expect `301` and the new `location`).
