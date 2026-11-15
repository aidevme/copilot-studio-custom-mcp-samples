# GA4 Data API schema cheatsheet

<!-- cspell:ignore isoYearIsoWeek yearWeek unifiedScreenName minutesAgo keyEvents -->

API names for the GA4 Data API (`run_report`, `run_funnel_report`). Names are **camelCase** and case-sensitive;
request *object keys* are snake_case. Full list: [API dimensions & metrics](https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema).

## Scope rules (read first)

Every field has a scope. Mixing scopes is the main source of empty, odd or rejected reports.

| Scope | Examples | Pairs well with | Watch out |
| --- | --- | --- | --- |
| **User** | `firstUserSource`, `firstUserDefaultChannelGroup`, `newVsReturning`*, `customUser:*` | `totalUsers`, `activeUsers`, `newUsers` | "First user" = how the user was *first* acquired, not this visit |
| **Session** | `sessionSource`, `sessionMedium`, `sessionCampaignName`, `sessionDefaultChannelGroup`, `landingPage` | `sessions`, `engagedSessions`, `engagementRate`, `bounceRate`, `averageSessionDuration` | Use session-scoped acquisition fields for "where did this visit come from" |
| **Event** | `eventName`, `pagePath`, `pageTitle`, `pageReferrer`, `customEvent:*` | `eventCount`, `screenPageViews`, `keyEvents`, `userEngagementDuration` | Session metrics by an event dimension are attributed to every value the session touched — totals don't add up |
| **Item** | `itemName`, `itemCategory`, `customItem:*` | `itemsViewed`, `itemRevenue` | Item-scoped fields don't combine with non-item metrics; aidevme.com has no e-commerce, so avoid them |

\* `newVsReturning` is evaluated per user at the time of the session.

## Known incompatibilities and traps

- **Item-scoped dimension + session/user metric** (for example `itemName` + `sessions`) → rejected or empty.
- **Processed vs realtime:** `run_realtime_report` accepts only realtime fields (below). `pagePath`,
  `pageTitle`, `sessionSource`, `landingPage`, `engagementRate` are **not** realtime fields.
- **Cohort fields** (`cohort`, `cohortNthDay`, …) need a cohort spec the tool doesn't expose — don't use them.
- **Custom dimensions** must be registered in GA4 and referenced with their prefix (`customEvent:author`);
  a parameter that was sent but never registered isn't queryable. Check with `get_custom_dimensions_and_metrics`.
- **`order_bys`** fields must be in the request's `dimensions` / `metrics`.
- **Filters:** dimension conditions in `dimension_filter`, metric conditions in `metric_filter`; an
  OR of (dimension AND metric) conditions can't be expressed in one request.
- **Key events:** `keyEvents` is the renamed `conversions` metric (2024). Per-event form: `keyEvents:sign_up`.
  An event counts only if it is marked as a key event in GA4 Admin.

## Acquisition

| Dimension | Meaning |
| --- | --- |
| `sessionDefaultChannelGroup` | Organic Search, Direct, Referral, Organic Social, Email, … |
| `sessionSource` / `sessionMedium` / `sessionSourceMedium` | e.g. `github.com` / `referral`, `newsletter` / `email` |
| `sessionCampaignName` | `utm_campaign` |
| `sessionManualAdContent`, `sessionManualTerm` | `utm_content`, `utm_term` |
| `firstUserSource`, `firstUserMedium`, `firstUserDefaultChannelGroup` | First-touch acquisition (user scope) |
| `pageReferrer` | Full referring URL (event scope) |

## Engagement

| Metric | Meaning |
| --- | --- |
| `sessions`, `engagedSessions` | Sessions; engaged = > 10 s, ≥ 2 page views, or a key event |
| `engagementRate`, `bounceRate` | engagedSessions / sessions; 1 − engagementRate |
| `averageSessionDuration` | Seconds per session |
| `userEngagementDuration` | Total foreground seconds (divide by `activeUsers` for per-user time) |
| `eventCount`, `eventsPerSession` | Events |

## Pages and content

| Field | Kind | Meaning |
| --- | --- | --- |
| `pagePath` | dim | Path without host or query |
| `pagePathPlusQueryString` | dim | Path with query string |
| `pageTitle` | dim | `<title>` of the page |
| `landingPage` / `landingPagePlusQueryString` | dim | First page of the session (session scope) |
| `hostName` | dim | Filter to `aidevme.com` to exclude previews/staging |
| `screenPageViews` | metric | Page views |
| `screenPageViewsPerSession` | metric | Views per session |

## Events and key events

| Field | Kind | Meaning |
| --- | --- | --- |
| `eventName` | dim | `page_view`, `scroll`, `click`, `user_engagement`, `sign_up`, … |
| `isKeyEvent` | dim | `true` for events marked as key events |
| `keyEvents`, `keyEvents:<event>` | metric | Key-event count |
| `sessionKeyEventRate`, `userKeyEventRate` | metric | Share of sessions / users with a key event |

## Users and technology

| Field | Kind | Meaning |
| --- | --- | --- |
| `newVsReturning` | dim | `new`, `returning`, `(not set)` |
| `deviceCategory`, `operatingSystem`, `browser`, `language` | dim | |
| `totalUsers`, `activeUsers`, `newUsers` | metric | `activeUsers` is GA4's default "Users" |

## Geography

| Field | Kind |
| --- | --- |
| `country`, `region`, `city`, `continent` | dim |

## Time

| Field | Use |
| --- | --- |
| `date` (`YYYYMMDD`), `dateHour` | Daily / hourly series |
| `isoYearIsoWeek`, `yearWeek`, `week` | Weekly series (prefer `isoYearIsoWeek` for Monday-start weeks) |
| `yearMonth`, `month` | Monthly series |
| `dayOfWeekName` | Weekday patterns |

## Realtime fields (`run_realtime_report` only)

| Dimensions | Metrics |
| --- | --- |
| `unifiedScreenName` (page title on web), `country`, `city`, `deviceCategory`, `platform`, `eventName`, `minutesAgo`, `streamName`, `audienceName` | `activeUsers`, `screenPageViews`, `eventCount`, `keyEvents` |

Realtime covers the last 30 minutes (60 on GA4 360); `minutesAgo` buckets 0–29.
