---
name: aidevme-google-analytics
metadata:
  layer: atomic
  scope: project
description: |
  Analyse Google Analytics 4 (GA4) data for the aidevme.com blog through Google's official read-only
  analytics-mcp server. Use when the user asks about aidevme.com traffic, users or page views; top or trending
  posts; traffic sources, referrals (GitHub, LinkedIn, newsletter UTMs) or landing pages; newsletter sign-up
  conversions; reader funnels (visit → article engagement → sign-up); realtime visitors in the last 30 minutes;
  or the GA4 property's configuration (custom dimensions and metrics, property details, annotations). Turns
  report rows into findings and content recommendations. Does NOT apply to Universal Analytics (UA-, retired),
  managing Google Ads campaigns, Google Tag Manager or gtag installation, or changing GA4 configuration (the
  server is read-only).
allowed-tools: mcp__analytics-mcp__get_account_summaries, mcp__analytics-mcp__get_property_details, mcp__analytics-mcp__list_google_ads_links, mcp__analytics-mcp__list_property_annotations, mcp__analytics-mcp__get_custom_dimensions_and_metrics, mcp__analytics-mcp__run_report, mcp__analytics-mcp__run_funnel_report, mcp__analytics-mcp__run_realtime_report, Read, AskUserQuestion
argument-hint: "[question about aidevme.com traffic, posts, sources, funnels or realtime]"
---

# aidevme-google-analytics

<!-- cspell:ignore aidevme pipx thresholding UTMs -->

GA4 analysis for the aidevme.com technical blog. The **analytics-mcp server provides API access**; this skill
provides the expertise: which tool to call, in what order, how to build a valid request, and how to turn rows
into decisions about what to write and promote next.

**Never invent, estimate or "fill in" numbers.** Every figure you report comes from a tool response in this
conversation. If you can't get data, say so.

## Property configuration

Fill these in once. Until then, resolve them at run time as described in step 1.

| Setting | Value |
| --- | --- |
| GA4 property ID | `{{AIDEVME_GA4_PROPERTY_ID}}` <!-- e.g. 123456789; fill in --> |
| Property display name to match | `aidevme.com` |
| Site hostname | `aidevme.com` |
| Newsletter sign-up event | `{{NEWSLETTER_SIGNUP_EVENT}}` <!-- e.g. sign_up / generate_lead; verify in GA4 --> |
| Post URL pattern | `{{POST_PATH_PATTERN}}` <!-- e.g. /<slug>/ ; see Content mapping --> |

## Preflight

Before the first analysis in a conversation:

1. Check that the `mcp__analytics-mcp__*` tools are available. If they aren't, **stop**: explain that the
   analytics-mcp server isn't connected and walk the user through [references/setup.md](references/setup.md).
2. If any call fails with an auth or permission error (`401`, `403`, `PERMISSION_DENIED`,
   `invalid_grant`, `Request had insufficient authentication scopes`, "API has not been used in project" /
   `SERVICE_DISABLED`), **stop** and point to the matching section of [references/setup.md](references/setup.md).
   Do not retry with guessed parameters.

## Workflow

### 1. Resolve the property

- If the property ID in the table above is filled in, use it, and confirm once with `get_property_details`
  that its display name matches.
- Otherwise call `get_account_summaries` and pick the property whose display name matches `aidevme.com`.
  **Never guess or reuse an ID from memory.** If there is no match, or several, list the candidates and ask.
- Note the property **time zone** and **currency** from `get_property_details`; state the time zone in every
  answer.

### 2. Check custom fields

Before using any field that isn't a standard GA4 dimension or metric (anything shaped `customEvent:…`,
`customUser:…`, `customItem:…`), call `get_custom_dimensions_and_metrics` and use the exact `api_name` and
scope it returns. Cache the result for the conversation.

### 3. Choose the tool

| Question | Tool |
| --- | --- |
| Historical traffic, posts, sources, trends | `run_report` |
| Ordered steps (visit → engage → sign up) | `run_funnel_report` |
| Who's on the site right now (last 30 minutes) | `run_realtime_report` |
| Which property / its settings, time zone | `get_account_summaries`, `get_property_details` |
| Custom dimensions and metrics | `get_custom_dimensions_and_metrics` |
| Why traffic spiked or dropped on a date | `list_property_annotations` (plus a `date` report) |
| Linked Google Ads accounts (read-only) | `list_google_ads_links` |

### 4. Build and validate the request

- Start from a recipe in [references/report-recipes.md](references/report-recipes.md) (funnels:
  [references/funnel-patterns.md](references/funnel-patterns.md)).
- Use API names from [references/ga4-schema-cheatsheet.md](references/ga4-schema-cheatsheet.md). Field names
  in the request objects are **snake_case** (`start_date`, `field_name`, `string_filter`, `match_type`).
