---
name: safe-yeet
description: Publish local git changes with an extra privacy, secret, and genericity gate before commit and push. Use when the user asks to commit, push, publish, yeet, sync to GitHub, or ship local changes while avoiding leaked secrets, personal data, machine-specific details, private examples, or code/docs that are overfitted to one user instead of generalized product behavior.
---

# Safe Yeet

Use this skill for publish flows where correctness includes not leaking private context.

## Workflow

1. Confirm repository scope.
   - Run `git status --short --branch`.
   - Inspect the diff before staging.
   - If multiple repos or unrelated changes are dirty, handle each repo separately and stage explicit paths.
   - Do not stage generated/runtime artifacts unless the user explicitly asked for them and they are safe source artifacts.

2. Check remote and visibility.
   - Confirm the remote is GitHub-backed before pushing.
   - Determine whether the target repo is public or private.
   - Apply stricter scrutiny to public repos, but still check private repos for secrets and avoid unnecessary personal detail.

3. Run the privacy and genericity gate before commit.
   - Search the staged candidate diff for secrets, keys, tokens, private hostnames, private IPs, local-only paths, personal names, raw transcripts, private account data, and exact user stories.
   - Replace private examples with generic product requirements, roles, placeholders, or supported workflow categories.
   - Replace machine-specific paths with placeholders such as `<state-root>`, `<runtime-root>`, `<repo-root>`, or documented env vars.
   - Keep implementation behavior general unless a user-specific customization is intentionally scoped to private configuration, ignored state, or an account profile.
   - Do not commit real `.env` files, databases, uploads, logs, binaries, model weights, browser profiles, session archives, screenshots with private data, or raw AI transcripts unless the user explicitly confirms the repo is private and the artifact belongs in source.

4. Run checks before committing.
   - Run `git diff --check`.
   - Run `gitleaks protect --staged --redact --verbose --log-level warn` after staging.
   - Run relevant repo tests or lightweight verification from local docs.
   - For docs-only changes, run available doc/contract checks when present.
   - If full-history secret scans report old findings, distinguish historical leaks from the current staged diff and do not claim history is clean.

5. Commit intentionally.
   - Stage only reviewed files.
   - Use a terse commit message that describes the user-visible change.
   - Re-run `git status --short --branch` after commit.

6. Push.
   - Push the current branch to its tracked remote unless the user requested a branch or PR workflow.
   - If on a feature branch and the user wants a PR, push the branch and open a draft PR.
   - If pushing `main` triggers deploys, check the workflow result when practical.

7. Report clearly.
   - List repos, commits, branches, and push status.
   - List checks run and any skipped checks.
   - Call out remaining dirty files, historical leak findings, or risks that were not part of the pushed diff.
