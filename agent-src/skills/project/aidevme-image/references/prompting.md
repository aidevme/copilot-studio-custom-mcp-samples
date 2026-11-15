# Prompting for aidevme images

<!-- cspell:ignore aidevme Dataverse -->

## Structure

```text
[Subject: the visual metaphor and its 3–5 elements]
+ [Setting: where it happens, background]
+ [Style: flat vector editorial illustration, clean geometric shapes, soft shadows]
+ [Colors: aidevme palette with hex values]
+ [Composition: size, where the subject sits, empty third for a title]
+ [Exclusions: no text, letters, numbers, logos, faces, UI]
```

- **60–150 words.** Shorter prompts leave too much to the generator; much longer ones lose focus.
- **Name every element concretely** ("an envelope card for its own mailbox"), not abstractly ("communication").
- **Put the hex colors in the prompt.** Generators follow explicit colors better than "brand colors".
- **Always state the size or ratio**, otherwise the output size is random.
- **Write exclusions twice:** at the end of the prompt and, when the generator supports it, as a negative prompt.

## Shared style block

Paste this into every aidevme prompt and change only the subject and composition:

```text
Style: flat vector editorial illustration, modern SaaS look, clean geometric shapes, soft drop shadows,
generous white space, calm and professional.
Colors: background #F5F6FB, main accent violet #5B3FD6, deep violet #3F2BA8, teal #0B6476, small rust #9A3B12
accents, ink #0E1330 for dark shapes.
No text, no letters, no numbers, no logos, no brand marks, no realistic faces, no user interface screenshots.
```

Negative prompt: `text, letters, words, watermark, logo, Microsoft logo, product logo, realistic photo, human
faces, user interface, clutter, dark background, neon glow, 3D render`.

## Visual metaphors for aidevme topics

| Topic | Metaphor |
| --- | --- |
| Agent identity and accounts | An agent at the team table with its own ID badge, mailbox and chat window, under a shield and key |
| MCP servers and tools | A hub with plug-in sockets; tool cards connecting an agent to a database cylinder |
| Dataverse and data models | Stacked rounded tables linked by lines, with a magnifier checking one row |
| ALM and governance | Packages moving along a pipeline through gates with check marks and a shield |
| AI-assisted development | A developer's desk shape with a code editor card and an assistant shape suggesting a block |
| PCF and front-end components | Building blocks snapping into a form frame |
| Billing and credits | Tokens or coins flowing from a meter into an agent, with a gauge |
| Security and shared data risk | A document card whose summary bubble floats past a locked door |

## Example: featured image

```text
Flat vector illustration, wide 1200x630 banner, light background #F5F6FB with a subtle geometric grid.
Center: a friendly abstract AI agent figure in violet #5B3FD6 sitting at a shared team table as a colleague,
wearing a lanyard with a blank ID badge. Next to it float three small cards: an envelope (its own mailbox), a
chat window (its own chat presence) and a notebook with connected dots (shared memory).
Left: two or three people as simple shapes without faces, in teal #0B6476 and ink #0E1330, connected to the
agent by thin dotted lines. Right: a clock and an envelope with small lightning marks for triggers.
Background, top right: a large soft shield with a key in deep violet #3F2BA8 at low opacity. Rust #9A3B12
accent dots. Modern SaaS editorial illustration, soft drop shadows, empty space on the left third.
No text, no letters, no numbers, no logos, no brand marks, no realistic faces.
```

## When the result is wrong

| Problem | Fix |
| --- | --- |
| Garbled text or labels appear | Repeat "no text, no letters" at the start and end; add "blank" to cards and badges |
| Logos or Microsoft-like icons | Add the logo names to the negative prompt; describe icons as simple shapes |
| Too busy | Cut elements to 3–5; add "generous white space, minimal" |
| Wrong colors | Name the hex values per element, not as a list at the end |
| Looks like a photo or 3D | Start the prompt with "flat vector illustration" |
| Subject cropped on LinkedIn | Keep the subject in the center; ask for "subject centered, wide margins" |

## Generators

Use whatever the user has. Check the tool's current model names and pricing on its own site; they change often.

| Need | Good fit |
| --- | --- |
| General illustrations, editing an existing image | Gemini image models, OpenAI GPT Image models |
| Short text in the image | Ideogram |
| Consistent style across a series | A generator that accepts reference images (Flux, Gemini): pass an earlier aidevme image as the style reference |
