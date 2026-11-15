---
name: aidevme-image
metadata:
  layer: atomic
  scope: project
  version: 1.0.0
description: |
  Define, generate and check images for aidevme.com posts and their promotion: the featured image (also
  the Open Graph / LinkedIn preview), in-post illustrations, LinkedIn and newsletter graphics and GitHub social
  previews. Writes an AI image prompt in the aidevme visual style, with file name, size, alt text and description,
  into the post folder's `image-generation-prompts.md`, then checks the file's size and dimensions. Use when: (1) the
  user asks for a featured, hero, cover or OG image or a social preview; (2) "image generation prompt", "generate
  an image", "create a graphic" or "alt text for this image"; (3) aidevme-blog-writer reaches its Illustrate step;
  (4) an image is too large or the wrong size for WordPress; (5) "media audit", "which images have no WebP
  version", or the media-audit workflow. Does NOT draw diagrams (use aidevme-diagram-mermaid or
  aidevme-diagram-drawio), fake product UI or screenshots, write the post (aidevme-blog-writer) or social copy
  (aidevme-social), or upload to WordPress.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
argument-hint: "<.content/wordpress-posts/<slug>/> [featured | inline <section> | linkedin | github]"
---

# aidevme-image

<!-- cspell:ignore aidevme Yoast Zsolt frontmatter cwebp -->

Images for aidevme.com that look like one site, describe themselves for search and screen readers, and load
fast. The skill writes the prompt and the metadata; the image is generated with a tool the user has
(Gemini, ChatGPT, Flux, Ideogram or similar) and then checked.

## Before starting

