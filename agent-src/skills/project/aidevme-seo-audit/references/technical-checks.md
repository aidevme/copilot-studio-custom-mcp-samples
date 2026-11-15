# Technical checks

<!-- cspell:ignore aidevme Yoast runPagespeed -->

Commands assume bash with `curl` and `python`. Always send a browser user agent; aidevme.com's firewall can
answer scripted requests with **406**, which is not a page error.

```bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) aidevme-seo-audit"
```

## Crawlability

| Check | Command | Pass when |
| --- | --- | --- |
| robots.txt | `curl -s -A "$UA" https://aidevme.com/robots.txt` | No `Disallow` on posts, `/category/`, CSS/JS; sitemap referenced |
| Sitemap index | `curl -s -A "$UA" https://aidevme.com/sitemap_index.xml` | Lists post, page and category sitemaps |
| Sitemap contents | fetch each child sitemap, collect `<loc>` URLs | Only canonical, indexable 200 URLs; every published post present; no tag/author/attachment noise unless intended |
| Orphans | compare sitemap post URLs with internal links found on the homepage, category archives and other posts | Every post linked from at least one other post or archive |

## Indexation

| Check | How | Pass when |
| --- | --- | --- |
| Robots meta per post | REST API `yoast_head_json.robots` (see below) | `index, follow` on posts you want ranked |
| Canonical | `yoast_head_json.canonical` | Self-referencing, `https://aidevme.com/<slug>/` with trailing slash |
| Status codes | `curl -s -o /dev/null -w "%{http_code}" -A "$UA" <url>` | 200 for posts; 301 (single hop) for moved URLs; no 404 in sitemap or internal links |
| Redirect chains | `curl -sIL -A "$UA" <url>` | At most one redirect, ending in 200 |
| Index coverage | Search Console → Pages report; `site:aidevme.com` as a rough check only | Indexed ≈ sitemap count; reasons for exclusions understood |

### Per-post Yoast data in one call

```bash
curl -s -A "$UA" "https://aidevme.com/wp-json/wp/v2/posts?per_page=100&_fields=id,slug,link,date,modified,title,yoast_head_json"
```

`yoast_head_json` contains `title`, `description`, `canonical`, `robots`, `og_*`, `twitter_*` and `schema`
(the JSON-LD graph Yoast outputs). Repeat with `/pages` for pages. If the field is missing, Yoast's REST output
is disabled — fall back to fetching each page's HTML `<head>`.

## Duplicate URLs

- Topic **pages** with the same slug as **category archives** (e.g. `/pcf/` vs `/category/pcf/`) compete for the
  same queries. Report them, then hand the fix (redirect, delete, merge) to **aidevme-blog-optimization**.
- HTTP → HTTPS and `www` → apex must each 301 once: `curl -sI -A "$UA" http://aidevme.com/` and
  `curl -sI -A "$UA" https://www.aidevme.com/`.
- Trailing slash consistency: `/<slug>` should 301 to `/<slug>/`.

## Speed and Core Web Vitals

Field data (real users) beats lab data. Thresholds for "good" at the 75th percentile:

| Metric | Good | Needs improvement | Poor |
| --- | --- | --- | --- |
| LCP | ≤ 2.5 s | ≤ 4.0 s | > 4.0 s |
| INP | ≤ 200 ms | ≤ 500 ms | > 500 ms |
| CLS | ≤ 0.1 | ≤ 0.25 | > 0.25 |

PageSpeed Insights API (keyless use is rate-limited; sample a few URLs):

```bash
curl -s "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://aidevme.com/&strategy=mobile&category=performance" \
  | python -c "import json,sys;d=json.load(sys.stdin);f=d.get('loadingExperience',{}).get('metrics',{});print({k:v.get('category') for k,v in f.items()});print('lab score:',d['lighthouseResult']['categories']['performance']['score'])"
```

Report field data when present (`loadingExperience`); otherwise label results as **lab data**. Also check
Search Console → Core Web Vitals for site-wide groups.

Common WordPress causes to check before blaming hosting: oversized featured images, multiple analytics tags
(e.g. Site Kit and MonsterInsights both loading `gtag.js`), page-builder and mega-menu scripts, unoptimized web
fonts, and caching or CDN misconfiguration.

## HTTPS and mobile

- Valid certificate, no mixed content (search the HTML for `http://` asset URLs).
- `<meta name="viewport">` present; no horizontal scroll; tap targets ≥ 44 px; same main content as desktop.

## Structured data

Yoast outputs JSON-LD server-side, so `yoast_head_json.schema` (or the `<script type="application/ld+json">`
in the HTML) shows it. Check that posts carry `Article`/`BlogPosting` with author, `datePublished` and
`dateModified`, and that the author is a `Person` linked to the About page. Validate with the Rich Results
Test (https://search.google.com/test/rich-results), which renders JavaScript — don't report "no schema" from a
stripped fetch.
