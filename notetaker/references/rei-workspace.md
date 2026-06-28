# Rei Workspace Profile

Use this reference when a repo follows Rei's GitHub-first workspace conventions, especially the Kapotteke portfolio and related standalone repos.

## Workspace Rules

- Treat repos under the GitHub workspace as GitHub-bound unless the user says otherwise.
- Before publishing, check for private hostnames, private IPs, local-only paths, tokens, passwords, keys, and exact private examples.
- If a repo has `AGENTS.md`, follow it before writing project memory.
- Keep tracked docs sanitized. Raw transcripts, personal details, private machine state, and unpublished sensitive context stay out of public or GitHub-bound files.

## Kapotteke Portfolio

- Start with root `AGENTS.md`, then `apps.manifest.json`, then the app README and app-local docs.
- Keep app-specific memory in the paired app, usually under `frontends/<app>/<project>/docs/`.
- For app product direction, use app-local `docs/product-vision.md`.
- For app runtime, module, data, cost, privacy, deploy, or KISS contracts, use app-local `docs/architecture.md`.
- For session continuity, current state, verification, and loose ends, use app-local `docs/handoff.md`.
- For launch/legal/store/payment/privacy readiness, use existing app-local `docs/product-readiness.md` when present.
- Preserve the repo rule: one app, one task, one verification command. Do not turn app notes into repo-wide refactors.

## KatTAXeke-Style Repos

- Product, legal, tax, compliance, and release direction belongs in `docs/product-compliance-roadmap.md` or an existing equivalent.
- Internet-backed legal, tax, regulatory, pricing, YC/startup-positioning, vendor, or cross-border claims require dated source notes under `docs/source-notes/`.
- Source notes are engineering memory, not legal or tax advice. Prefer official sources and record recheck triggers.

## QAunxi-Style Repos

- Public product direction belongs in public docs such as `docs/product-vision.md`.
- Private commercial strategy, raw Codex transcripts, learned standards drafts, and customer-specific research stay in ignored `private/` conventions or outside the repo.
- Public docs should receive generalized principles and sanitized examples, not private conversation residue.

## Masterdale-Style Repos

- Public docs stay generic and local-first.
- Machine-specific context, private fleet details, local model assumptions, and private audits belong in ignored local context when such a convention exists.
- Do not publish private network details, private safe roots, tokens, or host-specific operational state.

## Paused Operational Projects

- For a project being paused or handed across machines, a dated pause handoff can be appropriate: `docs/<PROJECT>_PAUSE_HANDOFF_YYYY-MM-DD.md`.
- Include repository state, branch, last relevant commit, automation status, latest run result, entry points, blockers, and exact next verification target.
- Keep the handoff focused on resuming engineering work, not preserving chat history.
