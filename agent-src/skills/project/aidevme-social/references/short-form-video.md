# Short-form video: YouTube Shorts, TikTok, Reels

<!-- cspell:ignore aidevme Dataverse -->

For aidevme, short-form video means **captioned screen-recording demos** of tools, fixes and workflows —
one recording, posted to Shorts, TikTok and Reels.

## Specs

| Platform | Length that works | Aspect | Notes |
| --- | --- | --- | --- |
| YouTube Shorts | 30–60 s (max 3 min) | 9:16 | Searchable title; links to the full video or post |
| TikTok | 20–45 s | 9:16 | Native, unpolished is fine |
| Instagram Reels | 15–45 s | 9:16 | Saves and shares weigh most |

## The first 3 seconds

Three hooks at once, in the first second:

```text
[VISUAL: the finished result on screen] + [VOICE: the claim] + [TEXT OVERLAY: 3–6 words]
```

Show the end result first ("this diagram was generated and validated by an agent"), then how.

## Hook library (developer edition)

- **Result first:** "This Dataverse ERD took one sentence and 20 seconds."
- **Problem:** "Your plugin runs twice on every update. Here's why."
- **Discovery:** "I found a Copilot Studio setting that removes the need for a flow."
- **Warning:** "Stop hard-coding environment URLs in canvas apps. It broke our release."
- **Comparison:** "Power Automate or a plugin for this? Here's how I decide."
- **Transformation:** "Manual solution export: 15 minutes. With this pipeline: zero clicks."

Every hook must be true and shown in the video.

## Structures

**Tool demo (30–45 s)**

```text
[0–3 s]   Result on screen + claim
[3–8 s]   The pain it replaces
[8–35 s]  2–4 steps, one per beat, zoomed to the action
[35–45 s] Where to get it (repo/post) + one line why
```

**Fix in 60 seconds (45–60 s)**

```text
[0–3 s]   The symptom (error message on screen)
[3–12 s]  Why it happens
[12–50 s] The fix, step by step
[50–60 s] Result + link to the write-up
```

**Decision (30–45 s)**

```text
[0–3 s]   "A or B?"
[3–35 s]  Criteria, with one example each
[35–45 s] The pick and when the other one wins
```

## Scripting template

```markdown
## Video: [working title]

**Platforms:** Shorts / TikTok / Reels · **Length:** XX s · **Format:** screen recording + voice-over

### Hook (0–3 s)
- Visual: [what's on screen]
- Voice: [the line]
- Text overlay: [3–6 words]

### Body
- [time] — [beat: what's shown, what's said]
- [time] — [next beat]

### CTA (last 3–5 s)
- Voice: [e.g. "Repo and write-up in the description"]
- Text: [same]

### Production
- Recording: [app, resolution, zoom level]
- Captions: [tool]
- Redaction: [blur tenant names, URLs, record data]
```

## Recording screen demos

- Record at 1080p+; zoom in so text is readable on a phone (crop to the relevant pane)
- Highlight the cursor and clicks; keep movements slow and deliberate
- **Blur or use demo data**: no tenant URLs, client names, emails or record data
- Optional face-cam in a corner for talking points
- Voice-over slightly faster than conversation; record in a quiet room; remove noise

## Captions

Most viewing is muted. Max 2 lines on screen, 3–5 words per line, bold sans-serif with outline, key terms
highlighted, timed to speech. Tools: CapCut, Descript, Premiere Pro, or the platform's auto-captions
(check technical terms like "Dataverse" and "PCF").

## Posting

- Post the same edit to all three platforms; adapt title, caption and hashtags per
  [platform-limits.md](platform-limits.md)
- Times to test: 12–3 pm and 7–9 pm in the audience's time zone
- Reply to comments in the first hour; turn good questions into the next video

## Metrics

| Metric | Tells you |
| --- | --- |
| Average view duration / completion | Did the hook and pacing hold? |
| Saves | Reference value |
| Shares | Worth passing on |
| Comments | Sparked questions |
| Follows, link clicks | Converted interest |

**Pivot rules:** low completion across 5+ videos → change hooks and cut length; views but no follows →
check the CTA and topic fit; saves but no shares → useful but not social, add a stronger opinion or result.
