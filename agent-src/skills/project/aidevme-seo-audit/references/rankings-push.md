# Rankings push

<!-- cspell:ignore aidevme -->

Moving posts that already rank onto page one is cheaper than winning a query from nothing. This needs query
data; without it, mark the section **[NEEDS DATA]** and tell Zsolt how to get it.

## Get the data

| Source | How | Gives |
| --- | --- | --- |
| Search Console | search.google.com/search-console → Performance → Search results → filter last 28 days vs previous → export (queries + pages) | Query, page, clicks, impressions, CTR, average position |
| Site Kit (WordPress admin) | Site Kit → Search Console widgets | Top queries and pages (summary) |
| GA4 via **aidevme-google-analytics** | Organic landing pages (`sessionDefaultChannelGroup` = Organic Search, `landingPage`) | Engagement of organic visitors — not positions |

Ask Zsolt for a Search Console export (CSV) when positions or CTR are needed; never estimate them.

## Find the candidates

| Bucket | Filter | Fix type |
| --- | --- | --- |
| Striking distance | Average position 8–20, impressions above a floor that fits the site (start with 50+/28 days) | Content and internal links |
| Weak click-through | Position 1–5, CTR clearly below the site's other top-5 queries | Title and meta description only |
| Near the top | Position 4–7 on a pillar query | Missing section, freshness, snippet-friendly format |

Prioritize by fit with the positioning (pillar topics, flagship guides) over raw impressions.

**Check cannibalization first:** if two aidevme posts rank for the same query, choose one owner before editing.

## Diagnose against the top three

For each candidate, open the three results above it and write the concrete reason each wins:

- **Intent** — they answer the question asked; the aidevme post answers a neighboring one.
- **Missing section** — a sub-question they cover (People Also Ask, their H2s).
- **Freshness** — current product names, statuses, screenshots.
- **Format** — the table, steps or comparison the query calls for.
- **Links** — more and stronger internal and external links.

No visible reason → the gap is likely authority; recommend internal links from strong aidevme posts and
earned mentions rather than a rewrite.

## Smallest change that closes the gap

- Answer the query in the first two sentences of the relevant section.
- Add the missing section; don't rewrite a page that already ranks.
- Put the query in the SEO title and H1 if it reads naturally.
- Add 2–3 internal links from strong related posts with descriptive anchors.
- Refresh stale facts, names and screenshots.
- Weak CTR: change only the SEO title and meta description, so the effect is attributable.

Record the baseline (position, impressions, CTR, date), then wait 3–4 weeks before judging. After two rounds
without movement, stop editing — the limit is intent or authority.

## New posts launch-ready

Handled by **aidevme-blog-writer**'s SEO checklist; verify after publishing: in the sitemap, indexable,
self-canonical, 2–5 inbound internal links, unique title/description, schema present. Request indexing once in
Search Console; repeating doesn't help.
