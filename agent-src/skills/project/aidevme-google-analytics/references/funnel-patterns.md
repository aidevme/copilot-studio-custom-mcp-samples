# Funnel patterns — `run_funnel_report`

<!-- cspell:ignore aidevme -->

Signature (analytics-mcp v0.7.0):

```text
run_funnel_report(property_id, funnel_steps, date_ranges=None, funnel_breakdown=None,
                  funnel_next_action=None, segments=None, return_property_quota=False)
```

Always pass `date_ranges` explicitly, even though the tool makes it optional.

## Step syntax

Each step is a dict with a `name` and **either**:

- `"event": "<event_name>"` — shorthand for a single event, or
- `"filter_expression": {…}` — a full `FunnelFilterExpression` (snake_case keys):
  - `funnel_event_filter`: `{"event_name": "…", "funnel_parameter_filter_expression": {…}}`
  - `funnel_field_filter`: `{"field_name": "<dimension>", "string_filter": {"match_type": "…", "value": "…"}}`
  - `and_group` / `or_group`: `{"expressions": [ … ]}`, `not_expression`: `{…}`

Optional:

- `funnel_breakdown`: `{"breakdown_dimension": "deviceCategory"}` (or `sessionDefaultChannelGroup`, `country`).
- `funnel_next_action`: `{"next_action_dimension": "pagePath", "limit": 5}` — what readers did next.

## Open vs closed funnels

- **Closed funnel:** a user must enter at step 1 and complete steps in order. **This is the only kind the
  tool builds** — it doesn't expose `is_open_funnel`, "directly followed by" or time limits between steps.
- **Open funnel** (users may enter at any step) would show where people *join* the journey — for example
  readers who reach the sign-up page from a newsletter without reading an article first.
- **Approximating an open view:** run separate `run_report` counts per step event (`eventName` +
  `totalUsers`) for the same date range. Present them side by side, and label them "users per step, not
  sequential".
- Choose closed when the question is "of readers who arrived, how many subscribed?"; use the approximation
  when the question is "how many people reached the sign-up form at all?".

## Example 1 — Blog visit → article engagement → newsletter sign-up

**Purpose:** the core aidevme.com reader journey.

```json
{
  "property_id": "PROPERTY_ID",
  "date_ranges": [{"start_date": "28daysAgo", "end_date": "yesterday"}],
  "funnel_steps": [
    {"name": "Visited the blog", "event": "session_start"},
    {"name": "Engaged with an article", "filter_expression": {
      "funnel_event_filter": {
        "event_name": "scroll",
        "funnel_parameter_filter_expression": {
          "funnel_parameter_filter": {
            "event_parameter_name": "percent_scrolled",
            "numeric_filter": {"operation": "GREATER_THAN_OR_EQUAL", "value": {"int64_value": 90}}
          }
        }
      }
    }},
    {"name": "Signed up for the newsletter", "event": "NEWSLETTER_EVENT"}
  ],
  "funnel_breakdown": {"breakdown_dimension": "sessionDefaultChannelGroup"}
}
```

**Interpret:** `scroll` with `percent_scrolled` 90 is GA4 enhanced measurement's "read to the end". If the
blog fires a custom read event, use it instead. Biggest drop between steps 2 and 3 → strengthen the in-post
call to action; between 1 and 2 → intros and page speed.

## Example 2 — Search landing → second page → sign-up

**Purpose:** do search visitors explore and subscribe?

```json
{
  "property_id": "PROPERTY_ID",
  "date_ranges": [{"start_date": "28daysAgo", "end_date": "yesterday"}],
  "funnel_steps": [
    {"name": "Organic search visit", "filter_expression": {
      "and_group": {"expressions": [
        {"funnel_event_filter": {"event_name": "session_start"}},
        {"funnel_field_filter": {"field_name": "sessionDefaultChannelGroup", "string_filter": {"match_type": "EXACT", "value": "Organic Search"}}}
      ]}
    }},
    {"name": "Viewed a page", "event": "page_view"},
    {"name": "Signed up", "event": "NEWSLETTER_EVENT"}
  ],
  "funnel_next_action": {"next_action_dimension": "pagePath", "limit": 5}
}
```

**Interpret:** in a closed funnel the step-2 `page_view` must come after step 1, so the landing view itself
counts; read step 2 as "viewed at least one page". `funnel_next_action` lists the pages abandoners went to.

## Example 3 — Post page → GitHub repo click

**Purpose:** do readers of a tutorial go on to its sample code? (Uses enhanced-measurement outbound
`click` events.)

```json
{
  "property_id": "PROPERTY_ID",
  "date_ranges": [{"start_date": "28daysAgo", "end_date": "yesterday"}],
  "funnel_steps": [
    {"name": "Viewed the post", "filter_expression": {
      "and_group": {"expressions": [
        {"funnel_event_filter": {"event_name": "page_view"}},
        {"funnel_field_filter": {"field_name": "pagePath", "string_filter": {"match_type": "EXACT", "value": "/post-slug/"}}}
      ]}
    }},
    {"name": "Clicked through to GitHub", "filter_expression": {
      "funnel_event_filter": {
        "event_name": "click",
        "funnel_parameter_filter_expression": {
          "funnel_parameter_filter": {
            "event_parameter_name": "link_domain",
            "string_filter": {"match_type": "CONTAINS", "value": "github.com"}
          }
        }
      }
    }}
  ],
  "funnel_breakdown": {"breakdown_dimension": "deviceCategory"}
}
```

**Interpret:** low click-through on mobile is normal for code; on desktop, make the repo link more prominent.

## Reading the response

- `funnel_table` holds per-step active users, completion rate and abandonments; with a breakdown, one block
  per breakdown value.
- Report completion **per step** and **overall** (last step ÷ first step), the largest drop, and the
  breakdown value that over- or under-performs.
- Small numbers (< ~30 users at a step) make rates unstable — say so.
