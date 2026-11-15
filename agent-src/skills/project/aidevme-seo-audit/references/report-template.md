# Report template

<!-- cspell:ignore aidevme -->

Saved as a new file per audit: `.audit/<YYYY-MM-DD_HHmmss>_seo-audit_<scope>.md`.

```markdown
---
skill: aidevme-seo-audit
scope: full
run: 2026-10-23 10:15:02 (local)
request: "<Zsolt's request, verbatim>"
sources: [robots.txt, sitemap_index.xml, wp-json posts + yoast_head_json, PageSpeed Insights (mobile), Search Console export 2026-09-25..2026-10-22]
---

# aidevme.com SEO audit — <scope>

**Verdict:** one or two sentences on overall health and the biggest blocker.

**Top issues**
1. …
2. …
3. …

**Quick wins:** …

## Crawlability and indexation
| Issue | Impact | Evidence | Fix | Priority |
| --- | --- | --- | --- | --- |

## Technical health
(same table; Core Web Vitals labelled field or lab data)

## On-page (per post)
| Post | SEO title (len) | Meta description (len) | Canonical | Robots | H1 | Images w/o alt | Readability | Long sentences % | Passive % | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Content
(same issue table: intent, freshness, E-E-A-T, cannibalization groups, AI-search readiness)

## Striking distance
| Query | Post | Position | Impressions | CTR | Why the top 3 win | Smallest fix |
| --- | --- | --- | --- | --- | --- | --- |
(or [NEEDS DATA] with how to get it)

## Proposed titles and descriptions
| Post | Current | Proposed | Reason |
| --- | --- | --- | --- |

## Action plan
1. Critical (blocks indexing or ranking)
2. High impact
3. Quick wins
4. Long term
Handed to aidevme-blog-optimization: …
Handed to aidevme-blog-writer: …

## [VERIFY] / [NEEDS DATA]
- …
```

Impact scale: **High** = blocks indexing or affects many posts; **Medium** = limits ranking or CTR of
important posts; **Low** = hygiene. Priority orders the action plan, not the severity.
