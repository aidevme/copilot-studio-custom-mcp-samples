# Report recipes for aidevme.com

<!-- cspell:ignore aidevme isoYearIsoWeek lnkd unifiedScreenName minutesAgo keyEvents -->

Ready-to-use argument shapes. Replace `PROPERTY_ID` with the resolved property, `NEWSLETTER_EVENT` with the
configured sign-up event and `/post-slug/` with a real path. Unless noted, recipes use the **default date
ranges** (last 28 days vs the previous 28 days):

```json
"date_ranges": [
  {"start_date": "28daysAgo", "end_date": "yesterday", "name": "current"},
  {"start_date": "56daysAgo", "end_date": "29daysAgo", "name": "previous"}
]
```

Shorthand below: `"date_ranges": "DEFAULT"` means that block — send the full list, not the string. Keys are
snake_case; enum values are passed by name (`"EXACT"`, `"GREATER_THAN_OR_EQUAL"`); "one of several values" is
an `in_list_filter`.

Reusable host filter (excludes previews and staging):

```json
{"filter": {"field_name": "hostName", "string_filter": {"match_type": "EXACT", "value": "aidevme.com"}}}
```

---

## 1. Top posts by engaged sessions — `run_report`

**Purpose:** which posts hold readers' attention.

```json
{
  "property_id": "PROPERTY_ID",
  "date_ranges": "DEFAULT",
  "dimensions": ["pagePath", "pageTitle"],
  "metrics": ["engagedSessions", "screenPageViews", "activeUsers", "userEngagementDuration"],
  "dimension_filter": {"filter": {"field_name": "hostName", "string_filter": {"match_type": "EXACT", "value": "aidevme.com"}}},
  "order_bys": [{"metric": {"metric_name": "engagedSessions"}, "desc": true}],
  "limit": 25
}
```

**Interpret:** apply the post URL pattern (drop `/`, `/category/…`). Engagement time per user =
`userEngagementDuration / activeUsers`; a post with high views but low time per user has a weak hook or
mismatched search intent.

## 2. Channel overview — `run_report`

**Purpose:** how readers arrive, at a glance.

```json
{
  "property_id": "PROPERTY_ID",
  "date_ranges": "DEFAULT",
  "dimensions": ["sessionDefaultChannelGroup"],
  "metrics": ["sessions", "engagedSessions", "engagementRate", "keyEvents"],
  "order_bys": [{"metric": {"metric_name": "sessions"}, "desc": true}]
}
```

**Interpret:** for a technical blog, Organic Search is the base; Referral and Organic Social spikes usually
trace back to one share — drill in with recipe 3.

## 3. Referrals and social sources — `run_report`

**Purpose:** which sites and networks send readers (GitHub, LinkedIn, X, Reddit, dev communities).

```json
{
  "property_id": "PROPERTY_ID",
  "date_ranges": "DEFAULT",
  "dimensions": ["sessionSource", "sessionMedium"],
  "metrics": ["sessions", "engagedSessions", "engagementRate"],
  "dimension_filter": {"filter": {"field_name": "sessionDefaultChannelGroup", "in_list_filter": {"values": ["Referral", "Organic Social"]}}},
  "order_bys": [{"metric": {"metric_name": "sessions"}, "desc": true}],
  "limit": 25
}
```

**Interpret:** LinkedIn appears as `linkedin.com`, `lnkd.in` and app sources — sum them. `github.com`
referrals with high engagement mean README or repo links work; link more posts from repos.

## 4. GitHub and LinkedIn: which posts they drive — `run_report`

**Purpose:** connect a source to the posts it lands on.

```json
{
  "property_id": "PROPERTY_ID",
  "date_ranges": [{"start_date": "28daysAgo", "end_date": "yesterday"}],
  "dimensions": ["sessionSource", "landingPage"],
  "metrics": ["sessions", "engagedSessions"],
  "dimension_filter": {"filter": {"field_name": "sessionSource", "in_list_filter": {"values": ["github.com", "linkedin.com", "lnkd.in", "com.linkedin.android"]}}},
  "order_bys": [{"metric": {"metric_name": "sessions"}, "desc": true}],
  "limit": 30
}
```

