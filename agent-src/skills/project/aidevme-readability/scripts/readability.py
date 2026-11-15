#!/usr/bin/env python3
"""Approximate the Yoast SEO readability analysis for an aidevme.com post.

Checks (English blog posts; limits from Yoast's scoring spec, yoastseo 3.3.0 "SCORING READABILITY.md"):
  1. Subheading distribution  section after a subheading < 300 words green, 300-350 orange, > 350 red;
                              no subheadings at all in a text over 300 words red (cornerstone: 50 words less)
  2. Paragraph length         <= 150 words green, 150-200 orange, > 200 red
  3. Sentence length          sentences over 20 words: <= 25% green, 25-30% orange, > 30% red
                              (cornerstone: <= 20% / 20-25% / > 25%)
  4. Consecutive sentences    3 or more sentences in a row starting with the same word: red
  5. Passive voice            <= 10% green, 10-15% orange, > 15% red
  6. Transition words         >= 30% of sentences green, 20-30% orange, < 20% red (only texts over 200 words)
  7. Text presence            under 50 characters: red
  9. Text alignment (Premium) centered paragraph or heading over 50 characters: red (HTML input only)
Not measured: 8. Word complexity (Premium) needs Yoast's word-frequency list; read it from Yoast.

Overall score: red adds 3 penalty points, orange 2. Under 4 points is green, 4-5 orange, 6 or more red.

Input: a Markdown draft (.content/wordpress-posts/<slug>/index.md), a saved HTML page, or an http(s) URL of a published post
(read through the WordPress REST API, falling back to the page HTML). Body text only: frontmatter, fenced code,
tables, images, HTML comments and everything from the "Resources" heading on are skipped. List items count as
sentences. The results approximate Yoast's analysis, so keep a margin below the limits. Standard library only.

Usage:
  python readability.py <file-or-url> [--cornerstone] [--list] [--json]
"""
import argparse
import html
import json
import re
import sys
import urllib.request

MAX_WORDS = 20

BE = r"\b(?:am|is|are|was|were|be|been|being|isn't|aren't|wasn't|weren't|get|gets|got|gotten|getting)\b"
ADVERBS = (r"(?:\s+(?:not|still|only|also|now|automatically|currently|explicitly|separately|then|already|never|"
           r"always|often|usually|easily|fully|first))*")
IRREGULAR = (
    "made|done|given|taken|shown|known|seen|written|built|sent|kept|held|set|put|run|left|found|told|brought|"
    "bought|paid|met|read|thrown|driven|hidden|chosen|frozen|spoken|broken|drawn|grown|begun|led|meant|spent|"
    "lost|won|understood|sold|cut|shut|hit|split|spread|bound|caught|taught|thought|fed|hung|laid|lit|"
    "sought|struck|sworn|torn|worn|woken|forgotten|forbidden|overridden|rewritten|undone"
)
PASSIVE = re.compile(BE + ADVERBS + r"\s+(?:\w+ed|" + IRREGULAR + r")\b", re.I)

# Common English transition words and phrases (our own list, not Yoast's; Yoast's list is longer).
TRANSITIONS = [
    "accordingly", "additionally", "after", "afterwards", "also", "although", "as a result", "as long as",
    "as soon as", "as well as", "at first", "at last", "at the same time", "because", "before", "besides",
    "but", "by contrast", "consequently", "conversely", "despite", "due to", "during", "earlier", "either",
    "especially", "even if", "even so", "even though", "eventually", "finally", "first", "firstly",
    "for example", "for instance", "for this reason", "furthermore", "hence", "however", "in addition",
    "in contrast", "in fact", "in other words", "in particular", "in practice", "in short", "in summary",
    "in the meantime", "indeed", "instead", "lastly", "later", "likewise", "meanwhile", "moreover",
    "namely", "nevertheless", "next", "nonetheless", "not only", "on the other hand", "once", "otherwise",
    "overall", "particularly", "previously", "rather", "second", "secondly", "similarly", "since", "so",
    "so that", "specifically", "still", "subsequently", "such as", "that's why", "then", "thereby",
    "therefore", "third", "though", "thus", "to illustrate", "to sum up", "ultimately", "unless", "until",
    "when", "whenever", "whereas", "while", "yet",
]
TRANSITION = re.compile(r"\b(?:" + "|".join(re.escape(t).replace(r"\ ", r"\s+") for t in TRANSITIONS) + r")\b",
                        re.I)
