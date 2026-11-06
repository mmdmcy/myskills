#!/usr/bin/env python3
"""Check a repository's documentation against the documentation model.

Docs drift the way code does; this makes the drift a failing check instead of
something an agent has to notice. Run it in a repository's tests:

    python3 doc_check.py [--root DIR] [--config docs-check.toml] [--format json] [--staged]

Exit 0: clean. Exit 1: findings (each names the file and what to do).
Exit 2: the config or the root could not be read. Exit 4: no findings, but
notices (a reference page whose re-check is due).

Without a config the model's defaults apply (references/doc-model.md):
root AGENTS.md/CLAUDE.md 150 lines, package AGENTS.md 60, other docs 400,
a contents list past 100 lines, every relative link resolves, every page under
docs/ is linked from somewhere. A `docs-check.toml` in the root may set:

    index = "docs/handbook.md"          # 200 lines
    roots = ["agents/AGENTS.md"]         # also loaded every session: 150 lines
    open_list = "../fleet/OPEN.md"       # 110 lines; only open list
    skip = ["docs/archive/", "docs/decisions/", "docs/reports/"]
    no_limit = ["docs/changelog.md"]
    [[covers]]                           # every name the command prints
    file = "docs/commands.md"            # (one per line) appears in file
    command = "mytool list-commands"
    before = "(?:`|mytool )"             # optional: what must precede it

Structure rules, each only when its key is set (a folder ends with `/`; a
glob or `<name>` placeholder expands against the root):

    reach = ["."]                        # every page under these roots is linked from somewhere (default docs/)
    patterns = true                      # `apps/<app>/README.md` or `docs/x-*.md` in a doc counts as a link to every match
    state = ["docs/handbook/"]           # `State as of: YYYY-MM-DD` and `Owner:` in the first 10 lines, no dated ## heading
    state_grace_days = 7                 # the date may trail the page's last commit by this much
    decisions = "docs/decisions/"        # NNNN-slug.md, gapless, Date/Status/Decider, Superseded by NNNN exists, README.md links all
    frozen = ["docs/reports/"]           # YYYY-MM-DD-slug.md, not committed after its date plus the grace
    frozen_grace_days = 7
    frozen_ok = ["docs/reports/2026-01-01-x.md"]   # link-only edits the owner allowed
    changelog = "docs/changelog.md"      # touched when HEAD (or --staged) touches state, decisions, frozen or reference files; "decid" lines name ADR NNNN
    reference = "docs/reference/"        # `Checked on:` and `Re-check: every N days|weeks|months` (due: notice, exit 4) or `Re-check: when ...` (listed); README.md links all
    [[only_in]]                          # one home per fact: the pattern may appear only in files,
    pattern = "KVK \\\\d{8}"              # the frozen, decisions and archive folders and the changelog;
    files = ["docs/handbook/legal.md"]   # any other .md that matches is a finding
"""

import argparse
import calendar
import json
import os
import re
import subprocess
import sys
import tomllib
from datetime import date
from pathlib import Path

LIMITS = {"root": 150, "package": 60, "index": 200, "open": 110, "page": 400}
CONTENTS_FROM = 100
HEADER_LINES = 10
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
# A doc map often names a page as code, `docs/page.md`: that counts as a link.
CODE_PATH = re.compile(r"`([\w./-]+\.md)`")
# With patterns on, so does `apps/<app>/README.md` or `docs/stripe-*.md`, for every match.
CODE_PATTERN = re.compile(r"`([\w./<>*-]*[<*][\w./<>*-]*\.md|[\w./-]+\.md)`")
PLACEHOLDER = re.compile(r"<[^<>/]+>")
OPEN_HEADING = re.compile(r"^#{1,4}\s+.*\b(open items|loose ends|todo|next steps)\b", re.I)
DATE = re.compile(r"\d{4}-\d\d-\d\d")
DATED_HEADING = re.compile(r"^#{2,}\s.*\d{4}-\d\d-\d\d")
RECORD_NAME = re.compile(r"^(\d{4})-[\w.-]+\.md$")
DATED_NAME = re.compile(r"^(\d{4}-\d\d-\d\d)-[\w.-]+\.md$")
SUPERSEDED = re.compile(r"Superseded by\b(.*)")
NUMBER = re.compile(r"(?<![\d-])(\d{4})(?![\d-])")
ADR = re.compile(r"\bADR \d{4}\b")
EVERY = re.compile(r"^every (\d+) (day|week|month)s?\b")
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


