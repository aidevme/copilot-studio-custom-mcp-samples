# aidevme.com WordPress REST API: read endpoints

<!-- cspell:ignore aidevme Yoast yoast orderby totalpages -->

Base: `{{baseUrl}}/wp-json/wp/v2/` with `baseUrl` = `https://aidevme.com`. Every request in the collection is a
**GET**: aidevme.com is read-only for assistants (AGENTS.md section 7). Field lists match the ones the other
aidevme skills already use against the site.

## In the collection

| Folder / request | Path and key parameters | Auth |
| --- | --- | --- |
| Site / Get API index | `/wp-json/?_fields=name,description,url,namespaces` | none |
| Posts / List recent posts | `posts?per_page=10&_fields=id,date,modified,slug,link,title,categories,tags` | none |
| Posts / Get post by slug | `posts?slug={{postSlug}}&_fields=id,slug,link,title,excerpt,categories,tags,yoast_head_json` | none |
| Posts / Search posts | `posts?search={{searchTerm}}&per_page=10&_fields=id,slug,link,title` | none |
| Pages / List pages | `pages?per_page=50&_fields=id,slug,link,title,status` | none |
| Taxonomy / List categories | `categories?per_page=100&_fields=id,name,slug,parent,count,description,link` | none |
| Taxonomy / List tags | `tags?per_page=100&orderby=count&order=desc&_fields=id,name,slug,count,description,link` | none |
| Media / List recent media | `media?per_page=20&_fields=...` with every public media field (the schema's view fields, `featured_media`, `filename`, `filesize` and the plugin fields `wf_attachment_folders`, `acf`, `jetpack_*`, `class_list`) | none |
| Drafts / List draft posts | `posts?status=draft&per_page=20&_fields=id,slug,status,modified,title` | basic, application password |

## Candidates to add (all GET)

| Need | Path |
| --- | --- |
| Posts in one category or tag | `posts?categories=<id>` / `posts?tags=<id>` |
| Posts changed since a date | `posts?modified_after=<ISO 8601>&orderby=modified` |
| One post, page or media item by ID | `posts/<id>`, `pages/<id>`, `media/<id>` |
| A category or tag by slug | `categories?slug=<slug>` / `tags?slug=<slug>` |
| Site-wide search (posts, pages, terms) | `search?search=<term>&type=post` |

Before adding anything not listed, check the route in the
[WordPress REST API reference](https://developer.wordpress.org/rest-api/reference/) or in the API index
(`/wp-json/`), and confirm it is a read.

## Never in this collection

`POST`, `PUT`, `PATCH` and `DELETE` on any route, including "harmless" ones (a test post, a tag rename, a media
upload). Changes to the site go through an approved plan that Zsolt applies (aidevme-blog-tags,
aidevme-blog-categories). `check_collection.py` fails on any method other than GET or HEAD.

## Query parameters

| Parameter | Notes |
| --- | --- |
| `_fields` | Comma-separated fields to return; keeps responses small. Use it on every list request. |
| `per_page` | 1–100 (default 10). Above 100 the API answers 400 `rest_invalid_param`. |
| `page` | Page number; read `X-WP-TotalPages` to know how many there are. |
| `orderby`, `order` | e.g. `date`, `modified`, `title`, `count` (terms); `asc` / `desc`. |
| `slug`, `search`, `status` | Filters; `status` other than `publish` needs authentication. |

Pagination headers on list responses: `X-WP-Total` (items) and `X-WP-TotalPages` (pages).

## Errors

| Status | Meaning on aidevme.com |
| --- | --- |
| 406 | The site firewall rejected the user agent. The collection-level User-Agent header is missing or short. |
| 401 `rest_forbidden_status` / `rest_not_logged_in` | Not signed in: credentials missing or wrong. Check the variable names, never the values in chat. |
| 403 `rest_forbidden_status` / `rest_forbidden` | Signed in, but the user lacks the capability. |
| 400 `rest_invalid_param` | A parameter is out of range (`per_page` > 100, unknown `orderby`). |
| 404 `rest_no_route` | Wrong path or namespace. Compare with `/wp-json/`. |
| 200 with `[]` | Valid query, nothing matches (e.g. no published post with that slug). |