**Interpret:** single range keeps rows readable. Posts that do well on LinkedIn but not in search are
candidates for an SEO rewrite; the reverse are candidates for a LinkedIn post.

## 5. Newsletter campaign traffic (UTMs) — `run_report`

**Purpose:** clicks from newsletter issues, tagged `utm_medium=email`.

```json
{
  "property_id": "PROPERTY_ID",
  "date_ranges": [{"start_date": "90daysAgo", "end_date": "yesterday"}],
  "dimensions": ["sessionCampaignName", "sessionManualAdContent", "landingPage"],
  "metrics": ["sessions", "engagedSessions", "engagementRate"],
  "dimension_filter": {"filter": {"field_name": "sessionMedium", "string_filter": {"match_type": "EXACT", "value": "email", "case_sensitive": false}}},
  "order_bys": [{"metric": {"metric_name": "sessions"}, "desc": true}],
  "limit": 50
}
```

**Interpret:** `utm_content` (`sessionManualAdContent`) shows which link in the issue was clicked. Untagged
newsletter clicks land in Direct — tag every link.

## 6. Landing pages — `run_report`

**Purpose:** entry points, and whether they keep new readers.

```json
{
  "property_id": "PROPERTY_ID",
  "date_ranges": "DEFAULT",
  "dimensions": ["landingPage"],
  "metrics": ["sessions", "newUsers", "engagementRate", "keyEvents"],
  "metric_filter": {"filter": {"field_name": "sessions", "numeric_filter": {"operation": "GREATER_THAN_OR_EQUAL", "value": {"int64_value": 20}}}},
  "order_bys": [{"metric": {"metric_name": "sessions"}, "desc": true}],
  "limit": 25
}
```

**Interpret:** high-entry posts with low engagement rate need a better intro or related-post links. The
metric filter removes low-volume noise.

## 7. Newsletter sign-ups by page — `run_report`

**Purpose:** where sign-ups happen.

```json
{
  "property_id": "PROPERTY_ID",
  "date_ranges": "DEFAULT",
  "dimensions": ["pagePath"],
  "metrics": ["eventCount", "totalUsers"],
  "dimension_filter": {"filter": {"field_name": "eventName", "string_filter": {"match_type": "EXACT", "value": "NEWSLETTER_EVENT"}}},
  "order_bys": [{"metric": {"metric_name": "eventCount"}, "desc": true}],
  "limit": 25
}
```

**Interpret:** empty result → wrong event name; run recipe 15 first. `pagePath` here is the page where the
sign-up event fired.

## 8. Sign-up rate by channel — `run_report`

**Purpose:** which channels bring readers who subscribe.

```json
{
  "property_id": "PROPERTY_ID",
  "date_ranges": "DEFAULT",
  "dimensions": ["sessionDefaultChannelGroup"],
  "metrics": ["sessions", "keyEvents:NEWSLETTER_EVENT"],
  "order_bys": [{"metric": {"metric_name": "sessions"}, "desc": true}]
}
```

**Interpret:** requires the event to be marked as a **key event**; otherwise the metric is invalid — fall back
to recipe 7 with `sessionDefaultChannelGroup` as the dimension. Compute sign-ups per 100 sessions yourself.

## 9. New vs returning readers — `run_report`

**Purpose:** audience loyalty.

```json
{
  "property_id": "PROPERTY_ID",
  "date_ranges": "DEFAULT",
  "dimensions": ["newVsReturning"],
  "metrics": ["activeUsers", "sessions", "engagementRate", "screenPageViewsPerSession"]
}
```

**Interpret:** returning readers usually engage more; a rising returning share after newsletter issues
means the newsletter is building habit. Mention the `(not set)` row if present.

## 10. Country breakdown — `run_report`

**Purpose:** where readers are (time zones for publishing, language).