def expand(base, entries):
    """The .md files the entries name: a folder (`docs/x/`, recursive), a glob,
    a `<name>` placeholder pattern or a path; absolute, resolved."""
    out = set()
    for entry in entries:
        pattern = PLACEHOLDER.sub("*", entry)
        if pattern in (".", "./"):
            pattern = "**/*.md"
        elif pattern.endswith("/"):
            pattern += "**/*.md"
        try:
            matches = list(base.glob(pattern))
        except (ValueError, NotImplementedError):  # an absolute pattern
            continue
        for path in matches:
            parts = path.relative_to(base).parts[:-1]
            if path.is_file() and path.suffix == ".md" and not any(p in SKIP_DIRS or p.startswith(".") for p in parts):
                out.add(path.resolve())
    return out


def relative(root, paths):
    out = set()
    for path in paths:
        try:
            out.add(path.relative_to(root.resolve()).as_posix())
        except ValueError:
            pass
    return out


def kind_of(rel, config):
    if rel == config.get("index"):
        return "index"
    if rel in ("AGENTS.md", "CLAUDE.md") or rel in config.get("roots", []):
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


def read_lines(root, rel):
    return (root / rel).read_text(errors="replace").splitlines()


def header(lines, key):
    """The value of `Key: value` in the page's header block, or None."""
    for line in lines[:HEADER_LINES]:
        if line.startswith(key):
            return line[len(key):].strip()
    return None


def parse_date(text):
    found = DATE.search(text or "")
    try:
        return date.fromisoformat(found.group()) if found else None
    except ValueError:
        return None


def add_months(when, months):
    month = when.month - 1 + months
    year, month = when.year + month // 12, month % 12 + 1
    return date(year, month, min(when.day, calendar.monthrange(year, month)[1]))


def git(root, *args):
    """Output lines of a git command in root, or None when git cannot answer."""
    try:
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=60, check=True).stdout.splitlines()
    except (subprocess.SubprocessError, OSError):
        return None


def git_date(root, rel):
    """The date of the last commit touching rel, or None (no git, untracked)."""
    lines = git(root, "log", "-1", "--format=%cs", "--", rel)
    return parse_date(lines[0]) if lines else None


def git_touched(root, staged):
    """Root-relative paths the last commit (or the staged set) touched, or None."""
    top = git(root, "rev-parse", "--show-toplevel")
    lines = git(root, "diff", "--cached", "--name-only") if staged else git(root, "show", "--name-only", "--format=", "HEAD")
    if not top or lines is None:
        return None
    return relative(root, (Path(top[0]) / line for line in lines if line))


