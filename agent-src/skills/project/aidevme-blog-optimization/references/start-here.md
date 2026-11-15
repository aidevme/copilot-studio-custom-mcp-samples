# Start Here page

<!-- cspell:ignore aidevme Dataverse -->

The page to link from LinkedIn, conference slides and speaker bios. Its job: in one screen, tell a new
visitor what AIDevMe is for, prove the author is credible, and route them to the right guides.

## Structure

| # | Section | Content |
| --- | --- | --- |
| 1 | Opening | The positioning line in plain words: pro-code Power Platform in the age of AI agents, for architects and pro developers |
| 2 | Who writes this | Microsoft MVP (Copilot Studio and Power Apps), Senior Solution Architect, 25+ years in the Microsoft ecosystem, PL-600 / PL-400 — verified, no invented numbers |
| 3 | Build with AI | Two-line description + 2–3 guides |
| 4 | Build AI agents | Two-line description + 2–3 guides |
| 5 | Pro-code Power Platform | Two-line description + 2–3 guides |
| 6 | Also here | ALM and governance; open-source tools; talks |
| 7 | Newsletter | One primary signup with a concrete promise (what arrives, how often) |

## Copy rules

- Use the voice profile in `.claude/agents/aidevme-context.md` (technical mode, but warmer and shorter).
- Each guide link: title + one line on what the reader gets.
- Pick guides that are evergreen and on-positioning; check performance with **aidevme-google-analytics**.
- Numbers (subscribers, years) only when verified; otherwise placeholder + [VERIFY].
- Suggest an SEO title, a 150–160-character meta description and the slug `start-here` (keep it stable once
  linked from slides and bios).
