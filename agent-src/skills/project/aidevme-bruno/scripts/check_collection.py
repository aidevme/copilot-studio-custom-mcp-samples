#!/usr/bin/env python3
"""Check the aidevme.com Bruno collection (OpenCollection YAML) before it is used or committed.

Fails (exit 1) when:
  - a request uses any method other than GET or HEAD (aidevme.com is read-only for assistants);
  - a request URL does not start with {{baseUrl}};
  - a request has no status check (a res.status assertion or a test that reads the status);
  - auth or an environment variable holds a literal credential instead of a {{...}} reference;
  - opencollection.yml has no browser User-Agent header (the site firewall answers 406 to short ones);
  - two requests in one folder share a seq number, or a request file has no info.name.

Standard library only; the collection's own files are simple enough for line-based checks.

Usage:
  python check_collection.py <collection-folder>
"""
import argparse
import re
import sys
from pathlib import Path

ALLOWED_METHODS = {"GET", "HEAD"}
CREDENTIAL_KEYS = re.compile(r"^\s*(password|username|token|apiKey|api_key|secret)\s*:\s*(.*)$", re.I)
CREDENTIAL_VAR_NAMES = re.compile(r"(password|passwd|token|secret|apikey|api_key)", re.I)
REFERENCE = re.compile(r"""^["']?\{\{[^}]+\}\}["']?$""")


def value_of(line):
    """Return the scalar after the first colon, without quotes."""
    return line.split(":", 1)[1].strip().strip("'\"")


def check_request(path, problems):
    text = path.read_text(encoding="utf-8")
    rel = path.as_posix()
    info = {}
    in_info = False
    for line in text.splitlines():
        if re.match(r"^info:\s*$", line):
            in_info = True
            continue
        if in_info and re.match(r"^\S", line):
            in_info = False
        if in_info:
            m = re.match(r"^\s+(name|type|seq):\s*(.*)$", line)
            if m:
                info[m.group(1)] = m.group(2).strip().strip("'\"")

    if not info.get("name"):
        problems.append(f"{rel}: no info.name")

    methods = re.findall(r"^\s+method:\s*(\S+)", text, re.M)
    if not methods:
        problems.append(f"{rel}: no http.method")
    for method in methods:
        if method.strip("'\"").upper() not in ALLOWED_METHODS:
            problems.append(f"{rel}: method {method} - only GET or HEAD; aidevme.com is read-only for assistants")

    urls = re.findall(r"^\s+url:\s*(.+)$", text, re.M)
    for url in urls:
        if not url.strip().strip("'\"").startswith("{{baseUrl}}"):
            problems.append(f"{rel}: url does not start with {{{{baseUrl}}}}: {url.strip()}")

    has_status_assertion = re.search(r"expression:\s*res\.status", text)
    has_status_test = re.search(r"res\.getStatus\(\)|res\.status\b", text)
    if not (has_status_assertion or has_status_test):
        problems.append(f"{rel}: no status check (add a res.status assertion)")

    for line in text.splitlines():
        m = CREDENTIAL_KEYS.match(line)
        if m and m.group(2).strip() and not REFERENCE.match(m.group(2).strip()):
            problems.append(f"{rel}: literal {m.group(1)} - use a {{{{variable}}}} that reads process.env")
    if re.search(r"Authorization", text, re.I) and re.search(r"(Basic|Bearer)\s+[A-Za-z0-9+/=._-]{8,}", text):
        problems.append(f"{rel}: literal Authorization header value")

    return info.get("seq")


def check_environment(path, problems):
    rel = path.as_posix()
    current = None
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\s*-\s*name:\s*(.+)$", line) or re.match(r"^\s+name:\s*(.+)$", line)
        if m:
            current = m.group(1).strip().strip("'\"")
            continue
        m = re.match(r"^\s+value:\s*(.*)$", line)
        if m and current and CREDENTIAL_VAR_NAMES.search(current):
            value = m.group(1).strip()
            if value not in ("", "''", '""') and not REFERENCE.match(value):
                problems.append(f"{rel}: variable {current} holds a literal value - use '{{{{process.env.NAME}}}}'")


def check_root(path, problems):
    text = path.read_text(encoding="utf-8")
    if not re.search(r"^opencollection:\s*", text, re.M):
        problems.append(f"{path.as_posix()}: no opencollection version")
    ua = re.search(r"name:\s*User-Agent\s*\n\s+value:\s*(.+)", text)
    if not ua or "Mozilla/" not in ua.group(1):
        problems.append(f"{path.as_posix()}: no browser User-Agent header in request.headers (the firewall answers 406)")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("collection", help="Folder that holds opencollection.yml")
    args = parser.parse_args()

    root = Path(args.collection)
    problems = []
    root_file = root / "opencollection.yml"
    if not root_file.is_file():
        print(f"ERROR: {root_file} not found - is this an OpenCollection YAML collection?", file=sys.stderr)
        return 2
    check_root(root_file, problems)

    for env in sorted((root / "environments").glob("*.yml")):
        check_environment(env, problems)

    if (root / ".env").is_file():
        print("NOTE: .env present - make sure it stays untracked (git check-ignore -v .env).")

    requests = 0
    seqs = {}
    for path in sorted(root.rglob("*.yml")):
        if path.name in ("opencollection.yml", "folder.yml") or "environments" in path.relative_to(root).parts:
            continue
        if any(part in ("node_modules", ".git") for part in path.parts):
            continue
        requests += 1
        seq = check_request(path, problems)
        if seq:
            key = (path.parent, seq)
            if key in seqs:
                problems.append(f"{path.as_posix()}: seq {seq} also used by {seqs[key].name}")
            seqs[key] = path

    if problems:
        print(f"FAILED: {len(problems)} problem(s) in {requests} request(s)")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print(f"OK: {requests} request(s) checked - GET only, {{{{baseUrl}}}} URLs, status checks, no literal credentials, browser User-Agent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
