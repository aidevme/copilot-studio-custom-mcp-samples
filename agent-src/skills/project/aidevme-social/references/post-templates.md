# Post templates

<!-- cspell:ignore aidevme Dataverse -->

Starting shapes for aidevme posts. Fill every slot with real detail (tool names, versions, error text,
numbers) and write in paragraphs, not one sentence per line. Every template must still pass the
"No AI tells" check in SKILL.md.

## Contents

- LinkedIn: Project Lesson, How-To, Gotcha List, Release, Opinion
- X threads: Tutorial, Story, Breakdown, Release
- Bluesky: Insight + link, Mini-thread
- Reddit / forum answer
- Hook formulas

## LinkedIn

### The Project Lesson (story)

```text
[Hook: the unexpected outcome, with a number or the exact symptom]

[Context in one or two sentences: the system, the constraint — no client names]

[What went wrong or what we tried first, with the technical detail]

[The fix or turning point: the setting, code, design change]

[The result, measured if possible]

[The lesson another architect can reuse]

[Optional real question you want answered, or "Full write-up in the first comment."]
```

### The How-To

```text
How to [outcome] in [Power Platform / D365 context] (without [common workaround]):

1. [Step] — [why it matters]
2. [Step] — [the key setting or call]
3. [Step] — [the mistake to avoid]

[What you get at the end, and one limitation to know about]

Code and screenshots in the post: link in the first comment.
```

### The Gotcha List

```text
[N] things that broke when we [did X] — and the fix for each:

1. [Gotcha]: [symptom]. Fix: [specific fix].
2. [Gotcha]: [symptom]. Fix: [specific fix].
3. [Gotcha]: [symptom]. Fix: [specific fix].

[Which one cost the most time, and why]
```

Deliver exactly the count in the hook; no filler items.

### The Release

```text
[What the reader can now do, in one sentence, naming the tool]

[The problem it solves, from your own work]

[How it works in two or three sentences, or "Here's a 40-second demo:" + video/GIF]

[Install / try it: one command or one link]

[What's next or what feedback you want]
```

### The Opinion

```text
[The position, stated plainly]

[The evidence that changed your mind: a test, a number, a project outcome]

[Two or three reasons, each with a concrete example]

[What you recommend instead, and when the common approach is still right]
```

## X threads

### Tutorial thread

```text
1/ [Specific claim naming the topic in the first 8 words] — here's the exact setup:
2–6/ One step per post, each with the setting, code (as image) or command
7/ [Result + limitation]
8/ Full write-up with code: [link]
```

### Story thread

```text
1/ [Time] ago, [specific unexpected thing] happened in a [system] project.
2–5/ The beats: symptom → investigation → wrong turns → root cause
6/ The fix and the result
7/ The lesson + link to the write-up
```

### Breakdown thread

```text
1/ [Microsoft/Anthropic/GitHub] just shipped [thing]. What it means for [audience]:
2–5/ Analysis points, each with a concrete implication
6/ Your take, with the evidence
```

### Release thread

```text
1/ [Tool] now [capability]. [Demo video, 8 s+, captioned]
2/ Why I built it (the problem)
3/ How to try it: [one command]
4/ Repo: [link] — issues and PRs welcome
```

Post the thread as one unit; don't post other originals within the hour.

## Bluesky

### Insight + link

```text
[One specific insight in ≤ 2 sentences, naming the tool]
[Link card to the post]
```

### Mini-thread

```text
1/ [Hook + promise] (≤ 300 characters)
2–4/ The steps or findings
5/ [Link]
```

## Reddit / forum answer

```text
[Direct answer to the question in the first line]

[Steps or code that solve it, in full]

[The gotcha people usually hit]

Disclosure: I wrote a longer walkthrough here (my blog): [link]
```

## Hook formulas

Fill every formula with a real fact; never ship the bracket text.

- **Curiosity:** "I was wrong about [common Power Platform belief]." · "[Symptom] usually comes down to [specific cause]."
- **Story:** "Last week [unexpected thing] happened in production." · "I almost [shipped a specific mistake]."
- **Value:** "How to [outcome] (without [common pain]):" · "[N] [settings/gotchas] that [outcome]:"
- **Contrarian:** "[Common advice] cost us [specific result]." · "Everyone says [X]. In our [N] projects, [Y]."
- **Proof:** "We [result] in [timeframe] with [tool]. Here's the setup:"
