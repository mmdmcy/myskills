# Documentation model

One shape for every repository, so an agent finds what it needs and misses
nothing. It follows Anthropic's public guidance for Claude Code: files that
load every session stay short, because longer files "consume more context and
reduce adherence"; a file an agent is only told to read is seen "only if it
decides to open the file"
(https://code.claude.com/docs/en/memory,
https://code.claude.com/docs/en/best-practices,
https://code.claude.com/docs/en/large-codebases).

## The layers

| File | Holds | Limit | Read |
|---|---|---|---|
| Root `AGENTS.md` (or `CLAUDE.md`) | what the repo is, verify commands, gotchas, the repo's own rules, a doc map (one line per doc: what it holds, when to read it) | 150 lines | every session |
| Package `AGENTS.md` (`services/x/`, `apps/y/`) | that package's commands, gotchas and boundaries | 60 lines | when a file in that folder is read |
| Handbook / index | one line per device, service, project or topic, each linking to its page | 200 lines | before touching what it lists |
| Topic pages (`docs/<area>/<topic>.md`) | how one thing works and why; a contents list on top past 100 lines | 400 lines | when working on that topic |
| Open list (one per owner, not per repo) | what was asked and promised, not done yet: date, what, the owner's words, why not yet | 110 lines | every session (imported, see below) |
| `docs/handoff.md` | current state only: where things stand, what is in flight, how to verify | 150 lines; rewritten, older copies moved aside | when resuming |
| Changelog | one line per change, newest last | none; read the last lines only | after a change, to add a line |
| Decision records (`docs/decisions/NNNN-*.md`) | one decision each: context, decision, consequences; never rewritten, superseded by a newer one | one decision | when working in that area |

## Rules that keep it working

- **A check, not a habit.** `scripts/doc_check.py` runs in the repository's
  tests: size limits, links that resolve, every page reachable from an index
  or doc map, contents lists past 100 lines, one open list, and (`[[covers]]`)
  every name a command lists appears in its doc. Docs that drift fail a test
  like code does; an agent fixes what the finding names instead of rewriting.
  A repository that wants the structure enforced sets more keys in its
  `docs-check.toml`, each a rule only when set (the script's docstring shows
  the syntax; the tests, `python3 -I -m unittest discover -s notetaker/scripts/tests`):
  - `reach = ["."]`, `patterns = true`: every page in the whole repository is
    linked from somewhere; a doc-map line such as `apps/<app>/README.md` or
    `docs/x-*.md` counts as a link to every file it matches.
  - `state = [folders or globs]`, `state_grace_days = 7`: a state page has
    `State as of: YYYY-MM-DD` (valid, not in the future, not more than the
    grace behind its last commit) and `Owner:` in its first 10 lines, and no
    `##` heading with a date (that is a report).
  - `decisions = "docs/decisions/"`: records named `NNNN-slug.md`, numbered
    without gaps or doubles, with `Date:`, `Status:` and `Decider:`;
    `Superseded by NNNN` names a record that exists; `README.md` links every
    record; `TEMPLATE.md` is skipped.
  - `frozen = [folders or globs]`, `frozen_grace_days = 7`, `frozen_ok =
    [paths]`: a dated file is named `YYYY-MM-DD-slug.md` and its last commit
    is at most the grace after that date, unless listed in `frozen_ok`.
  - `changelog = "docs/changelog.md"`: when the last commit (or, with
    `--staged`, the staged set: a pre-commit hook) touches a state, decision,
    frozen or reference file, the changelog is touched too; a changelog line
    with "decid" names `ADR NNNN` or a path under the decisions folder.
  - `[[only_in]]` with `pattern` (a regex) and `files`: the pattern may
    appear only in those files, the frozen, decisions and archive folders and
    the changelog; every other `.md` that matches is a finding (one home per
    fact). Code is not scanned.
  - `reference = "docs/reference/"`: each page has `Checked on: YYYY-MM-DD`
    and at least one `Re-check:` line; `every N days|weeks|months` past due is
    a notice (exit 4, listed in text and JSON), `when <trigger>` is listed and
    never flagged; `README.md` links every page.
- **One home per fact.** A rule, a list or a state lives in one file; others
  link to it. Two copies drift, and an agent believes the stale one.
- **Open work has one list.** Loose ends, next steps and promises go to the
  owner's open list, not into a handoff, a handbook section or a changelog.
  An item leaves only when done and checked, or when the owner drops it.
- **What must be seen every session is loaded, not mentioned.** In Claude
  Code, import it in the global or root instructions with a line holding only
  `@path/to/file.md` (home paths as `@~/...`). Other agents may not expand
  imports, so the line above it says in words which file to read.
- **What must happen every time is a hook or a check, not a sentence.**
- **Indexes stay indexes.** When a page grows past its limit, split by
  topic and leave one line with a link where the text was.
- **Write for the next agent.** Facts, dates, commands, file paths and the
  reason behind each decision; no narrative, no chat history.

## The reader test (after a substantial doc change)

Give a fresh agent only the changed doc (and the doc map), plus 5 to 10
questions the next agent will have ("where does X run?", "what is still open
about Y?", "how do I verify Z?"). Every wrong or missing answer is a fix to
the doc, not to the test. From Anthropic's doc-coauthoring skill
(https://github.com/anthropics/skills/blob/main/skills/doc-coauthoring/SKILL.md).

## Moving an existing repo onto the model

1. Write the doc map into the root instructions first; mark each existing doc
   with its layer.
2. Move open items out of handoffs and handbooks into the open list.
3. Cut the handbook down to its index; move each long section to a topic page
   with the same heading, leaving its line and link.
4. Add package `AGENTS.md` files where a folder has its own commands or
   gotchas.
5. Run the reader test on the root instructions and the index.
