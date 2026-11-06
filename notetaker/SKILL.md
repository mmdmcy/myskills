---
name: notetaker
description: Write and maintain durable project memory for repos and apps. Use when the user asks to write things down, preserve what was discussed, summarize decisions, record what was done, explain why choices were made, update the context future agent sessions (Codex, Claude Code) start from, maintain handoff notes, product vision, architecture notes, source/research notes, roadmap memory, readiness notes, or session continuity docs.
---

# Notetaker

Use this skill to preserve project continuity without turning chat into a transcript.

## Workflow

1. Ground yourself before writing.
   - Read the nearest repo instructions, then existing README and docs.
   - Search for existing vision, architecture, readiness, handoff, notes, source-notes, roadmap, and private-context conventions.
   - If the repo resembles Rei's GitHub workspace or Kapotteke portfolio, read `references/rei-workspace.md`.

2. Route the memory to the right durable document.
   - Product direction, positioning, audience, principles, and roadmap: update or create `docs/product-vision.md` or the existing vision doc.
   - Runtime boundaries, data model, cost/privacy/security contracts, interfaces, and extension points: update or create `docs/architecture.md`.
   - Current state, what changed and why, and how to verify: update or create `docs/handoff.md` (current state only; rewrite it, move older copies aside).
   - Loose ends, next steps and promises: the owner's one open list (named in the global agent instructions), never the handoff; an item leaves only when done and checked.
   - Internet-backed legal, tax, regulatory, pricing, vendor, or current-source claims: update or create a dated source note such as `docs/source-notes/YYYY-MM-DD-topic.md`.
   - Launch, legal, store, payment, privacy, or policy audit state: update the existing readiness doc; create one only if the repo already uses readiness docs or the user asks for launch readiness.
   - Small repos with no docs folder: update the README first unless durable context would clearly outgrow it.

3. Use standard structure when creating a missing doc.
   - Read `references/doc-model.md` for the layers (root and package instructions, index, topic pages, open list, handoff, changelog, decisions), their size limits and the rules that keep them working, before creating a doc or when one has grown past its limit.
   - Read `references/document-structure.md` before creating or heavily reshaping product vision, architecture, handoff, or source-note files.
   - Keep repo-specific headings if they already exist and are clear.

4. Sanitize tracked docs.
   - Do not store secrets, credentials, tokens, private account data, raw transcripts, exact private stories, or machine-only operational details in GitHub-bound files.
   - Generalize private examples into requirements, product categories, roles, constraints, or operating principles.
   - Use an ignored private notes convention only when it already exists or the user explicitly asks for it.

5. Write for the next agent session (Codex, Claude Code).
   - Be concise, factual, dated where useful, and editable.
   - Prefer bullets, file references, commands, and decision rationale over narrative.
   - Record why decisions were made so future sessions do not reverse them by accident.
   - Separate stable product truth from temporary session state.

6. Verify before finishing.
   - Run `git diff --check`.
   - Run `scripts/doc_check.py` in the repository (it reads an optional `docs-check.toml`; `--fix` adds contents lists; exit 4 is a notice, a reference page due for a re-check) and fix every finding; if the repository's tests do not run it yet, add it there, so drift fails a test instead of waiting for an agent to notice. The structure rules a repository can switch on (state pages, decision records, frozen reports, the changelog, one home per fact, reference pages) are listed in `references/doc-model.md`.
   - After a substantial change, run the reader test (`references/doc-model.md`): a fresh agent with only the doc answers the next agent's questions; every miss is a doc fix.
   - Run any repo-specific doc, contract, or validation check that already exists.
   - If sensitive topics were discussed, scan the diff for secrets and private examples.
   - Do not commit or push unless the user asks.
