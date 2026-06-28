---
name: safe-yeet
description: Default safe publish workflow for local git changes. Use when the user asks to commit, push, publish, yeet, sync to GitHub, ship local changes, or publish multiple repos, especially when avoiding leaked secrets, personal data, machine-specific details, private examples, or code/docs overfitted to one user instead of generalized product behavior.
---

# Safe Yeet

Use this standalone skill as the default publish flow. It does not require the GitHub plugin. Use the GitHub plugin only as an optional enhancement for pull requests, review comments, connector-backed repository data, or CI log workflows.

## Workflow

1. Confirm repository scope.
   - Run `git status --short --branch`.
   - Inspect the diff before staging.
   - If multiple repos or unrelated changes are dirty, handle each repo separately and stage explicit paths.
   - Do not stage generated/runtime artifacts unless the user explicitly asked for them and they are safe source artifacts.

2. Check remote and visibility.
   - Confirm the repo has a push remote before pushing.
   - Inspect every remote with `git remote -v`, not only `origin`; treat a remote named `public` as a public target.
   - Determine whether each target repo is public or private when possible.
   - Use `gh` or a GitHub connector when available; if not, continue with local `git` and assume public-level scrutiny unless the user explicitly confirms the repo is private.
   - Apply stricter scrutiny to public repos, but still check private repos for secrets and avoid unnecessary personal detail.
   - For public repos, treat `AGENTS.md`, private notes, and private operating instructions as non-public by default. Do not commit them unless the user explicitly says that this specific repo is private or that the file is intentionally public-safe.
   - If GitDCY is available for the workspace, run `gitdcy audit <repo>` or `gitdcy audit --all` before public publishing and honor its blocking findings.

3. Run the privacy and genericity gate before commit.
   - Search the staged candidate diff for secrets, keys, tokens, private hostnames, private IPs, local-only paths, personal names, raw transcripts, private account data, and exact user stories.
   - Inspect staged paths as well as content. In public repos, block `AGENTS.md`, `.env*` except `.env.example`, private/runtime directories such as `private/`, `docs/private/`, `.codex/`, `.claude/`, top-level `state/`, `uploads/`, `logs/`, and local-only config unless there is explicit confirmation that the path is meant to be public source.
   - Do not broadly block source-like folders such as `data/`, `dist/`, or `build/`; inspect them by content and project context instead.
   - Replace private examples with generic product requirements, roles, placeholders, or supported workflow categories.
   - Replace machine-specific paths with placeholders such as `<state-root>`, `<runtime-root>`, `<repo-root>`, or documented env vars.
   - Keep implementation behavior general unless a user-specific customization is intentionally scoped to private configuration, ignored state, or an account profile.
   - Do not commit real `.env` files, databases, uploads, logs, binaries, model weights, browser profiles, session archives, screenshots with private data, or raw AI transcripts unless the user explicitly confirms the repo is private and the artifact belongs in source.

4. Run checks before committing.
   - Run `git diff --check`.
   - Run `gitleaks protect --staged --redact --verbose --log-level warn` after staging when `gitleaks` is installed.
   - If `gitleaks` is unavailable, run targeted text scans for common secret markers and report that deterministic secret scanning was unavailable.
   - Run relevant repo tests or lightweight verification from local docs.
   - For docs-only changes, run available doc/contract checks when present.
   - If full-history secret scans report old findings, distinguish historical leaks from the current staged diff and do not claim history is clean.

5. Commit intentionally.
   - Stage only reviewed files.
   - Use a terse commit message that describes the user-visible change.
   - Re-run `git status --short --branch` after commit.

6. Push.
   - Push the current branch to its tracked remote unless the user requested a branch or PR workflow.
   - If on a feature branch and the user wants a PR, push the branch and open a draft PR using `gh` or the GitHub plugin if available.
   - If pushing `main` triggers deploys, check the workflow result when practical.

7. Report clearly.
   - List repos, commits, branches, and push status.
   - List checks run and any skipped checks.
   - Call out remaining dirty files, historical leak findings, or risks that were not part of the pushed diff.
