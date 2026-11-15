# Homepage blueprint and visual direction

<!-- cspell:ignore aidevme Dataverse -->

## Setup

The homepage is a **static page** (Settings → Reading → "A static page"). The post feed moves to a separate
**/blog/** page set as the posts page.

## Sections, top to bottom

| # | Section | Content |
| --- | --- | --- |
| 1 | **Header** | Logo, the six-item menu, a search icon, a Subscribe button |
| 2 | **Hero** | Positioning headline, one-line subhead, **Start here** and **Get the newsletter** buttons, the comic portrait, name and role |
| 3 | **Credentials strip** | MVP areas, 25+ years in the Microsoft ecosystem, PL-600 and PL-400, the verified subscriber count |
| 4 | **Three pillars** | Build with AI, Build AI agents, Pro-code Power Platform — each with an icon, a two-line description and a link |
| 5 | **Flagship guides** | Three hand-picked evergreen posts, reviewed quarterly. Defaults: Canvas Apps vs Code Apps, Dataverse MCP Server, Dataverse Skills |
| 6 | **Latest posts** | Four cards with filter chips by pillar, plus "View all posts" |
| 7 | **Speaking and open source** (side by side) | Next confirmed talk plus recent sessions · GitHub tools with status badges |
| 8 | **Newsletter block** | One primary signup (either the LinkedIn newsletter or the on-site form), a clear promise, an email field with a label |
| 9 | **Footer** | LinkedIn, GitHub, YouTube, About, FAQ, Contact, Disclaimer — social icons live here, not in the header |

The homepage has **no sidebar, tag cloud or recent-comments widget**. Single posts keep the sidebar.

Before showing numbers (subscribers, years) or a talk, verify them: numbers from Zsolt, events by checking the
event page for date and status. Unverified → `[500+]`-style placeholder plus [VERIFY].

## Flagship review (quarterly)

Pick from evergreen posts that match the positioning and perform well (engaged sessions and returning
readers via **aidevme-google-analytics**). A news post is never a flagship; replace a flagship only with a
post that's stronger on both fit and performance.

## Visual direction (from the approved mockup)

| Token | Value |
| --- | --- |
| Accent | Violet `#5B3FD6` (links `#3F2BA8`) |
| Pillar tints | Teal `#0B6476`, rust `#9A3B12` |
| Ink | `#0E1330` |
| Muted text | `#4A5068` |
| Soft ground | `#F5F6FB` |
| Card border | 1px `#E4E6EF`, 14–22px radius |
| Headings | Sora |
| Body | IBM Plex Sans |
| Eyebrow labels | IBM Plex Mono, small |

- Flat cards; **no gradients or drop shadows**.
- Touch targets at least 44px; text contrast at least 4.5:1 (check tints against white and the soft ground).
- The comic-style portrait is the brand's signature image and belongs in the hero.

## Delivering a mockup

- Quick look: an inline mockup (HTML/CSS using the tokens above).
- Editable or exportable: a Design artifact.
- Always pair it with WordPress click paths (Appearance → Menus, Settings → Reading, Posts → Categories,
  theme/block editor sections) and the redirect list from
  [pillars-and-categories.md](pillars-and-categories.md#redirects).
