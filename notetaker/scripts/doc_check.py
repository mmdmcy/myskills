#!/usr/bin/env python3
"""Check a repository's documentation against the documentation model.

Docs drift the way code does; this makes the drift a failing check instead of
something an agent has to notice. Run it in a repository's tests:

    python3 doc_check.py [--root DIR] [--config docs-check.toml] [--format json]

Exit 0: clean. Exit 1: findings (each names the file and what to do).
Exit 2: the config or the root could not be read.

Without a config the model's defaults apply (references/doc-model.md):
root AGENTS.md/CLAUDE.md 150 lines, package AGENTS.md 60, other docs 400,
a contents list past 100 lines, every relative link resolves, every page under
docs/ is linked from somewhere. A `docs-check.toml` in the root may set:

    index = "docs/handbook.md"          # 200 lines
    open_list = "../fleet/OPEN.md"       # 110 lines; only open list
    skip = ["docs/archive/", "docs/decisions/", "docs/reports/"]
    no_limit = ["docs/changelog.md"]
    [[covers]]                           # every name the command prints
    file = "docs/commands.md"            # (one per line) appears in file
    command = "mytool list-commands"
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path

LIMITS = {"root": 150, "package": 60, "index": 200, "open": 110, "page": 400}
CONTENTS_FROM = 100
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
# A doc map often names a page as code, `docs/page.md`: that counts as a link.
CODE_PATH = re.compile(r"`([\w./-]+\.md)`")
OPEN_HEADING = re.compile(r"^#{1,4}\s+.*\b(open items|loose ends|todo|next steps)\b", re.I)
SKIP_DIRS = {".git", "node_modules", "target", "vendor", "dist", "build", ".next", ".claude"}


def markdown_files(root, skip):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for name in filenames:
            if name.endswith(".md"):
                path = Path(dirpath, name)
                rel = path.relative_to(root).as_posix()
                if not any(rel.startswith(prefix) for prefix in skip):
                    yield path, rel


def kind_of(rel, config):
    if rel == config.get("index"):
        return "index"
    if rel in ("AGENTS.md", "CLAUDE.md"):
        return "root"
    if rel.endswith("/AGENTS.md") or rel.endswith("/CLAUDE.md"):
        return "package"
    return "page"


def slug(heading):
    """GitHub's anchor for a heading."""
    text = re.sub(r"[`*_]", "", heading.strip().lower())
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def add_contents(path, lines):
    """Insert a contents line, made from the page's ## headings, under its title."""
    headings = []
    in_code = False
    for line in lines:
        if line.lstrip().startswith("```"):
            in_code = not in_code
        elif not in_code and line.startswith("## "):
            headings.append(line[3:].strip())
    if len(headings) < 2:
        return False
    title = next((n for n, line in enumerate(lines) if line.startswith("# ")), -1)
    entry = "Contents: " + " · ".join(f"[{h}](#{slug(h)})" for h in headings)
    lines[title + 1:title + 1] = ["", entry]
    path.write_text("\n".join(lines))
    return True


def check(root, config, fix=False, fixed=None):
    found = []
    fixed = fixed if fixed is not None else []
    skip = config.get("skip", [])
    no_limit = set(config.get("no_limit", []))
    files = dict((rel, path) for path, rel in markdown_files(root, skip))
    linked = set()
    for rel, path in files.items():
        text = path.read_text(errors="replace")
        # splitlines: a final newline does not count as one more line.
        lines = text.splitlines()
        kind = kind_of(rel, config)
        limit = LIMITS[kind]
        if rel not in no_limit and len(lines) > limit:
            found.append((rel, f"{len(lines)} lines, over the {kind} limit of {limit}: split it by topic and leave one line with a link"))
        head = "\n".join(lines[:25]).lower()
        if rel.startswith("docs/") and kind == "page" and rel not in no_limit and len(lines) > CONTENTS_FROM and "contents" not in head:
            if fix and add_contents(path, lines):
                fixed.append(rel)
            else:
                found.append((rel, f"{len(lines)} lines without a contents list near the top (--fix adds one from its headings)"))
        in_code = False
        for number, line in enumerate(lines, 1):
            if line.lstrip().startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                continue
            if OPEN_HEADING.match(line) and config.get("open_list"):
                found.append((rel, f"line {number}: an open-items section; open work belongs in {config['open_list']}"))
            for named in CODE_PATH.findall(line):
                for base in (path.parent, root):
                    candidate = (base / named).resolve()
                    if candidate.exists():
                        try:
                            linked.add(candidate.relative_to(root.resolve()).as_posix())
                        except ValueError:
                            pass
            for target in LINK.findall(line):
                if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith("#"):
                    continue
                clean = target.split("#", 1)[0]
                if not clean:
                    continue
                resolved = (path.parent / clean).resolve()
                try:
                    linked.add(resolved.relative_to(root.resolve()).as_posix())
                except ValueError:
                    pass
                if not resolved.exists():
                    found.append((rel, f"line {number}: link to {target}, which does not exist"))
    for rel in files:
        if rel.startswith("docs/") and kind_of(rel, config) == "page" and rel not in linked:
            found.append((rel, "no other doc links to it: add its line to the index or doc map"))
    open_list = config.get("open_list")
    if open_list:
        path = (root / open_list).resolve()
        if path.exists():
            count = len(path.read_text(errors="replace").splitlines())
            if count > LIMITS["open"]:
                found.append((open_list, f"{count} lines, over the open list's limit of {LIMITS['open']}: move detail to a page and keep one line with a link"))
    for cover in config.get("covers", []):
        doc = root / cover["file"]
        try:
            names = subprocess.run(cover["command"], shell=True, capture_output=True, text=True, timeout=120, cwd=root, check=True).stdout.split()
        except (subprocess.SubprocessError, OSError) as error:
            found.append((cover["file"], f"could not list what it must cover ({cover['command']}): {error}"))
            continue
        text = doc.read_text(errors="replace") if doc.exists() else ""
        for name in names:
            if not re.search(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])", text):
                found.append((cover["file"], f"does not mention {name} ({cover['command']} lists it)"))
    return found


def main():
    parser = argparse.ArgumentParser(description="Check documentation against the documentation model.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--config")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--fix", action="store_true", help="add the contents lists it can make from headings")
    args = parser.parse_args()
    root = Path(args.root)
    config_path = Path(args.config) if args.config else root / "docs-check.toml"
    try:
        config = tomllib.loads(config_path.read_text()) if config_path.exists() else {}
    except (OSError, tomllib.TOMLDecodeError) as error:
        print(f"doc_check: {config_path}: {error}", file=sys.stderr)
        return 2
    if not root.is_dir():
        print(f"doc_check: {root} is not a folder", file=sys.stderr)
        return 2
    fixed = []
    found = check(root, config, args.fix, fixed)
    for rel in fixed:
        print(f"docs: added a contents list to {rel}", file=sys.stderr)
    if args.format == "json":
        print(json.dumps({"schema_version": "doc-check.v1", "ok": not found, "findings": [{"file": f, "finding": m} for f, m in found]}))
    elif found:
        print(f"docs: {len(found)} finding(s)")
        for file, message in found:
            print(f"  {file}: {message}")
    else:
        print("docs: ok")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
