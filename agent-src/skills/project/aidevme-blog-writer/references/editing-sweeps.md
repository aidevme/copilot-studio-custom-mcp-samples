# Editing sweeps

<!-- cspell:ignore aidevme -->

Run in order. Each sweep has one focus; fix as you go. Re-read the whole draft after the last sweep.

## 1. Accuracy

- Every fact has a source in Resources or came from the user.
- Product names, versions, preview/GA status and dates match the sources.
- Code blocks are complete, have a language tag and match the text around them.
- House terms from the context file are used consistently (Dataverse, Copilot Studio, PCF…).

## 2. Structure

- The opening states the problem or moment within the first 3 sentences.
- Each H2 delivers one idea, starts with its answer, and earns its place — cut or merge the rest.
- Heading levels don't skip (H2 → H3 → H4).
- The post delivers exactly what the title and intro promise (count, scope, steps).

## 3. Clarity

- **Readability (aidevme-readability):** run its script on the draft and fix in its order until every measured
  Yoast check is green (subheadings, paragraphs, passive voice, sentence length, transition words, sentence
  beginnings). Report the overall score in the final review.
- Replace vague verbs and nouns ("leverage", "utilize", "solution" used loosely) with specific ones.
- Define an acronym on first use unless it's in the audience's daily vocabulary (API, ALM are fine; ACS isn't).

## 4. Specificity and proof

- Replace "significantly", "much faster", "many" with the number, or remove the claim.
- Back every recommendation with a reason or an example.
- Opinions are labelled as such ("My recommendation…", "I'd treat this as…").

## 5. Voice and style rules

Check against the voice profile in `.claude/agents/aidevme-context.md`:

- Technical mode reads analytical and candid; personal mode warm and understated.
- **Contrast lines** ("not X — Y"): at most one per H2 section; rewrite the rest as direct statements.
- **Em dashes**: allowed for asides, not in every paragraph.
- **Never:** stock phrases, broetry, emoji bullets, engagement bait, invented numbers or quotes.
- Fragments for emphasis: occasional, not a rhythm.
- Passive voice, sentence length and the other Yoast checks: measured and fixed in the clarity sweep
  (aidevme-readability).

## 6. Scannability

- Comparisons and reference lists are tables, not paragraphs.
- Steps are numbered; options are bulleted.
- Bold lead-ins only for genuine labels (Current status:, Remember:), not decoration.
- An image, diagram, table or code block at least every ~600 words in technical posts.

## 7. Leftovers

Search the draft for and remove:

- Editing instructions or revision notes, especially bracketed ones like "(shifts perspective)"
- `TODO`, `TBD`, `[placeholder]`, `lorem`, unresolved `[VERIFY: …]` (list any that must stay)
- Duplicate paragraphs or a sample shown twice by accident
- Broken relative links and images missing alt text
