# Carousel frameworks (LinkedIn document posts)

<!-- cspell:ignore aidevme Dataverse -->

Five slide-by-slide structures for LinkedIn document posts (the same work for Instagram carousels and
TikTok photo mode). Each framework is a different reason to keep swiping; choosing the right one matters
more than polishing individual slides. Treat them as starting structures and validate against aidevme's
own analytics.

A carousel is not a blog post chopped into squares. Every slide has two jobs: deliver one idea, and make
the next swipe worth it.

## Picking a framework

| The content is… | Use | Why |
| --- | --- | --- |
| A list of tools, settings, resources | **A: Value-Stack** | The exact count is the hook; completeness is the promise |
| A result with a system behind it | **B: Problem-Proof** | Proof opens and closes the loop |
| Several named gotchas or techniques on one theme | **C: Hack List** | Each item re-earns the swipe |
| A strong opinion about a common practice | **D: Rant Callout** | Conviction, kept fair by structure |
| A tool or workflow you can show | **E: Demo Walkthrough** | Seeing the steps persuades |

Two rules for all of them:

- **Slide 1 is the thumbnail.** It appears in the feed alone; write it as a standalone scroll-stopper.
- **One visual template.** Same layout, type scale and palette on every interior slide.

## A: Value-Stack (4–14 slides)

| Slide | Job | Pattern |
| --- | --- | --- |
| 1 — Cover | Exact count + exact deliverable | "[N] [resources] for [role/outcome]" |
| 2 to N−1 | One item per slide, 3–6 concrete sub-points | "[Item]: [sub-points]" |
| N — Close | One action | "Full list with links: first comment" / follow / save |

*aidevme example:* "9 Dataverse Web API calls every PCF developer should know" → one call per slide with the
request shape → "Code for all nine in the first comment."

**Failure mode:** padding to a bigger number. A tight 7 beats a padded 12.

## B: Problem-Proof (6–10 slides)

| Slide | Job | Pattern |
| --- | --- | --- |
| 1 — Hook | A result stated as fact, with a number | "[We did X]. [Result]." |
| 2 — The real problem | Name what was actually wrong | "The real problem: [named issue]" |
| 3–4 — Mechanism | Named tools and steps | "The setup: [tools/steps]" |
| 5 to N−1 — Detail | The config, code or prompt — the save-worthy part | "[Literal detail]" |
| N — Proof | The real output (screenshot, chart) | "[Screenshot]: the result" |

*aidevme example:* "Our solution import went from 45 to 9 minutes." → the real problem (unmanaged layers in
test) → the pipeline changes → the YAML → the pipeline duration chart.

**Failure mode:** vague mechanism slides; without named steps the proof reads as luck.

## C: Hack List (6–10 slides)

| Slide | Job | Pattern |
| --- | --- | --- |
| 1 — Contrarian hook | A claim implying most people get this wrong | "[Most X fail at Y because Z]" |
| 2 — The problem | Why the common approach fails | "Why it fails: [reason]" |
| 3 to N−1 — Named items | One named technique per slide, bad vs good | "Gotcha #n: [name]" |
| N — Synthesis | One-line thesis + one CTA | "[Thesis]" + save/follow |

*aidevme example:* "Most plugin bugs aren't in the code. They're in the step registration." → Gotcha #1:
missing filtering attributes, #2: wrong stage for the update… → "Register like you code. Save this for your next plugin."

**Name every item.** Named techniques get repeated and credited; "keep it short" doesn't.

## D: Rant Callout (4–8 slides)

| Slide | Job | Pattern |
| --- | --- | --- |
| 1 — Provocative claim | An opinion about a common practice | "Unpopular opinion: [practice]" |
| 2 to N−2 — Escalate | Specific, concrete examples | "[Specific example]" |
| N−1 — Fairness pivot | What you're *not* attacking | "I use [X] daily. My problem is [Y]." |
| N — Sign-off | Owned opinion | "[Firm close] — [name]" |

*aidevme example:* "Stop shipping canvas apps with 40 hard-coded environment URLs." → examples → "Canvas apps
are great. My problem is skipping environment variables." → sign-off.

**Failure mode:** skipping the pivot, or ranting about something your own repos visibly do.

## E: Demo Walkthrough (5–11 slides)

| Slide | Job | Pattern |
| --- | --- | --- |
| 1 — Outcome | Tool + finished result | "[Tool]: [outcome]" |
| 2 — Pain | What it replaces | "Before: [manual pain]" |
| 3 — Overview | Numbered step list before the detail | "[N] steps, [time]" |
| 4 to N−1 — Steps | One real screenshot per step, short caption | "Step n: [caption]" |
| N — Result | Final output + one positioning line | "[Output] + [line]" |

*aidevme example:* "From a plain-English request to a validated Mermaid ERD in 3 steps" → the pain → 3-step
overview → one screenshot per step → the rendered diagram + repo link in the comment.

**Failure mode:** screenshots with too much UI — crop to the action, one annotation arrow.

## LinkedIn production notes

- Upload a **PDF**; 4:5 (1080×1350) or square. The "N pages" badge rewards an exact count.
- The post text above the document is a second hook — write it as its own post, not "see attached".
- Put the blog/repo link in the first comment.
- Diagrams can be generated with **aidevme-diagram-mermaid** (validated, accessible) and exported as SVG/PNG.

## Production checklist

- [ ] Slide 1 works as a standalone post
- [ ] One idea per slide
- [ ] Same template on every interior slide
- [ ] Count on the cover delivered exactly
- [ ] Numbers and screenshots are real and contain no client data
- [ ] Text legible at thumbnail size (~28 pt at 1080 px wide)
- [ ] One CTA on the last slide
- [ ] Post text written as its own hook

## Measuring

Judge carousels on **saves, completion and comments**, not likes. When one underperforms, the fix is
usually slide 1 or the framework choice. Track performance per framework and keep the two that fit the
audience; see [reverse-engineering.md](reverse-engineering.md).
