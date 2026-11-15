# SEO and AI-search checklist

<!-- cspell:ignore aidevme -->

Write for readers first; these checks make the post findable by search engines and quotable by AI
assistants without changing what it says.

## Title and slug

- **Title:** names the product and the outcome; ~50–65 characters before truncation in search results. A longer
  title is fine on the page, but put the key terms first.
- **Slug:** lowercase, hyphenated, 3–7 meaningful words, no dates, no stop-word padding
  (`dataverse-mcp-server-tools`, not the full title). Never change the slug of a published post.

## Excerpt (meta description)

- ≤ 155 characters, one or two sentences: what the reader learns and for whom.
- Contains the main term naturally; no quotes or emoji.

## Headings and structure

- One H1 (the title — WordPress renders it; don't repeat it in the body).
- H2s are descriptive and contain the terms people search for ("Connecting Claude Code to the Dataverse MCP
  Server", not "Setup").
- The first paragraph under each H2 answers the heading directly — this is what AI assistants extract and
  cite.
- Define the main subject in one plain sentence early ("The Dataverse MCP server is…").

## Evidence AI assistants can cite

- Tables for comparisons, limits and reference data.
- Explicit versions, dates and preview/GA status.
- Numbered steps for procedures.
- A **Resources** section linking official sources.

## Links

- **Internal:** 2–5 links to related aidevme posts (search the site or recent posts) with descriptive anchor
  text; add the new post's link to an older related post when refreshing it.
- **External:** official documentation and announcements; avoid linking competitors' rewrites of the same docs.

## Images

- Descriptive file names (`dataverse-mcp-risk-tiers.png`, not `image1.png`).
- Alt text that states what the image shows and why it matters; diagrams use the Mermaid `accDescr` text.
- Featured image set in the frontmatter with alt text.

## Avoid

- Keyword stuffing, repeated exact-match phrases, filler intros written for length.
- "Ultimate/complete guide" claims the post doesn't fully deliver.