# When a sentence starts with one of these, Yoast-style beginnings compare the first two words.
BEGINNING_EXCEPTIONS = {"the", "a", "an", "this", "that", "these", "those", "one", "two", "three", "four",
                        "five", "six", "seven", "eight", "nine", "ten"}

SENTENCE_END = re.compile(r"(?<=[.!?])[\"”')\]]*\s+(?=[A-Z\"“(\[])")
ABBREVIATIONS = re.compile(r"\b(e\.g|i\.e|vs|etc|approx|Fig|No)\.", re.I)
LIST_ITEM = re.compile(r"^(?:\d+\.|[-*+])\s+")
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/126.0 Safari/537.36")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", "replace")


def load(source):
    if re.match(r"https?://", source):
        # A WordPress post's body is cleanest from the REST API; fall back to the page HTML.
        match = re.match(r"(https?://[^/]+)/([^/?#]+)/?$", source)
        if match:
            api = f"{match.group(1)}/wp-json/wp/v2/posts?slug={match.group(2)}&_fields=content"
            try:
                posts = json.loads(fetch(api))
                if posts:
                    return posts[0]["content"]["rendered"], "html"
            except (OSError, ValueError, KeyError):
                pass
        return fetch(source), "html"
    with open(source, encoding="utf-8") as fh:
        text = fh.read()
    return text, "html" if source.lower().endswith((".html", ".htm")) else "md"


def clean_inline(text):
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return re.sub(r"[*_`]", "", text).strip()


def items_from_markdown(text):
    """Return the body as an ordered list of (kind, text) with kind h, p or li."""
    text = re.sub(r"\A---\n.*?\n---\n", "", text.replace("\r\n", "\n"), flags=re.S)
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.split(r"\n#{2,6}\s+Resources\b", text)[0]
    items, kind, current = [], None, ""

    def flush():
        if current:
            items.append((kind, clean_inline(current)))

    for line in text.split("\n"):
        stripped = line.strip()
        heading = re.match(r"^#{2,6}\s+(.*)", stripped)
        if heading:
            flush()
            items.append(("h", clean_inline(heading.group(1))))
            kind, current = None, ""
        elif not stripped or stripped.startswith(("#", "|", "![", "<")):
            flush()
            kind, current = None, ""
        elif LIST_ITEM.match(stripped):
            flush()
            kind, current = "li", LIST_ITEM.sub("", stripped)
        else:
            if kind is None:
                kind = "p"
            current = f"{current} {stripped}".strip()
    flush()
    return items


def items_from_html(text):
    text = re.split(r"<h[2-6]\b[^>]*>(?:\s|<[^>]+>)*Resources\b", text, flags=re.I)[0]
    text = re.sub(r"<(script|style|pre|table|figure|nav|header|footer)\b.*?</\1>", " ", text, flags=re.S | re.I)
    items = []
    for match in re.finditer(r"<(h[2-6]|p|li)\b[^>]*>(.*?)</\1>", text, flags=re.S | re.I):
        tag, inner = match.group(1).lower(), match.group(2)
        # A list item that is only a link is navigation (table of contents, share buttons), not prose.
        if tag == "li" and re.fullmatch(r"\s*<a\b.*</a>\s*", inner, re.S):
            continue
        plain = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", inner))).strip()
        if plain:
            items.append(("h" if tag.startswith("h") else tag, plain))
    return items


def centered_long(text):
    found = []
    for match in re.finditer(r"<(p|h[1-6])\b[^>]*class=\"[^\"]*has-text-align-center[^\"]*\"[^>]*>(.*?)</\1>",
                             text, flags=re.S | re.I):
        plain = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", match.group(2)))).strip()
        if len(plain) > 50:
            found.append(plain)
    return found


