---
name: repo-starter
description: Start or standardize a new repository with privacy-first Git defaults, public/private visibility decisions, conservative ignore rules, safe AGENTS.md handling, GitDCY compatibility, lightweight documentation, and first-commit readiness. Use when creating a new repo, onboarding an existing local repo, preparing a project before its first commit or push, adding a public mirror/export, or auditing whether a repo baseline is safe before development begins.
---

# Repo Starter

Use this skill before a repo's first meaningful commit or before an existing repo gets a new public/private publishing shape. It complements `safe-yeet`: this skill creates the baseline; `safe-yeet` handles commit and push.

## Workflow

1. Identify the repo and its visibility.
   - Run `git status --short --branch` and `git remote -v` when the repo exists.
   - Inspect every remote, not only `origin`; treat any remote named `public` or any known public hosting target as a public publishing target.
   - Classify the repo as `local-only`, `private`, `public`, or `private-with-public-export`.
   - If visibility is unknown, use public-safe defaults until the user or hosting metadata proves otherwise.
   - Do not force one architecture across unrelated repos. Standardize safety, source hygiene, and documentation; let each repo keep its appropriate stack and shape.

2. Create a conservative privacy baseline.
   - For public repos or repos with any public remote, do not track `AGENTS.md`, private operating notes, raw transcripts, private workspace docs, or machine-specific instructions.
   - For private repos, `AGENTS.md` can be tracked only when it contains no real secrets, credentials, private account data, or unnecessary personal detail.
   - Keep secrets in ignored local env files and document sanitized examples in `.env.example`.
   - Replace personal examples with generic roles, placeholders, or product-level scenarios unless the repo is intentionally private and the detail belongs in source.
   - Keep user-specific behavior in ignored local config, account/profile data, or runtime state rather than hardcoded source.

3. Add or verify `.gitignore`.
   - Include common private/runtime entries when relevant: `.env`, `.env.*`, `!.env.example`, `.codex/`, `.claude/`, `private/`, `docs/private/`, top-level `state/`, `uploads/`, `logs/`, `*.log`, `*.sqlite`, `*.db`, key/certificate files, dependency folders, build caches, OS files, and editor caches.
   - Add `AGENTS.md` for public repos and public-export repos.
   - Do not blindly ignore source-like directories such as `data/`, `dist/`, `build/`, or generated assets; inspect the project context first.
   - Avoid an overbroad global ignore that hides files a repo may legitimately need to version.

4. Add lightweight repo docs.
   - Create or update `README.md` with the repo purpose, stack, local run/test commands, and visibility expectations.
   - For product or app repos, add `docs/product-vision.md` only when the repo lacks a better source of truth.
   - For non-obvious architecture, add a short `docs/architecture.md`; keep it practical and tied to how the repo is operated.
   - For ongoing decisions or session memory, use the `notetaker` skill instead of stuffing private context into public docs.

5. Integrate GitDCY when available.
   - If GitDCY is configured for the workspace, prefer repo-specific policy over a universal template.
   - Use `gitdcy policy status <repo>` and `gitdcy audit <repo> --explain` to inspect the baseline.
   - Use `gitdcy policy apply <repo>` only after reviewing the planned ignore/policy changes.
   - Public-export repos must pass the GitDCY audit before public push.

6. Verify before first commit.
   - Run `git status --short --branch` after edits.
   - Inspect `git ls-files` and staged paths for private notes, env files, databases, logs, uploads, local state, and generated artifacts.
   - Run `git diff --check`.
   - Run `gitleaks protect --staged --redact --verbose --log-level warn` when files are staged and `gitleaks` is installed.
   - If no files are staged yet, run a local content scan or stage intentionally before invoking `safe-yeet`.
   - Run the smallest meaningful project check available from the repo docs or scaffold.

7. Hand off cleanly.
   - Summarize visibility, remotes, ignored private paths, docs added, verification run, and any remaining repo-specific decisions.
   - Do not commit or push unless the user asks. When they do, use `safe-yeet`.
