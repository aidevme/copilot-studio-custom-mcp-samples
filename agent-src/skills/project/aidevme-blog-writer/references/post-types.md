# Post types

<!-- cspell:ignore aidevme Dataverse -->

Templates modelled on published aidevme posts. Headings are examples — write descriptive H2s for the actual
topic. Every type ends with **Resources** (except personal posts, which link inline).

## Deep dive

**For:** how a capability works and what it changes for architects (e.g. "Dataverse MCP Server: The 15 Tools
That Make Power Platform Agent-Ready"). **Length:** 3,500–5,000 words, ~18–22 min read.

```text
Opening (no heading)  — the concrete problem the capability solves, in 2–4 short paragraphs
H2 The problem, solved structurally  — what it is and why it matters
H2 How it works  — architecture, components, flow (diagram)
H2 [Capability areas]  — one H2 per major area, each answer-first
H2 Connecting / setting it up  — clients and configuration, numbered steps
H2 Writing instructions / configuration that works  — real samples in code blocks
H2 Billing and licensing  — what costs what, sourced
H2 Security and governance  — H3 per concern: auth, roles, environment gates, audit, data, risks
H2 What this changes for architects  — the author's analysis and recommendations
H2 Reference: [full surface]  — table of tools / settings / limits
H2 Resources
Close  — one forward-looking line before Resources
```

## Guide / tutorial

**For:** getting something working end to end (e.g. "Storybook MCP Server: The Complete Developer Guide").
**Length:** 2,500–4,500 words.

```text
Opening  — why the author cared, in first person, and what the reader will have at the end
H2 What is [X]?  — answer-first definition, then context
H2 Options compared  — table (official vs community, A vs B) with when to use each
H2 How it works  — H3 per component
H2 Installing [X]: step by step  — H3 "Step 1…n", each with command/config in a code block
H2 Configuring [client]  — e.g. VS Code / Claude Code / Copilot Studio
H2 Real-world workflows  — H3 per workflow, numbered sequence, what the output looks like
H2 Current limitations and roadmap  — candid, dated
H2 Key takeaways  — 4–6 bullets
H2 Over to you  — one real question for comments
H2 Resources
```

Prerequisites go inline at the step that needs them unless there are more than three; then add a short
"Before you start" list under the first step.

## News analysis

**For:** an announcement and its impact (e.g. "GitHub Copilot Code Reviews Are Coming to Azure Repos — What
It Means for Power Platform Teams"). **Length:** 1,500–2,500 words.

```text
Opening  — what was announced, when, by whom, with the source link
H2 What actually shipped  — facts only: availability, regions, licensing, preview/GA
H2 How it works  — mechanism, diagram if useful
H2 What it means for Power Platform / D365 teams  — concrete scenarios
H2 What to do now  — numbered actions (try, wait, plan, govern)
H2 Open questions  — what's unclear or unannounced
H2 Resources
```

Date every claim about availability ("as of 2026-10-22"); separate announcement from the author's analysis.

## Lessons learned

**For:** a real project problem, root cause and fix. **Length:** 1,500–3,000 words.

```text
Opening  — the symptom as it appeared (error text, behaviour), anonymised context
H2 What we saw
H2 What we tried first  — and why it didn't work
H2 The root cause  — with evidence (logs, trace, docs)
H2 The fix  — config/code, step by step
H2 How to prevent it  — checks, pipeline gates, design rules
H2 Key takeaways
H2 Resources
```

No client names, tenants or data. Use demo reproductions for screenshots.

## Release

**For:** an aidevme tool, skill or MCP server. **Length:** 1,200–2,500 words.

```text
Opening  — the problem it solves, from the author's own work
H2 What [tool] does  — capabilities, with a demo GIF/screenshot
H2 How it works  — architecture, diagram
H2 Getting started  — install + first run in code blocks
H2 Example: [realistic task]  — input → output
H2 Limitations and what's next
H2 Over to you  — feedback, issues, contributions
H2 Resources  — repo, docs, related posts
```

## Personal / community

**For:** events, talks, milestones (e.g. "I'm a Microsoft MVP Now"). **Length:** 800–1,500 words.

```text
Opening  — the moment, told as a scene, first person
H2 What [it] actually means
H2 The long way here / What happened  — the story
H2 What changes, and what doesn't
H2 Who made it possible  — credit people and communities (with permission)
H2 Where this goes from here  — bulleted upcoming topics
Close  — a short thank-you
```

Warm, understated, dry humour; links inline, no Resources section needed.
