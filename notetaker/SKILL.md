---
name: notetaker
description: Write and maintain durable session notes for a repo or project. Use when the user asks to write things down, preserve what was discussed, summarize decisions, record what was done, explain why choices were made, capture who/what/how context, update handoff docs, or keep future Codex sessions aligned.
---

# Notetaker

Use this skill to preserve project continuity without turning chat into a transcript.

## Workflow

1. Ground yourself in the project.
   - Read local instructions first.
   - Search for existing notes, handoff, product, architecture, roadmap, README, or decision docs.
   - Prefer the project's established docs over inventing new locations.

2. Choose where notes belong.
   - Update an existing durable notes or handoff file when one exists.
   - For a single-project repo, use `docs/notes.md` or `docs/handoff.md` if no convention exists.
   - For a monorepo, use the relevant app, service, or package docs folder.
   - Add a short pointer from nearby README/product docs only when future agents would otherwise miss the notes.

3. Capture durable context.
   - Current status and scope.
   - What was discussed, decided, changed, and completed.
   - Why decisions were made, including important rejected options.
   - Who is involved when it matters, using roles instead of private identity details where possible.
   - How the system should be worked on next: commands, paths, contracts, runtime assumptions, and constraints.
   - Verification already run and what remains unverified.
   - Loose ends, risks, blockers, and next likely work.

4. Keep sensitive information out.
   - Do not store secrets, credentials, tokens, private account data, raw personal stories, or exact sensitive examples.
   - Generalize private examples into requirements, product categories, or operating constraints.
   - If a sensitive detail is required for continuity, ask before writing it and mark it clearly.

5. Write for the next Codex session.
   - Be concise, factual, dated, and editable.
   - Prefer bullets and file references over narrative.
   - Explain enough rationale that a future session does not reverse important decisions by accident.
   - Avoid praise, chat logs, and guesses not grounded in the repo.

6. Verify before finishing.
   - Run `git diff --check`.
   - Run any repo-specific doc or contract check that already exists.
   - If sensitive topics were discussed, scan the diff for secrets and private examples.
   - Do not commit or push unless the user asks.