1. **Read the post** (`.content/wordpress-posts/<slug>/index.md` or the post's Markdown file) and
   `.claude/agents/aidevme-context.md` for positioning and audience.
2. **Read `.content/wordpress-posts/<slug>/image-generation-prompts.md`** if it exists. Add to it; don't overwrite earlier
   entries.
3. **Clarify only what's missing:** which image (featured first, unless the user says otherwise), and which
   generator the user will use. Default: featured image, any generator.

## Choose the right kind of image

| Need | Approach |
| --- | --- |
| Featured image, concept illustration, LinkedIn graphic | AI generation with the prompt from this skill |
| Process, architecture, data model, sequence | A diagram: **aidevme-diagram-mermaid** (or **aidevme-diagram-drawio** for branded layouts), never AI art |
| Power Platform, Copilot Studio or admin center UI | A real screenshot with demo data. AI hallucinates interfaces and settings. |
| Logos, product icons | Not generated. Microsoft and other logos are trademarks; leave them out. |
| Text in the image (title, tagline) | Add it afterwards in a design tool, or use a generator known for text (Ideogram). Keep it to 3–5 words. |

## Sizes

| Placement | Size | Ratio | Notes |
| --- | --- | --- | --- |
| Featured image (WordPress, Open Graph, LinkedIn link preview) | 1200 × 630 | 1.91:1 | One image covers all three; keep key content in the center 1000 px |
| In-post illustration | 1200 × 675 | 16:9 | Full content width |
| LinkedIn feed image | 1200 × 627 | 1.91:1 | Or 1080 × 1350 (4:5) for more feed space |
| LinkedIn document / carousel slide | 1080 × 1350 | 4:5 | Made with aidevme-social |
| GitHub social preview (aidevme repos) | 1280 × 640 | 2:1 | Repo Settings → Social preview |

Generators often return a larger image in the same ratio (for example 1734 × 907). That's fine; the check
below flags only a wrong ratio.

## Visual style

One style across the site. Colors come from the approved mockup in aidevme-blog-optimization
(`references/homepage-blueprint.md`, *Visual direction*):

| Role | Color |
| --- | --- |
| Accent | Violet `#5B3FD6` |
| Deep accent | `#3F2BA8` |
| Pillar tints | Teal `#0B6476`, rust `#9A3B12` |
| Ink | `#0E1330` |
| Background | Soft ground `#F5F6FB` |

- **Style:** flat vector editorial illustration, clean geometric shapes, soft shadows, generous white space.
- **Always:** one clear visual metaphor for the post's main point; empty space on one third for an optional title.
- **Never:** text, letters or numbers in the generated image; logos or brand marks; realistic human faces;
  fake UI; dark neon "AI" clichés (glowing brains, robots shaking hands).

## Workflow

### 1. Concept

Find the one idea the reader should take from the post (usually the angle sentence or the H1). Turn it into a
visual metaphor with 3–5 concrete elements. For example: an agent with its own account becomes "an agent
sitting at the team table with its own ID badge, mailbox and chat window, under a governance shield". Offer
two concepts when the post has no obvious one.

### 2. Prompt

Structure: **subject + setting + style + colors + composition + exclusions**, 60–150 words. Patterns and
examples: [references/prompting.md](references/prompting.md).

### 3. Alt text, caption, description and locations

- **Alt text:** what the image shows and why it matters for this post, ≤ 125 characters, no "image of", no
  keyword stuffing. It goes into `featured_image_alt` and the media library's Alt Text field.
- **Caption:** one sentence shown under the image (the media library's Caption field and `<figcaption>`): the
  point the image makes for the reader, in the article's voice. It doesn't repeat the alt text.
- **Description:** 3–5 sentences for the media library's Description field: the scene, its elements and the
  point it makes.
- **Image generation prompt:** a link from the entry's table to its prompt section below the table, so the long
  prompt stays readable.
- **GitHub repo URL:** the file's path in the repo on `main`,
  `https://github.com/aidevme/aidevme-blog/blob/main/.content/wordpress-posts/<slug>/images/<file>`. The repo is private, so this is
  a source-of-truth reference, never an image URL for the blog.
- **Azure Blob Storage URL:** `{AZURE_BLOB_BASE_URL}/<slug>/<file>`, with the base URL defined once at the top of the
  prompts file. Never invent the storage account or container; leave the placeholder until Zsolt gives them.
- **File name:** descriptive, lowercase, hyphenated, `.png` (for example
  `copilot-studio-agent-account-identity.png`), never `image1.png` or only `featured.png`.

### 4. Write the entry

Append the entry to `.content/wordpress-posts/<slug>/image-generation-prompts.md` in the format of
[`.content/templates/wordpress-post-template/image-generation-prompts.md`](../../../.content/templates/wordpress-post-template/image-generation-prompts.md): file
name, size, placement (in-post images), alt text, caption, description, image generation prompt link, GitHub repo
URL, Azure Blob Storage URL, the prompt, the negative prompt and, for a featured image, the frontmatter lines. Add a
line for the entry to the file's Contents list. Show the same fields in the reply.

### 5. Generate (when asked)

Generate only when the user asks, with a tool that's available (for example a Gemini image skill or MCP
server). Otherwise hand over the prompt. Save the result as `.content/wordpress-posts/<slug>/images/<file name>`.

### 6. Check and finish

```bash
python .claude/skills/aidevme-image/scripts/check_image.py .content/wordpress-posts/<slug>/images/<file>.png --placement featured
```

- Checks format, dimensions, ratio for the placement, and file size. Use `python3` on Linux and macOS.
- Over the size budget (featured image ≤ 300 KB, in-post ≤ 200 KB): convert to WebP or JPEG at quality 80–85
  before uploading (`cwebp -q 82 in.png -o out.webp`, or export from any image editor). WordPress builds its
  own resized versions, but the original is what Open Graph and LinkedIn fetch.
- Look at the image: no garbled text, no logos, no extra fingers or broken shapes, colors close to the palette.
  If it fails, adjust the prompt (add the problem to the exclusions) and regenerate.
- For a featured image, update the post's frontmatter: `featured_image` and `featured_image_alt`.

## Media library audit

Lists every file in the WordPress media library and checks whether each image has an optimized version. The
weekly `media-audit` GitHub workflow runs the same script and reports the result as a `[Media audit]` issue.

```bash
python .claude/skills/aidevme-image/scripts/audit_media.py --out-dir <scratch dir> [--max-kb 300]
```

- Reads the public REST API (`wp-json/wp/v2/media`) with a browser user agent; read-only, standard library only.
- **Optimized** means the library also holds a WebP or AVIF attachment with the same base file name as the PNG,
  JPEG, GIF, BMP or TIFF original (the house convention: upload the PNG and its WebP side by side). WordPress's
  `-scaled` suffix is ignored when matching.
- Flags originals **missing an optimized version** and WebP or AVIF files **over the size budget** (default
  300 KB, the featured-image budget). SVG, PDF and video are listed but not checked.
- Writes `media-inventory.csv` (every item with its status) and `media-audit.md` (summary and the items that need
  attention, under 60,000 characters for an issue body). Write them to a scratch folder, not the repo.
- Fixes are Zsolt's: convert with `cwebp -q 82 in.png -o out.webp` (or re-export smaller) and upload in WordPress.

## Rules

- **Facts stay in the text.** An image illustrates; it never shows numbers, prices, UI or claims the post
  doesn't make.
- **No client data, people or logos.** Demo data only in screenshots; no real faces; no trademarks.
- **Every image has alt text**, and the file name describes it.
- **Generated images aren't screenshots.** Never caption an AI image as a product view.

## Verify

- [ ] Concept matches the post's main point; the prompt follows the structure and the aidevme palette.
- [ ] File name descriptive; size and ratio right for the placement; alt text ≤ 125 characters; caption one
  sentence.
- [ ] GitHub and Azure Blob Storage URLs follow the file name; no invented storage account or container.
- [ ] Entry appended to `image-generation-prompts.md`; earlier entries untouched.
- [ ] If generated: `check_image.py` passes or the fix is stated; frontmatter updated for a featured image.
- [ ] No text, logos, faces or fake UI in the image.

## Related skills

- **aidevme-blog-writer:** calls this skill in its Illustrate step
- **aidevme-diagram-mermaid** / **aidevme-diagram-drawio:** diagrams instead of illustrations
- **aidevme-social:** LinkedIn posts and carousels that use these images
- **aidevme-seo-audit:** image SEO on published posts (alt text, file names, size)
- **`media-audit` workflow** (`.github/workflows/media-audit.md`): runs the media library audit weekly