def check_structure(root, config, found, notices, triggers, staged, today):
    """The config-driven structure rules; each runs only when its key is set."""
    folder_readme = {}
    for rel in sorted(relative(root, expand(root, config.get("state", [])))):
        lines = read_lines(root, rel)
        when = parse_date(header(lines, "State as of:"))
        if when is None:
            found.append((rel, "no valid `State as of: YYYY-MM-DD` line in its first 10 lines"))
        elif when > today:
            found.append((rel, f"State as of {when} is in the future"))
        elif (changed := git_date(root, rel)) and (changed - when).days > config.get("state_grace_days", 7):
            found.append((rel, f"State as of {when}, but last changed {changed}: whoever changes a state page changes its date"))
        if header(lines, "Owner:") is None:
            found.append((rel, "no `Owner:` line in its first 10 lines"))
        for number, line in enumerate(lines, 1):
            if DATED_HEADING.match(line):
                found.append((rel, f"line {number}: a dated heading on a state page; that is a report"))
    decisions = config.get("decisions")
    if decisions:
        records, pages = {}, {}
        for rel in sorted(relative(root, expand(root, [decisions]))):
            name = rel.rsplit("/", 1)[-1]
            if name in ("README.md", "TEMPLATE.md"):
                continue
            match = RECORD_NAME.match(name)
            if not match:
                found.append((rel, "not named NNNN-slug.md"))
                continue
            number = int(match.group(1))
            if number in records:
                found.append((rel, f"number {number:04d} is also {records[number]}"))
            records.setdefault(number, rel)
            pages[rel] = read_lines(root, rel)
        numbers = sorted(records)
        for gap in sorted(set(range(numbers[0], numbers[-1] + 1)) - set(numbers)) if numbers else []:
            found.append((decisions, f"no record {gap:04d}: numbers are gapless"))
        for rel, lines in pages.items():
            for key in ("Date:", "Status:", "Decider:"):
                if header(lines, key) is None:
                    found.append((rel, f"no `{key}` line in its first 10 lines"))
            for line in lines:
                for target in (int(n) for m in SUPERSEDED.finditer(line) for n in NUMBER.findall(m.group(1))):
                    if target not in records:
                        found.append((rel, f"superseded by {target:04d}, which does not exist"))
        folder_readme[decisions] = [rel.rsplit("/", 1)[-1] for rel in pages]
    grace = config.get("frozen_grace_days", 7)
    frozen_ok = set(config.get("frozen_ok", []))
    for rel in sorted(relative(root, expand(root, config.get("frozen", [])))):
        name = rel.rsplit("/", 1)[-1]
        if name == "README.md":
            continue
        match = DATED_NAME.match(name)
        when = parse_date(match.group(1)) if match else None
        if when is None:
            found.append((rel, "not named YYYY-MM-DD-slug.md: a dated file is named by its date"))
        elif rel not in frozen_ok and (changed := git_date(root, rel)) and (changed - when).days > grace:
            found.append((rel, f"dated {when} but last changed {changed}: a correction is a new report or a changelog line (frozen_ok lists allowed link edits)"))
    reference = config.get("reference")
    if reference:
        folder_readme[reference] = []
        for rel in sorted(relative(root, expand(root, [reference]))):
            name = rel.rsplit("/", 1)[-1]
            if name in ("README.md", "TEMPLATE.md"):
                continue
            folder_readme[reference].append(name)
            lines = read_lines(root, rel)
            checked = parse_date(header(lines, "Checked on:"))
            if checked is None:
                found.append((rel, "no valid `Checked on: YYYY-MM-DD` line in its first 10 lines"))
            elif checked > today:
                found.append((rel, f"Checked on {checked} is in the future"))
            rules = [line[len("Re-check:"):].strip() for line in lines[:HEADER_LINES] if line.startswith("Re-check:")]
            if not rules:
                found.append((rel, "no `Re-check:` line in its first 10 lines (every N days|weeks|months, or when <trigger>)"))
            for rule in rules:
                every = EVERY.match(rule)
                if every and checked:
                    count, unit = int(every.group(1)), every.group(2)
                    due = add_months(checked, count) if unit == "month" else date.fromordinal(checked.toordinal() + count * (7 if unit == "week" else 1))
                    if today > due:
                        notices.append((rel, f"re-check due since {due} ({rule}, checked on {checked})"))
                elif rule.startswith("when "):
                    triggers.append((rel, f"re-check {rule}"))
                elif not every:
                    found.append((rel, f"Re-check: {rule} is neither `every N days|weeks|months` nor `when <trigger>`"))
    for folder, names in folder_readme.items():
        index = folder.rstrip("/") + "/README.md"
        if not (root / index).exists():
            found.append((index, "missing: the folder's index links every page in it"))
            continue
        text = (root / index).read_text(errors="replace")
        for name in names:
            if name not in text:
                found.append((index, f"does not link {name}"))
    changelog = config.get("changelog")
    if changelog:
        touched = git_touched(root, staged)
        watched = config.get("state", []) + config.get("frozen", []) + [f for f in (decisions, reference) if f]
        hit = sorted(touched & relative(root, expand(root, watched))) if touched is not None else []
        if hit and changelog not in touched:
            what = "the staged change" if staged else "the last commit"
            found.append((changelog, f"{what} touches {hit[0]}" + (f" and {len(hit) - 1} more" if len(hit) > 1 else "") + " without a changelog line"))
        if (root / changelog).exists():
            for number, line in enumerate(read_lines(root, changelog), 1):
                if line.lstrip().startswith(("-", "*")) and "decid" in line.lower() and not (ADR.search(line) or (decisions and decisions in line)):
                    found.append((changelog, f"line {number}: names a decision without its record (ADR NNNN" + (f" or a path under {decisions}" if decisions else "") + ")"))
    for rule in config.get("only_in", []):
        pattern = re.compile(rule["pattern"])
        allowed = relative(root, expand(root, rule.get("files", []) + config.get("frozen", []) + ([decisions] if decisions else [])))
        for path, rel in markdown_files(root, []):
            if rel in allowed or rel == changelog or "archive" in rel.split("/")[:-1]:
                continue
            for number, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
                if pattern.search(line):
                    found.append((rel, f"line {number}: matches {rule['pattern']}, which lives only in {', '.join(rule.get('files', []))}"))


