---
name: aidevme-readability
metadata:
  layer: atomic
  scope: project
  version: 2.0.0
description: |
  Measure and fix all nine checks of the Yoast SEO readability analysis for aidevme.com posts, so drafts land
  green before WordPress: subheading distribution, paragraph length, sentence length, consecutive
  sentences, passive voice, transition words, text presence, word complexity and text alignment, plus the overall
  score. A script measures a Markdown draft or published post and lists what failed; the skill fixes it without
  changing facts, quotes, code or links. Use when: (1) Yoast reports a readability problem or the user pastes a
  Yoast message; (2) the user asks to "check readability", "make it green in Yoast", "fix passive voice", "shorten
  sentences", "add subheadings" or "add transition words"; (3) aidevme-blog-writer reaches its editing sweeps or
  final review; (4) aidevme-seo-audit checks readability of published posts. Does NOT write or restructure articles
  (use aidevme-blog-writer), judge SEO titles, keyphrases or links (use aidevme-seo-audit), or apply to social
  posts (see aidevme-social).
allowed-tools: Read, Edit, Bash, Glob, Grep
argument-hint: "<.content/wordpress-posts/<slug>/index.md | https://aidevme.com/<slug>/> [--cornerstone]"
---

# aidevme-readability

<!-- cspell:ignore aidevme Yoast yoastseo -->

Get aidevme.com posts to a green Yoast SEO readability score, measured rather than guessed. Voice, tone and
house terms come from `.claude/agents/aidevme-context.md`; this skill owns the readability limits and how to
meet them.

## The nine checks

Limits for English blog posts, from Yoast's scoring spec ([yoastseo 3.3.0, `SCORING READABILITY.md`](https://cdn.jsdelivr.net/npm/yoastseo@3.3.0/build/scoring/assessments/SCORING%20READABILITY.md)),
the engine the plugin uses. The site runs Yoast SEO Premium 28.7, which may have newer values, so treat them
as very close rather than guaranteed.

| # | Check | 🟢 Green | 🟠 Orange | 🔴 Red | Script |
| --- | --- | --- | --- | --- | --- |
| 1 | Subheading distribution | Every section < 300 words | A section of 300–350 words | A section > 350 words, or no subheadings in a text > 300 words | ✅ |
| 2 | Paragraph length | Every paragraph ≤ 150 words | 150–200 words | > 200 words | ✅ |
| 3 | Sentence length | ≤ 25% of sentences over 20 words | 25–30% | > 30% | ✅ |
| 4 | Consecutive sentences | Fewer than 3 in a row start with the same word | — | 3 or more in a row | ✅ |
| 5 | Passive voice | ≤ 10% of sentences | 10–15% | > 15% | ✅ |
| 6 | Transition words | ≥ 30% of sentences contain one | 20–30% | < 20% (texts over 200 words only) | ✅ |
| 7 | Text presence | — | — | Under 50 characters | ✅ |
| 8 | Word complexity (Premium) | < 10% complex words | > 10% | > 10% on cornerstone content | ❌ read it from Yoast |
| 9 | Text alignment (Premium) | — | — | A centered paragraph or heading over 50 characters | Published posts only |

**Cornerstone content is stricter** (run the script with `--cornerstone`): sentence length green ≤ 20%, red
> 25%; sections 250 / 300 words instead of 300 / 350; word complexity over 10% turns red. Use it for the
flagship guides that aidevme-blog-optimization marks as cornerstone.

**Overall score:** each red check adds 3 penalty points and each orange check 2. Under 4 points is green, 4–5
orange, 6 or more red. One red alone stays green; two oranges already make it orange. The aim is every check
green, not just the overall score.

**Not scored:** Flesch Reading Ease and the estimated reading time appear in Yoast's panel (Premium Insights)
but don't affect the readability score.