- Validate before calling:
  - every dimension and metric exists, and realtime-only / processed-only fields aren't mixed up;
  - scopes are compatible (user vs session vs event vs item — see the cheatsheet);
  - every field in `order_bys` is also in `dimensions` or `metrics`;
  - dimension conditions go in `dimension_filter`, metric conditions in `metric_filter`.

### 5. Apply defaults (unless the user says otherwise)

- **Date range:** last 28 days compared with the previous 28 days, as two named ranges:
  `[{"start_date": "28daysAgo", "end_date": "yesterday", "name": "current"},
  {"start_date": "56daysAgo", "end_date": "29daysAgo", "name": "previous"}]`.
  Two ranges add a `dateRange` column to the response.
- Exclude today (partial, unprocessed data) from historical reports.
- **Ordering:** descending by the primary metric. **Limit:** 10–25 rows for rankings, all rows for
  time series (≤ 366 days).
- State the property time zone and the exact dates covered.

### 6. Present the results

1. **Findings first** — 3–5 bullets: what changed (with % change vs the previous period), why it likely
   matters, and **what to write or promote next** (for example "the Dataverse plugin post doubled from
   LinkedIn — write a follow-up and re-share it").
2. **Compact table** — the rows that back the findings, numbers formatted (thousands separators, % to
   one decimal).
3. **Caveats** — flag any that apply: `subject_to_thresholding` / sampling metadata in the response,
   `(not set)` rows, low volume (< ~50 sessions per row: treat changes as noise), realtime vs processed data,
   today excluded. Details: [references/gotchas.md](references/gotchas.md).

## Content mapping

aidevme.com posts live in the blog's CMS, not in this repository, so map GA4 page paths to **post URLs**:

1. Use `pagePath` (or `landingPage` for entry analysis); strip query strings and a trailing slash.
2. Treat a path as a post when it matches the post URL pattern above; group or drop the rest: `/` (home),
   `/category/…`, `/tag/…`, `/page/N`, `/author/…`, search and preview URLs.
3. Report each post as its title (`pageTitle`) linked to `https://aidevme.com<pagePath>`.
4. If two paths point to the same post (old slug, trailing slash, `?utm_…`), merge their rows and say so.

If the posts are later stored as Markdown with slugs, add the content root and slug rule here so findings can
link the source file.

## Error recovery

| Symptom | Likely cause | Action |
| --- | --- | --- |
| "Field … is not a valid dimension/metric" | Wrong API name, or a custom field without its prefix | Check the cheatsheet / `get_custom_dimensions_and_metrics`; fix the name |
| "… are incompatible" / "Please remove …" | Scope clash (for example item-scoped dimension with a session metric) | Drop or swap the field per the cheatsheet; run two reports if needed |
| Realtime call rejects `pagePath`, `sessionSource`, … | Not a realtime field | Use realtime fields (`unifiedScreenName`, `country`, `deviceCategory`, `minutesAgo`) |
| `RESOURCE_EXHAUSTED` / quota error | Property token quota | Stop, report it, retry later with fewer/narrower reports; use `return_property_quota` |
| Empty `rows` | Filter too narrow, wrong event name, no data in range, wrong property | Remove filters one at a time; check the event exists with an `eventName` report; confirm the property |
| Numbers far off what the user expects | Wrong property or stream, time zone, today included | Re-check step 1 and the date range; see gotchas |
| `PERMISSION_DENIED` on one property only | Account lacks access to that property | Ask the user to grant Viewer access in GA4 Admin |

Never paper over an error with a guess. Report what failed and what you tried.

## References — read X when Y

| Read | When |
| --- | --- |
| [references/setup.md](references/setup.md) | Tools missing, auth/permission/API-disabled errors, first-time setup |
| [references/ga4-schema-cheatsheet.md](references/ga4-schema-cheatsheet.md) | Choosing dimension/metric names, checking scope compatibility |
| [references/report-recipes.md](references/report-recipes.md) | Building any `run_report` or `run_realtime_report` request |
| [references/funnel-patterns.md](references/funnel-patterns.md) | Building a `run_funnel_report` request |
| [references/gotchas.md](references/gotchas.md) | Explaining odd numbers, thresholding, time zones, quotas, realtime limits |

## Guardrails

- Read-only: the server can't change GA4 configuration. Don't offer to create events, key events, custom
  dimensions or annotations — explain the GA4 Admin steps instead.
- Never print, request or store credentials, client secrets or the ADC JSON contents.
- Don't attribute causes the data doesn't show; label hypotheses as hypotheses.

## Verify

Before finishing an answer, confirm:

- [ ] The property was resolved by name or confirmed with `get_property_details` (not guessed).
- [ ] Every number traces to a tool response in this conversation.
- [ ] Date range and property time zone are stated.
- [ ] Applicable caveats (thresholding, `(not set)`, low volume, realtime) are listed.