def split_sentences(block):
    protected = ABBREVIATIONS.sub(lambda m: m.group(1) + "․", block)
    return [s.replace("․", ".").strip() for s in SENTENCE_END.split(protected)
            if len(s.split()) >= 2]


def words(text):
    return len(text.split())


def beginning(sentence):
    tokens = re.findall(r"[A-Za-z0-9'’]+", sentence.lower())
    if not tokens:
        return ""
    if tokens[0] in BEGINNING_EXCEPTIONS and len(tokens) > 1:
        return " ".join(tokens[:2])
    return tokens[0]


def light(value, green, red, higher_is_better=False):
    if higher_is_better:
        return "green" if value >= green else "red" if value < red else "orange"
    return "green" if value <= green else "red" if value > red else "orange"


def analyse(source, cornerstone=False):
    raw, kind = load(source)
    items = items_from_html(raw) if kind == "html" else items_from_markdown(raw)
    prose = [(k, t) for k, t in items if k != "h"]
    total_words = sum(words(t) for _, t in prose)
    total_chars = sum(len(t) for _, t in prose)
    sents = [s for _, t in prose for s in split_sentences(t)]
    n = len(sents) or 1
    checks = {}

    # 1. Subheading distribution
    sub_green, sub_red = (250, 300) if cornerstone else (300, 350)
    sections, current, title = [], 0, "(before the first subheading)"
    for k, t in items:
        if k == "h":
            sections.append((title, current))
            title, current = t, 0
        else:
            current += words(t)
    sections.append((title, current))
    has_headings = any(k == "h" for k, _ in items)
    if not has_headings:
        status = "red" if total_words > sub_green else "green"
        longest = total_words
    else:
        longest = max(w for _, w in sections)
        status = light(longest, sub_green - 1, sub_red)
    checks["subheading_distribution"] = {
        "value": f"longest section {longest} words", "status": status,
        "limit": f"< {sub_green} green, > {sub_red} red",
        "items": [{"section": s, "words": w} for s, w in sections if w >= sub_green]}

    # 2. Paragraph length
    paragraphs = [t for k, t in prose if k == "p"]
    longest_p = max((words(p) for p in paragraphs), default=0)
    checks["paragraph_length"] = {
        "value": f"longest paragraph {longest_p} words", "status": light(longest_p, 150, 200),
        "limit": "<= 150 green, > 200 red",
        "items": [{"words": words(p), "text": p} for p in paragraphs if words(p) > 150]}

    # 3. Sentence length
    long_ = [s for s in sents if words(s) > MAX_WORDS]
    pct = round(100 * len(long_) / n, 1)
    s_green, s_red = (20, 25) if cornerstone else (25, 30)
    checks["sentence_length"] = {
        "value": f"{pct}% over {MAX_WORDS} words ({len(long_)} of {len(sents)})", "percent": pct,
        "status": light(pct, s_green, s_red), "limit": f"<= {s_green}% green, > {s_red}% red",
        "items": [{"words": words(s), "text": s} for s in long_]}

    # 4. Consecutive sentences
    runs, run = [], [sents[0]] if sents else []
    for prev, cur in zip(sents, sents[1:]):
        if beginning(cur) and beginning(cur) == beginning(prev):
            run.append(cur)
        else:
            if len(run) >= 3:
                runs.append(run)
            run = [cur]
    if len(run) >= 3:
        runs.append(run)
    checks["consecutive_sentences"] = {
        "value": f"{len(runs)} run(s) of 3+ sentences with the same first word",
        "status": "red" if runs else "green", "limit": "no run of 3+",
        "items": [{"starts_with": beginning(r[0]), "sentences": r} for r in runs]}

    # 5. Passive voice
    passive = [s for s in sents if PASSIVE.search(s)]
    ppct = round(100 * len(passive) / n, 1)
    checks["passive_voice"] = {
        "value": f"{ppct}% ({len(passive)} of {len(sents)})", "percent": ppct,
        "status": light(ppct, 10, 15), "limit": "<= 10% green, > 15% red",
        "items": [{"text": s} for s in passive]}

    # 6. Transition words
    with_tw = [s for s in sents if TRANSITION.search(s)]
    tpct = round(100 * len(with_tw) / n, 1)
    if total_words > 200:
        tstatus = light(tpct, 30, 20, higher_is_better=True)
    else:
        tstatus = "green"
    checks["transition_words"] = {
        "value": f"{tpct}% of sentences ({len(with_tw)} of {len(sents)})", "percent": tpct,
        "status": tstatus, "limit": ">= 30% green, < 20% red (texts over 200 words)",
        "items": []}

    # 7. Text presence
    checks["text_presence"] = {
        "value": f"{total_chars} characters", "status": "red" if total_chars < 50 else "green",
        "limit": ">= 50 characters", "items": []}

    # 8. Word complexity: not measurable without Yoast's frequency list.
    checks["word_complexity"] = {
        "value": "not measured (Premium; read it from Yoast)", "status": "n/a",
        "limit": "< 10% complex words", "items": []}

    # 9. Text alignment
    if kind == "html":
        centered = centered_long(raw)
        checks["text_alignment"] = {
            "value": f"{len(centered)} centered block(s) over 50 characters",
            "status": "red" if centered else "green", "limit": "no centered block over 50 characters",
            "items": [{"text": c} for c in centered]}
    else:
        checks["text_alignment"] = {
            "value": "not applicable to Markdown (alignment is set in WordPress)", "status": "n/a",
            "limit": "no centered block over 50 characters", "items": []}

    points = sum(3 if c["status"] == "red" else 2 if c["status"] == "orange" else 0 for c in checks.values())
    overall = "green" if points < 4 else "orange" if points < 6 else "red"
    return {"source": source, "cornerstone": cornerstone, "words": total_words, "sentences": len(sents),
            "overall": {"status": overall, "penalty_points": points}, "checks": checks}


