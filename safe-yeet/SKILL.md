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
   - For a publish or sync request, exclude repositories without a push remote from both commit and push unless the user explicitly asks for a local-only commit.
   - Treat publishing as authorization to commit and push the requested source changes, not to create, enable, disable, or remove CI/GitHub Actions. Change CI only when the user explicitly includes it in scope.

2. Check remote and visibility.
   - Confirm the repo has a push remote before pushing.
   - Inspect every remote with `git remote -v`, not only `origin`; treat a remote named `public` as a public target.
   - Determine whether each target repo is public or private when possible.
   - Use `gh` or a GitHub connector when available; if not, continue with local `git` and assume public-level scrutiny unless the user explicitly confirms the repo is private.
   - Apply stricter scrutiny to public repos, but still check private repos for secrets and avoid unnecessary personal detail.
   - For public repos, treat `AGENTS.md`, private notes, and private operating instructions as non-public by default. Do not commit them unless the user explicitly says that this specific repo is private or that the file is intentionally public-safe.
   - Treat GitDCY as an optional supplemental path/visibility audit, never as a prerequisite or a replacement for the privacy, secret, and genericity gates below.
   - Resolve GitDCY without assuming a global installation:
     1. Use an executable path from `GITDCY_BIN` when the environment explicitly provides one.
     2. Otherwise use `gitdcy` when `command -v gitdcy` succeeds.
     3. Otherwise inspect only already-known source checkouts: the current repository, repositories already in confirmed scope, or a path supplied by the user. Confirm the checkout's Cargo workspace contains the `gitdcy-cli` package. Do not scan the whole home directory or hardcode a user-specific path.
     4. From a confirmed checkout root, prefer `cargo run --locked --quiet -p gitdcy-cli --` when Cargo and `Cargo.lock` are available. Otherwise try an executable `target/release/gitdcy`, then `target/debug/gitdcy` (and `.exe` variants on Windows).
   - Run a source fallback from the GitDCY checkout root so its ignored `.gitdcy.local.yaml` is honored. Audit each candidate by its exact provider-qualified manifest ID, such as `github/example`, rather than passing a filesystem path or auditing unrelated repos with `--all`.
   - Do not say "GitDCY is not installed" merely because it is absent from PATH. If no invocation resolves, report: `GitDCY supplemental audit skipped: no PATH executable or validated source checkout was available.` Continue every mandatory built-in gate. Do not install GitDCY, mutate PATH, or change its configuration unless the user asks.
   - Stop publishing a repository when GitDCY reports blocking findings. Distinguish blockers from invocation, build, configuration, and stale-manifest errors; never describe a failed or skipped audit as clean. If the repo is absent from its manifest, continue the mandatory built-in gates without changing machine-local GitDCY configuration.

3. Run the privacy and genericity gate before commit.
   - After reviewing the working tree, stage only explicit candidate paths. Audit the exact index with `git diff --cached --name-status` and the staged text diff. If the index changes afterward, rerun every gate.
   - Keep this gate mandatory even when GitDCY and gitleaks pass. GitDCY checks path policy and visibility; gitleaks checks secret patterns; neither proves that code or documentation is free of personal assumptions or generally designed.
   - Search the staged candidate diff for secrets, keys, tokens, private hostnames, private IPs, local-only paths, personal names, raw transcripts, private account data, and exact user stories.
   - Inspect staged paths as well as content. In public repos, block `AGENTS.md`, `.env*` except `.env.example`, private/runtime directories such as `private/`, `docs/private/`, `.codex/`, `.claude/`, top-level `state/`, `uploads/`, `logs/`, and local-only config unless there is explicit confirmation that the path is meant to be public source.
   - Do not broadly block source-like folders such as `data/`, `dist/`, or `build/`; inspect them by content and project context instead.
   - Replace private examples with generic product requirements, roles, placeholders, or supported workflow categories.
   - Replace machine-specific paths with placeholders such as `<state-root>`, `<runtime-root>`, `<repo-root>`, or documented env vars.
   - Keep implementation behavior general unless a user-specific customization is intentionally scoped to private configuration, ignored state, or an account profile.
   - Do not commit real `.env` files, databases, uploads, logs, binaries, model weights, browser profiles, session archives, screenshots with private data, or raw AI transcripts unless the user explicitly confirms the repo is private and the artifact belongs in source.
   - Never reproduce secret values, credential-bearing remote URLs, private hostnames, or personal records in commentary, commit messages, or reports. Report only the category and affected path, with values redacted.
   - Check staged workflow paths such as `.github/workflows/`. Do not introduce a workflow as publish plumbing when the user asked only to ship local changes, and preserve an explicit no-CI preference across multi-repo publishing.

4. Run checks before committing.
   - Run `git diff --cached --check` against the candidate commit. Optionally run `git diff --check` separately for remaining unstaged work.
   - Run `gitleaks protect --staged --redact --verbose --log-level warn` after staging when `gitleaks` is installed.
   - If `gitleaks` is unavailable, run targeted text scans for common secret markers and report that deterministic secret scanning was unavailable.
   - Run relevant repo tests or lightweight verification from local docs.
   - For docs-only changes, run available doc/contract checks when present.
   - If full-history secret scans report old findings, distinguish historical leaks from the current staged diff and do not claim history is clean.

5. Commit intentionally.
   - Confirm `git diff --cached --name-only` exactly matches the reviewed set. Do not add anything after the gates; rerun them if the staged snapshot changes.
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