def check(root, config, fix=False, fixed=None, staged=False, today=None):
    """Returns (findings, notices, triggers), each a list of (file, text)."""
    found, notices, triggers = [], [], []
    today = today or date.today()
    fixed = fixed if fixed is not None else []
    skip = config.get("skip", [])
    no_limit = set(config.get("no_limit", []))
    patterns = config.get("patterns", False)
    reach = [("" if r in (".", "./") else r.rstrip("/") + "/") for r in config.get("reach", ["docs/"])]
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
            for named in (CODE_PATTERN if patterns else CODE_PATH).findall(line):
                for base in (path.parent, root):
                    if "*" in named or "<" in named:
                        linked |= relative(root, expand(base, [named]))
                        continue
                    candidate = (base / named).resolve()
                    if candidate.exists():
                        linked |= relative(root, [candidate])
            for target in LINK.findall(line):
                if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith("#"):
                    continue
                clean = target.split("#", 1)[0]
                if not clean:
                    continue
                if patterns and ("*" in clean or "<" in clean):
                    matches = relative(root, expand(path.parent, [clean]))
                    linked |= matches
                    if not matches:
                        found.append((rel, f"line {number}: link to {target}, which matches nothing"))
                    continue
                resolved = (path.parent / clean).resolve()
                linked |= relative(root, [resolved])
                if not resolved.exists():
                    found.append((rel, f"line {number}: link to {target}, which does not exist"))
    for rel in files:
        if any(rel.startswith(prefix) for prefix in reach) and kind_of(rel, config) == "page" and rel not in linked:
            found.append((rel, "no other doc links to it: add its line to the index or doc map"))
    open_list = config.get("open_list")
    # Its size is checked only by the repository that holds it: one list, one
    # check (2026-11-04: one long list failed three repositories' tests).
    if open_list and (root / open_list).resolve().is_relative_to(root.resolve()):
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
        # `before`: a regex that must come right before the name, such as
        # "(?:`|lmice )" for a command named as code or after its tool.
        before = cover.get("before", r"(?<![\w-])")
        for name in names:
            if not re.search(before + re.escape(name) + r"(?![\w-])", text):
                found.append((cover["file"], f"does not mention {name} ({cover['command']} lists it)"))
    check_structure(root, config, found, notices, triggers, staged, today)
    return found, notices, triggers


def main():
    parser = argparse.ArgumentParser(description="Check documentation against the documentation model.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--config")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--fix", action="store_true", help="add the contents lists it can make from headings")
    parser.add_argument("--staged", action="store_true", help="the changelog rule reads the staged set, not HEAD (a pre-commit hook)")
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
    found, notices, triggers = check(root, config, args.fix, fixed, args.staged)
    for rel in fixed:
        print(f"docs: added a contents list to {rel}", file=sys.stderr)
    if args.format == "json":
        out = {"schema_version": "doc-check.v1", "ok": not found, "findings": [{"file": f, "finding": m} for f, m in found]}
        if config.get("reference"):
            out["notices"] = [{"file": f, "notice": m} for f, m in notices]
            out["triggers"] = [{"file": f, "trigger": m} for f, m in triggers]
        print(json.dumps(out))
    else:
        print(f"docs: {len(found)} finding(s)" if found else "docs: ok")
        for file, message in found:
            print(f"  {file}: {message}")
        for label, items in (("notice", notices), ("re-check trigger", triggers)):
            if items:
                print(f"docs: {len(items)} {label}(s)")
                for file, message in items:
                    print(f"  {file}: {message}")
    return 1 if found else 4 if notices else 0


if __name__ == "__main__":
    sys.exit(main())