LABELS = {
    "subheading_distribution": "1. Subheading distribution",
    "paragraph_length": "2. Paragraph length",
    "sentence_length": "3. Sentence length",
    "consecutive_sentences": "4. Consecutive sentences",
    "passive_voice": "5. Passive voice",
    "transition_words": "6. Transition words",
    "text_presence": "7. Text presence",
    "word_complexity": "8. Word complexity",
    "text_alignment": "9. Text alignment",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("source", help="Markdown or HTML file, or an http(s) URL")
    parser.add_argument("--cornerstone", action="store_true", help="use Yoast's stricter cornerstone limits")
    parser.add_argument("--list", action="store_true", help="list what each failing check flagged")
    parser.add_argument("--json", action="store_true", help="print the full result as JSON")
    args = parser.parse_args()

    result = analyse(args.source, args.cornerstone)
    ok = all(c["status"] in ("green", "n/a") for c in result["checks"].values())
    if args.json:
        json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
        print()
        return 0 if ok else 1

    print(f"Source: {result['source']}{'  (cornerstone limits)' if result['cornerstone'] else ''}")
    print(f"Body: {result['words']} words, {result['sentences']} sentences")
    print(f"Overall: {result['overall']['status'].upper()} ({result['overall']['penalty_points']} penalty points)\n")
    for key, check in result["checks"].items():
        print(f"{LABELS[key]:<28} {check['status'].upper():<7} {check['value']}  [{check['limit']}]")
    if args.list:
        for key, check in result["checks"].items():
            if check["status"] in ("orange", "red") and check["items"]:
                print(f"\n--- {LABELS[key]}")
                for item in check["items"]:
                    if "sentences" in item:
                        print(f"  starts with '{item['starts_with']}':")
                        for s in item["sentences"]:
                            print(f"      | {s}")
                    elif "section" in item:
                        print(f"  {item['words']:>4} words | {item['section']}")
                    elif "words" in item:
                        print(f"  {item['words']:>4} | {item['text']}")
                    else:
                        print(f"       | {item['text']}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
