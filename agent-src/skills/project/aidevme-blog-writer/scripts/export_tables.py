#!/usr/bin/env python3
"""Export every Markdown table in an aidevme draft as a WordPress table block, one HTML file per table.

Reads .content/wordpress-posts/<slug>/index.md and writes .content/wordpress-posts/<slug>/tables/<NN>-<heading>.html, where NN is the table's
position in the post and <heading> is the slug of the heading above it. Each file holds one block:

  <figure class="wp-block-table"><table class="has-fixed-layout"><tbody><tr><td>…</td></tr>…</tbody></table></figure>

Every row, including the header row, is a <tr> of <td> cells inside <tbody>. Inline Markdown in cells becomes
HTML (**bold** → <strong>, *italic* → <em>, `code` → <code>, [text](url) → <a>). The Markdown table stays the
source of truth: re-run after editing a table, and earlier exports (NN-*.html) are replaced. Tables inside fenced
code blocks are ignored. Standard library only.

Usage:
  python export_tables.py .content/wordpress-posts/<slug>/index.md
"""
import html
import pathlib
import re
import sys

SEPARATOR = re.compile(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")


def slugify(text, limit=50):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    if len(slug) > limit:
        slug = slug[:limit + 1].rsplit("-", 1)[0]  # cut at a word boundary
    return slug or "table"


def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    return [cell.strip().replace("\\|", "|") for cell in re.split(r"(?<!\\)\|", line)]


def inline(text):
    codes = []

    def keep_code(match):
        codes.append(html.escape(match.group(1), quote=False))
        return f"\x00{len(codes) - 1}\x00"

    text = re.sub(r"`([^`]+)`", keep_code, text)
    text = html.escape(text, quote=False)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: f"<code>{codes[int(m.group(1))]}</code>", text)


def tables(markdown):
    """Yield (heading, rows) for each GitHub-flavoured Markdown table outside fenced code."""
    lines = markdown.replace("\r\n", "\n").split("\n")
    heading, in_code, i = "", False, 0
    while i < len(lines):
        line = lines[i]
        if line.lstrip().startswith("```"):
            in_code = not in_code
        elif not in_code:
            match = re.match(r"^#{2,6}\s+(.*)", line)
            if match:
                heading = match.group(1).strip()
            elif line.lstrip().startswith("|") and i + 1 < len(lines) and SEPARATOR.match(lines[i + 1].strip()):
                rows = [split_row(line)]
                i += 2
                while i < len(lines) and lines[i].lstrip().startswith("|"):
                    rows.append(split_row(lines[i]))
                    i += 1
                yield heading, rows
                continue
        i += 1


def block(rows):
    body = "".join("<tr>" + "".join(f"<td>{inline(cell)}</td>" for cell in row) + "</tr>" for row in rows)
    return f'<figure class="wp-block-table"><table class="has-fixed-layout"><tbody>{body}</tbody></table></figure>\n'


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    source = pathlib.Path(sys.argv[1])
    out_dir = source.parent / "tables"
    out_dir.mkdir(exist_ok=True)
    for old in out_dir.glob("[0-9][0-9]-*.html"):
        old.unlink()
    count = 0
    for count, (heading, rows) in enumerate(tables(source.read_text(encoding="utf-8")), start=1):
        target = out_dir / f"{count:02d}-{slugify(heading)}.html"
        target.write_text(block(rows), encoding="utf-8", newline="\n")
        print(f"{target.as_posix()}  ({len(rows)} rows x {len(rows[0])} columns, under \"{heading}\")")
    print(f"{count} table(s) exported to {out_dir.as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
