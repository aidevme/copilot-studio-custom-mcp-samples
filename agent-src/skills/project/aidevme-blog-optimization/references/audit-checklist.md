# Audit checklist

<!-- cspell:ignore aidevme Yoast -->

Read-only. Collect evidence, compare with the rules, report ranked findings and an ordered change list.

## Collect

| What | How |
| --- | --- |
| Menu items, header/footer links, sidebar widgets, social links | Fetch `https://aidevme.com` (and `/blog/` if it exists) |
| Homepage title, meta description, og:title, og:site_name | Fetch the homepage HTML and read `<title>`, `meta[name=description]`, `og:*` tags |
| Categories (slug, parent, post count) | `curl -s "https://aidevme.com/wp-json/wp/v2/categories?per_page=100&_fields=id,name,slug,parent,count"` |
| Tags (name, count) | `curl -s "https://aidevme.com/wp-json/wp/v2/tags?per_page=100&orderby=count&order=desc&_fields=id,name,slug,count"` |
| Categories on recent posts | `curl -s "https://aidevme.com/wp-json/wp/v2/posts?per_page=20&_fields=title,link,categories,tags,date"` |
| Pages (Start Here, About, FAQ, Contact) | `curl -s "https://aidevme.com/wp-json/wp/v2/pages?per_page=50&_fields=title,link,status"` |
| Per-post Yoast metadata | `yoast_head_json` on the posts/pages endpoints (title, description, og) |
| Dead links | `curl -s -o /dev/null -w "%{http_code} %{url_effective}\n" -L <url>` for each social and footer link |
| Redirect behaviour | `curl -sI <old-url>` — expect `301` and a `location` header |

Menus aren't exposed by the public REST API; read them from the rendered HTML.

## Compare

| Check | Rule |
| --- | --- |
| Positioning | Homepage title, og:title and hero carry the positioning line; event recaps or personal news aren't the lead |
| Menu | ≤ 6 top-level items, two levels, Subscribe CTA; items point at category archives or pillar pages |
| Categories | Pillars, not products; no empty, legacy or duplicate categories; "Featured Post" isn't a category |
| Post categorization | 1 primary + ≤ 1 secondary; no default "Power Platform" |
| Labels | Sentence case; Power Apps, Fluent UI, PCF, Microsoft Foundry spelled officially |
| URLs | One URL per topic; renamed/removed slugs have 301s |
| Metadata | Single `site_name`; meta descriptions 150–160 characters |
| Hidden assets | Open-source tools, accessibility docs, talks, the newsletter, the MVP status — visible on the homepage? |
| Hygiene | Dead or placeholder social links (Facebook, X, Instagram), duplicate handles, outdated events |

## Report format

```text
VERDICT: [one or two sentences]

FINDINGS (ranked by impact)
| # | Area | Finding | Evidence | Fix |
1. Positioning gaps
2. Structural problems (duplicate URLs, category sprawl, labels)
3. Hidden assets
4. Hygiene (dead links, duplicate handles)

CHANGE LIST (in order)
1. Separate homepage (static page) from the blog (/blog/)
2. Create redirects
3. Change slugs / merge categories
4. Update menu
5. Metadata and hygiene fixes
6. Clear cache, re-test redirects

[VERIFY] items for Zsolt
```
