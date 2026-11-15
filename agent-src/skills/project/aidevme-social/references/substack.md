# Substack for aidevme

<!-- cspell:ignore aidevme Dataverse Substack substack repost restack restacking Zsolt -->

Substack is two channels in one: **posts**, which go to subscribers by email and live on the publication's site,
and **Notes**, a short-form feed inside the Substack app. aidevme.com stays the home of every article; Substack
brings it to readers who prefer email and to Substack's own network.

## Contents

- Cross-posting and search
- Post fields
- Post formats
- Structure of an adapted post
- Notes
- Voice and style
- Checklist

## Cross-posting and search

Substack has no setting for a canonical URL or `noindex` on a post, so a full copy of a blog post on Substack is
a second, competing page for the same content. Google's guidance on syndicated content recommends against
relying on cross-domain canonicals and suggests the copies block indexing instead, which Substack doesn't let you
do. Checked 2026-10-25; see the sources at the end.

That leads to the default: **write an adapted post for Substack and link to the full article on aidevme.com.**
The adapted post is useful on its own, sends readers to the blog, and doesn't compete with it in search.

| Format | When | Search risk |
| --- | --- | --- |
| **Adapted post** (default) | Every new aidevme article | Low: different text, links to the original |
| **Full repost** | Only when Zsolt asks; publish at least a few days after the blog post, with "Originally published on aidevme.com" and a link at the top | Real: the Substack copy can outrank the original. Say so and let Zsolt decide |
| **Roundup** | Monthly: what was published, what changed in the ecosystem, one tool or skill | Low |
| **Substack-only** | A personal or opinion piece that doesn't belong on the blog | None |

## Post fields

| Field | What it does | aidevme rule |
| --- | --- | --- |
| Title | The headline on the site and the **email subject line** | Short and specific, under ~60 characters; the reader's outcome or the problem, not the blog title copied |
| Subtitle | Shown under the title and in the **email preview**; the default SEO description | One sentence that makes the email worth opening |
| SEO title | Title tag in search results (Settings → SEO options) | Leave the default unless the title is too short to be found; under 60 characters |
| SEO description | Meta description; defaults to the subtitle | 150–160 characters when you set it |
| Post URL | Slug generated from the title | Edit only before publishing; lowercase, hyphenated, no dates |
| Social preview image | Defaults to the first image in the post | The post's featured image from **aidevme-image** (1200 × 630) |
| Email sending | Send to everyone, or publish on the web only | Zsolt decides when publishing; the draft says which is intended |

SEO title, SEO description and the social preview don't change how the post looks in the email or the app.

## Post formats

- **Length:** an adapted post is 400–900 words, so it reads in 2–4 minutes in an inbox. A roundup is 300–700 words.
- **Images:** one at the top (the featured image) and at most one diagram or screenshot in the body. Use images
  from the post's `images/` folder with their alt text.
- **Code:** a short snippet (up to ~10 lines) works in email; anything longer stays on the blog, with a link.
- **Links:** one primary link to the full article, repeated at the end. A few supporting links are fine; a link
  in every paragraph reads like a link list.
- **Headings:** two or three H2s at most; a newsletter reads as one piece.

## Structure of an adapted post

1. **Opening (2–3 sentences):** the moment or problem from the article, told for this reader: a real error, a
   decision someone faces, what changed.
2. **The insight:** the article's main point in one short paragraph, answer first.
3. **Three takeaways:** what the reader can do or check, each one sentence with its reason. Specific, from the
   article; no new facts.
4. **One proof:** a number, error message, short snippet or diagram from the article.
5. **What the full article adds:** one or two sentences on what's only on the blog (the full setup, the checklist,
   the code), then the link: "Read the full guide on aidevme.com".
6. **Close:** a real question you want answered ("Which process would you trust an agent with first?"), plus
   the subscribe line if the post is shared outside email.

## Notes

Notes are short posts in the Substack app, closer to LinkedIn or Bluesky than to email.

- **Use them for:** the post's single sharpest insight on publish day; one gotcha or number a few days later;
  restacking (sharing) and commenting on posts from people in the Power Platform and AI-agents community.
- **Format:** 1–4 short paragraphs, the hook in the first line, the link to the Substack post or aidevme.com at
  the end. Up to 6 images or GIFs per Note, according to Substack's Notes FAQ.
- **Length:** Substack doesn't publish a character limit. Buffer documents 10,000 characters; keep Notes well
  under that, and check the app when a Note is long.
- **Cadence:** 2–4 Notes a week beats one long Note; reply to comments like on LinkedIn.

## Voice and style

- **Posts** are long-form prose: they follow the **blog** style rules in `.claude/agents/aidevme-context.md`
  (em dashes for asides are allowed, sparingly), in the Technical or Personal mode of the article.
- **Notes** follow the stricter social rules in `SKILL.md` ("No AI tells"): no em dashes, no contrast reveals, no
  engagement bait.
- Both: never "In this week's newsletter…" or "I'm excited to share…". Open with the problem or the moment.
- Every fact comes from the article or from Zsolt; nothing new is added in the adaptation.

## Checklist

- [ ] Format chosen deliberately; a full repost only on request, with the search risk stated.
- [ ] Title under ~60 characters and different from the blog title; subtitle works as the email preview.
- [ ] Opening tells the article's real moment; three takeaways from the article; one proof.
- [ ] One primary link to the full article on aidevme.com, at least at the end.
- [ ] Social preview image and alt text from the post's `images/` folder.
- [ ] Notes written separately, within the social style rules.
- [ ] Saved as `.content/wordpress-posts/<slug>/substack-post.md`; nothing published or sent without approval.

## Sources

- [A guide to SEO on Substack](https://on.substack.com/p/substack-seo-guide) — Substack (post SEO fields)
- [Notes FAQ](https://on.substack.com/p/notes-faq) — Substack (images per Note; no stated character limit)
- [Using Substack with Buffer](https://support.buffer.com/en-us/articles/using-substack-with-buffer-lDbUYyIq4R) — Buffer (10,000-character Notes)
- [June 2023 SEO office hours](https://developers.google.com/search/help/office-hours/2023/june) — Google Search Central (noindex for syndicated copies)