Sources: [Yoast readability scoring spec](https://cdn.jsdelivr.net/npm/yoastseo@3.3.0/build/scoring/assessments/SCORING%20READABILITY.md) ·
[Passive voice](https://yoast.com/how-to-improve-your-passive-voice-score/) ·
[Sentence length](https://yoast.com/the-sentence-length-check/) ·
[Readability analysis](https://yoast.com/features/readability-analysis/)

## Rules

- **Measure body prose only:** paragraphs and list items. Headings, code blocks, tables, image alt text and the
  Resources section don't count.
- **Aim for a margin:** the script approximates Yoast, so target about 8% passive, 20% long sentences, 35%
  transition words and sections under 280 words.
- **Never change meaning for a score.** Facts, numbers, product names and preview status stay exactly as they are.
- **Verbatim quotes stay verbatim**, even when they're passive or long. Count them, and make up the difference
  elsewhere.
- **Keep a passive** only when the actor is unknown or irrelevant and no natural active version exists.
- **Keep the voice.** Short sentences must still read as Zsolt's analytical, candid voice, not as a list of
  fragments. Each sentence needs a subject and a verb.
- **Subheadings must earn their place:** descriptive, with the terms people search for (aidevme-blog-writer's SEO
  checklist), never "Part 2" or "More details".
- When Yoast changes a limit or adds a check, update the table with the exact value and source. Never guess a limit.

## Workflow

### 1. Measure

```bash
python .claude/skills/aidevme-readability/scripts/readability.py <file-or-url> --list [--cornerstone]
```

- Input: a draft (`.content/wordpress-posts/<slug>/index.md`), a saved HTML page, or a published post URL (read through the
  WordPress REST API, falling back to the page HTML).
- Prints a traffic light for each check and the overall score. `--list` shows what each failing check flagged
  (long sections, long paragraphs, long sentences, runs of sentence beginnings, passive candidates).
- `--json` gives the full result for other skills. Exit code 0 means every measured check is green.
- Use `python3` on Linux and macOS.
- **Heuristics to check by hand:**
  - Passive detection looks for a form of *be* or *get* followed by a past participle. "Is based on" or
    "is available" isn't a passive sentence you need to fix.
  - Transition words use the script's own list, which is shorter than Yoast's, so Yoast usually scores a
    little higher.
  - Word complexity isn't measured. After publishing, read it in Yoast's readability panel.

Report the baseline: the overall score and every check that isn't green.

### 2. Fix

Fix the checks in this order. Each fix can move the others, so re-measure after each step. Patterns with
aidevme examples: [references/rewrite-patterns.md](references/rewrite-patterns.md).

1. **Subheading distribution:** split sections over 300 words with a descriptive H3 at a natural break, such as
   a new sub-topic, a step or a table.
2. **Paragraph length:** split paragraphs over 150 words where the idea changes.
3. **Passive voice:** name the actor and put it first. This often shortens the sentence too.
4. **Sentence length:** one idea per sentence, hidden lists as bullets, never two long sentences in a row.
5. **Transition words:** when you split sentences, reconnect them (then, also, so, because, however, for example).
   Splitting without them drops this score.
6. **Consecutive sentences:** vary the first word of three or more sentences in a row. Bullet lists that all
   start with the same word count too.
7. **Word complexity:** after publishing, if Yoast flags it, swap long, uncommon words for familiar ones. Keep
   product names and the focus keyphrase, which Yoast excludes.
8. **Text alignment:** in WordPress, left-align any centered paragraph or heading over 50 characters.

### 3. Re-measure and report

Run the script again. Report before and after for every check and the overall score. Also report what you kept
on purpose (quotes, unavoidable passives) and what only Yoast can confirm (word complexity, table text).

## Used by

- **aidevme-blog-writer:** the clarity sweep and the final review, which reports the overall score and any check
  that isn't green.
- **aidevme-seo-audit:** readability columns for published posts in the per-post table.

## Verify

- [ ] Baseline measured with the script, not estimated; cornerstone limits used for cornerstone posts.
- [ ] Every measured check is green after the fix, or the reason it isn't is stated.
- [ ] No fact, number, quote, code block, link or product name changed.
- [ ] New subheadings are descriptive; remaining passives and long sentences are deliberate and named.
- [ ] Word complexity and text alignment flagged for checking in Yoast after publishing.
