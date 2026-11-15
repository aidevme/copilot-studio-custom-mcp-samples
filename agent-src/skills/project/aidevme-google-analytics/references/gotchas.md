# GA4 gotchas

<!-- cspell:ignore aidevme thresholding unifiedScreenName -->

Read this when numbers look odd, before blaming the content.

## Data thresholds and sampling

- **Thresholding:** GA4 withholds rows when a report could identify individuals — mainly with Google
  signals enabled and low user counts, or demographic dimensions. Rows silently disappear and totals drop.
  The response metadata reports `subject_to_thresholding: true`; when it does, say so and suggest a wider
  date range or fewer dimensions.
- **Sampling:** standard Data API reports are normally unsampled; very large or complex queries can return
  `sampling_metadatas` in the metadata. If present, state the sampled share.
- **`(not set)`:** the value wasn't available (for example a session without a landing page, a referrer
  stripped by privacy settings). Report it as its own row; don't drop it silently.
- **`(other)`:** high-cardinality dimensions (many unique `pagePathPlusQueryString` values) can collapse into
  `(other)`. Prefer `pagePath` over query-string variants.

## Time zone and date boundaries

- Every date and hour is in the **property time zone** (from `get_property_details`), not the reader's or
  yours. State it in answers.
- `today` is partial and still processing; `yesterday` can still change for 24–48 hours. Default historical
  ranges end at `yesterday`.
- Relative dates (`28daysAgo`) are evaluated in the property time zone when the request runs.
- Weekly dimensions: `isoYearIsoWeek` starts Monday; `week` starts Sunday. First and last weeks of a range
  may be partial.

## Realtime limitations

- Covers the last **30 minutes** (60 on GA4 360), counted from when the event arrives.
- Only realtime dimensions and metrics work (`unifiedScreenName` for the page title — no `pagePath`,
  no session or traffic-source fields, no engagement rate).
- Numbers aren't deduplicated or processed like standard reports; never add realtime figures to
  historical totals.

## Quota limits

The Data API meters **tokens** per property; complex requests (many dimensions, long ranges) cost more.
Standard-property defaults at the time of writing (check the
[current limits](https://developers.google.com/analytics/devguides/reporting/data/v1/quotas)):

| Quota (standard property) | Limit |
| --- | --- |
| Core tokens per property per day | 200,000 |
| Core tokens per property per hour | 40,000 |
| Concurrent requests per property | 10 |

Realtime and funnel reports have their own buckets. Pass `return_property_quota: true` to see remaining
tokens. On `RESOURCE_EXHAUSTED`: stop, report it, and retry later with fewer, narrower reports.

## Why GA4 numbers differ from other tools

- **Consent and blockers:** readers who decline cookies (Consent Mode) or block GA aren't counted, or are
  modelled; technical audiences block more than average.
- **Definitions:** GA4 "users" = `activeUsers`; a session ends after 30 minutes of inactivity; "views" =
  `screenPageViews`. Server logs, Search Console clicks, CMS view counters and newsletter click reports all
  count differently.
- **Attribution:** session-scoped source vs first-user source vs key-event attribution answer different
  questions. Search Console clicks ≠ GA4 Organic Search sessions.
- **Bots and previews:** filter on `hostName = aidevme.com` to exclude previews and staging.

## Read-only scope

The server runs with `analytics.readonly` (and without `--allow-write`). The skill **can't** create or change
events, key events, custom dimensions, audiences, data streams or annotations. When configuration is needed
(for example "mark `sign_up` as a key event"), explain the steps in GA4 Admin and let the user do it.
