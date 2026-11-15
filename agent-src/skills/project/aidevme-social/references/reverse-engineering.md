# Reverse-engineering what works

<!-- cspell:ignore aidevme Apify -->

Instead of guessing, study top-performing posts from peers in the Power Platform, Dynamics 365 and
AI-development space, extract the patterns, and apply them in aidevme's own voice.

## The six steps

### 1. Find the creators

Pick 10–20 accounts that consistently get strong engagement from the audience aidevme wants:

- Post at least weekly, with high engagement relative to followers
- Audience overlap: Power Platform architects, D365 developers, AI-agent builders
- A mix of established voices (MVPs, Microsoft dev-rel) and rising practitioners

Find them via who the audience follows and engages with, conference speaker lists, community newsletters,
and LinkedIn "People also viewed".

### 2. Collect posts

Gather 100–500 posts (a few dozen per account is enough for a personal analysis):

- **Manual:** copy into a spreadsheet — fine for small sets
- **Browser (read-only):** the **playwright-cli** skill with a logged-in session to read recent-activity pages
- **Export/scraping tools** (for example Apify actors): check each platform's terms before using them

Record per post: text, first line, format (text / document / video / image), engagement (reactions,
comments, reposts), posting day/time, topic, CTA.

### 3. Analyse

- **Quantitative:** rank by engagement rate; look at the top 10%; compare formats, topics and timing.
- **Qualitative:** which hook types, lengths, structures and CTAs recur in the top posts? What specific
  details (numbers, code, screenshots) do they use?

Questions to answer: average length of top posts; most common hook type in the top 10%; which formats get
saved; which CTAs drive comments rather than likes.

### 4. Codify a playbook

```text
Pattern: "[Symptom] usually comes down to [specific cause]"
Example: "Slow model-driven forms usually come down to one OnLoad web resource."
Why it works: curiosity gap + specificity

Pattern: "[N] [gotchas] we hit when [doing X]:"
Example: "5 gotchas we hit moving plugins to the 4-layer pattern:"
Why it works: exact count + experience
```

Also record format patterns (story post: hook → context → problem → fix → result → lesson; carousel:
see [carousel-frameworks.md](carousel-frameworks.md)) and CTA patterns that start real conversations
("What did you use instead?" beats "Agree?").

### 5. Apply aidevme's voice

**Practitioner sharing a discovery.** "I found that…" and "we changed…", not "you should…".

**Specific beats vague:**

| Vague | Specific |
| --- | --- |
| "Imports got much faster" | "Imports went from 45 to 9 minutes" |
| "A tricky plugin bug" | "An update step firing twice because filtering attributes were empty" |
| "Lots of people asked" | "Three people asked this in r/PowerApps this week" |

**Write in paragraphs with a rhythm.** Vary sentence length; break lines where a person would pause. One
short line for emphasis is fine; one sentence per line for the whole post is broetry and reads as generated.

```text
Weak:  "I spent three years building solutions the wrong way before I finally realized that the key to
        maintainability was fewer, smaller solutions with clear dependencies."

Better: "For three years we shipped one giant unmanaged solution per project. Every import was a gamble.

        We split it into four managed solutions with explicit dependencies, and the last six releases
        imported without a single conflict."
```

**Real feelings, real stories.** Mention frustration or relief only when it happened, and tie it to the
technical lesson.

### 6. Convert attention

- First-comment links to the full post (LinkedIn), link cards elsewhere
- Newsletter link in profile and in follow-up comments
- Repo links for tool posts, with a one-line install
- "If you've hit this too, I wrote up the fix" — sparingly

## The formula

1. Find what already works for this audience.
2. Extract the patterns (hooks, formats, CTAs).
3. Apply them in aidevme's voice, with real detail.
4. Measure with platform analytics and **aidevme-google-analytics**; iterate.

## Checklist

- [ ] 10–20 relevant creators identified
- [ ] 100+ posts collected and ranked by engagement rate
- [ ] Top hook, format and CTA patterns documented
- [ ] Voice rules written (specificity, paragraphs, no AI tells)
- [ ] Template library updated in [post-templates.md](post-templates.md)
- [ ] Own-post tracking in place