```json
{
  "property_id": "PROPERTY_ID",
  "date_ranges": [{"start_date": "28daysAgo", "end_date": "yesterday"}],
  "dimensions": ["country"],
  "metrics": ["activeUsers", "sessions", "engagementRate"],
  "order_bys": [{"metric": {"metric_name": "activeUsers"}, "desc": true}],
  "limit": 15
}
```

**Interpret:** combine with recipe 13 (hour of day) to choose publish times. Low-volume countries are noisy.

## 11. Week-over-week trend — `run_report`

**Purpose:** direction of travel over 12 weeks.

```json
{
  "property_id": "PROPERTY_ID",
  "date_ranges": [{"start_date": "84daysAgo", "end_date": "yesterday"}],
  "dimensions": ["isoYearIsoWeek"],
  "metrics": ["activeUsers", "sessions", "engagedSessions", "screenPageViews"],
  "order_bys": [{"dimension": {"dimension_name": "isoYearIsoWeek", "order_type": "ALPHANUMERIC"}, "desc": false}]
}
```

**Interpret:** the first and last weeks may be partial — say so. Check `list_property_annotations` for
explanations of spikes.

## 12. Post performance in its first 30 days — `run_report`

**Purpose:** launch curve of one post. Needs the publish date (from the CMS or the user).

```json
{
  "property_id": "PROPERTY_ID",
  "date_ranges": [{"start_date": "2026-09-01", "end_date": "2026-09-30"}],
  "dimensions": ["date"],
  "metrics": ["screenPageViews", "activeUsers", "engagedSessions"],
  "dimension_filter": {"filter": {"field_name": "pagePath", "string_filter": {"match_type": "EXACT", "value": "/post-slug/"}}},
  "order_bys": [{"dimension": {"dimension_name": "date", "order_type": "ALPHANUMERIC"}, "desc": false}]
}
```

**Interpret:** set `start_date` = publish date, `end_date` = publish date + 29 (absolute dates, property time
zone). Repeat with `sessionDefaultChannelGroup` instead of `date` to see what drove the launch. Compare
posts by day-7 and day-30 cumulative views, not by calendar month.

## 13. Hour-of-day and weekday pattern — `run_report`

**Purpose:** when readers show up.

```json
{
  "property_id": "PROPERTY_ID",
  "date_ranges": [{"start_date": "56daysAgo", "end_date": "yesterday"}],
  "dimensions": ["dayOfWeekName", "hour"],
  "metrics": ["sessions"],
  "order_bys": [{"metric": {"metric_name": "sessions"}, "desc": true}],
  "limit": 20
}
```

**Interpret:** hours are in the **property time zone**. Publish an hour or two before the peak.

## 14. Realtime: what's being read now — `run_realtime_report`

**Purpose:** live view after publishing or sharing a post.

```json
{
  "property_id": "PROPERTY_ID",
  "dimensions": ["unifiedScreenName"],
  "metrics": ["activeUsers", "screenPageViews"],
  "order_bys": [{"metric": {"metric_name": "activeUsers"}, "desc": true}],
  "limit": 10
}
```

**Interpret:** `unifiedScreenName` is the page **title** (realtime has no `pagePath`). Swap in
`country` or `deviceCategory`; add `minutesAgo` for a per-minute curve. Covers the last 30 minutes only and
isn't comparable to processed totals.

## 15. Event inventory — `run_report`

**Purpose:** find the real names of tracked events (for example the newsletter sign-up event).

```json
{
  "property_id": "PROPERTY_ID",
  "date_ranges": [{"start_date": "28daysAgo", "end_date": "yesterday"}],
  "dimensions": ["eventName", "isKeyEvent"],
  "metrics": ["eventCount"],
  "order_bys": [{"metric": {"metric_name": "eventCount"}, "desc": true}],
  "limit": 50
}
```

**Interpret:** confirm the sign-up event exists and whether it's a key event before running recipes 7–8 or a
funnel.
