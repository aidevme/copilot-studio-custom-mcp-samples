# Medium stories

<!-- cspell:ignore aidevme Zsolt Zombik Dataverse delve -->

Use this reference when the user wants a Medium post: a new story, a Medium version of an aidevme.com article, or a
story built from notes, a talk or a LinkedIn thread. Read `.claude/agents/aidevme-context.md` first, as for every
aidevme writing task.

The author is Zsolt Zombik: Senior Solution Architect at HSO International, Microsoft MVP (Copilot Studio, Power
Apps), founder of AIDevMe. Audience: Power Platform architects, senior developers and technical decision makers,
mostly in Europe.

Save the draft as `.content/wordpress-posts/<slug>/medium-article.md` in the format of `.content/templates/wordpress-post-template/medium-article.md`.
Nothing is published without Zsolt's approval.

## Contents

- Step 1: Pick the mode
- Step 2: Shape the story
- Step 3: Write
- Step 4: Deliverables
- Step 5: Self-check before returning

## Step 1: Pick the mode

Ask only if it is unclear from the request.

- **Mode A, cross-post.** An existing aidevme.com article goes to Medium. Goal: a shorter, story-shaped version that
  sends readers to the full article, without hurting the original's SEO.
- **Mode B, Medium-native.** A new story written for Medium first. Usually more personal and opinionated than a blog
  tutorial: lessons learned, a mistake, a contrarian take, a field report.

If the user gives a URL to an aidevme.com article (or its `.content/wordpress-posts/<slug>/index.md`), read it first and default to
Mode A.

## Step 2: Shape the story

Medium readers decide in the first screen. Before writing, settle these and show them to the user in 4 lines when
the piece is long:

1. The one idea the reader should leave with, in one sentence.
2. The opening scene: a concrete moment, problem or surprise. Never open with a definition or with "In today's...".
3. The reader's payoff: what they can do or decide differently afterwards.
4. Proof: first-hand experience, a demo, numbers, or a cited source.

If no first-hand experience is available, insert placeholders like `[ZSOLT: the client situation where this went
wrong]` rather than inventing anecdotes. Add at least two.

## Step 3: Write

### Length

- **Mode A:** 900 to 1,600 words (about 4 to 7 min read). Keep the argument and one strong example; cut reference
  tables, step-by-step setup and long checklists, and link to the full article for them.
- **Mode B:** 1,200 to 2,200 words (about 5 to 9 min read).

### Structure

- **Title:** under 60 characters, specific, promises the payoff. Offer 3 options. Avoid clickbait and
  colons-plus-buzzword patterns.
- **Subtitle:** one sentence, under 140 characters, adds what the title leaves out.
- **Opening:** 2 to 3 short paragraphs, starting in the scene.
- **Body:** 3 to 5 sections with short, meaningful headings.
- **Ending:** one takeaway paragraph, then a single question to the reader. In Mode A, end with a line linking to
  the full article on aidevme.com.

### Medium formatting limits

Write so the text survives pasting into the Medium editor:

- Medium has two heading levels only (large and small title). Use `##` and `###` and nothing deeper.
- There are no native tables. Turn a table into a short list, or mark it `[IMAGE: table of ...]` so it can be added
  as an image or embedded gist.
- Code: use fenced code blocks for short snippets (under ~25 lines). For longer code, add `[GIST: description]`.
- Use bold sparingly, for terms and UI labels. Use pull quotes (`>`) at most twice.
- Mark images as `[IMAGE: description | alt text]`, with one near the top for the story card preview. Images come
  from **aidevme-image**; diagrams from **aidevme-diagram-mermaid**.

### Voice and style

First person, direct, practical, opinionated where there is a basis for it. International English for a European
audience.

- Vary sentence length. Avoid long runs of short declarative sentences.
- Use sentence-opening connectors (However, As a result, In addition, Instead, Conversely) only for real contrast or
  causation, never in two consecutive sentences.
- No em dashes. Use commas, colons or a new sentence.
- Avoid: "Let's dive in", "It's worth noting", "In conclusion", "game-changer", "landscape", "delve", "robust",
  "seamless", "unlock", "in today's world".
- Prefer concrete product names, settings, numbers and outcomes over abstractions.
- Never invent facts, metrics, quotes or features. Write `[VERIFY: ...]` when a fact is needed but not provided.

## Step 4: Deliverables

Return, in this order:

1. Three title options and one subtitle.
2. The story in Markdown, ready to paste (also saved as `.content/wordpress-posts/<slug>/medium-article.md`).
3. **Tags:** 5 tags (Medium's maximum), mixing broad ones with reach (for example Artificial Intelligence,
   Microsoft, Software Architecture) and specific ones (for example Copilot Studio, Power Platform).
4. **Publication suggestions:** 2 or 3 Medium publications that fit the topic, flagged as "check submission
   guidelines". Don't claim a publication accepts submissions unless verified.
5. **Cross-post note (Mode A):** publish with Medium's **Import a story** feature using the aidevme.com URL. The
   import sets the canonical link to the original, so search engines credit AIDevMe, and backdates the story to the
   original's date. Alternatively, in edit mode open the three-dot menu > **More settings** > **Advanced Settings**,
   select "This story was originally published elsewhere", enter the aidevme.com URL, select **Save canonical
   link**, then publish again. To confirm, search the published page's source for "canonical". Recommend publishing
   on Medium a few days after the original is indexed.
6. **A LinkedIn teaser** (under 1,000 characters, max 3 hashtags) pointing to the Medium story, in the social style
   rules of `SKILL.md`.
7. **A checklist** of every `[ZSOLT]`, `[VERIFY]`, `[IMAGE]` and `[GIST]` placeholder.

## Step 5: Self-check before returning

Read the draft once as a skeptical Medium reader and fix:

- Does the first paragraph make you want to read the second?
- Is there a sentence that only exists to transition? Cut it.
- Are three or more sentences in a row the same length and shape? Merge or extend one.
- Does any section repeat the previous one in different words? Cut it.
- Is every factual claim either sourced, from the user, or marked `[VERIFY]`?

## Sources

- [Importing a post to Medium](https://help.medium.com/hc/en-us/articles/214550207-Import-post) — Medium Help
  Center (import sets the canonical link and backdates the story; checked 2026-10-26)
- [Set a canonical link](https://help.medium.com/hc/en-us/articles/360033930293-Set-a-canonical-link) — Medium
  Help Center (manual path under Advanced Settings)
