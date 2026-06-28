# Document Structure

Use these structures when creating or substantially reshaping durable project-memory docs. Prefer existing repo headings when they are already clear.

## Product Vision

Use for stable product direction and decisions that should guide future implementation.

````md
# <Product> Product Vision

Current status:

## Product Direction

- TBD

## Current Product Loop

- TBD

## Data And Privacy Direction

- TBD

## Risk Positioning

- TBD

## Product Surface

- TBD

## Roadmap Notes

- TBD
````

Keep product vision generic and reusable. Convert user-specific examples into supported workflows, target users, constraints, or principles.

## Architecture

Use for implementation boundaries, contracts, and operational constraints.

````md
# <Product> Architecture

## Runtime Shape

- TBD

## Core Boundaries

- TBD

## Data Model

- TBD

## Trust, Privacy, And Cost Boundaries

- TBD

## Extension Points

- TBD

## Verification

```bash

```
````

Keep architecture docs grounded in actual code paths, commands, schemas, interfaces, and deployment assumptions.

## Handoff

Use for current session continuity and cold-start context for a future agent.

````md
# <Product> Handoff

Last updated: YYYY-MM-DD

This file is the editable working handoff for future sessions.

## Current Position

- TBD

## Recent Changes

- TBD

## How To Extend Safely

- TBD

## Verification Baseline

```bash

```

## Known Loose Ends

- TBD
````

Keep handoff docs practical. Include what changed, why, how it was verified, what remains risky, and what the next session should do first.

## Source Notes

Use for current-source research and internet-backed claims.

````md
# YYYY-MM-DD Topic

- Checked: `YYYY-MM-DD HH:mm TZ`
- Researcher: `Codex`
- Scope:
- Status:

## Questions

- TBD

## Source Register

| Source | Authority | Checked | Status | Notes |
| --- | --- | --- | --- | --- |
| URL | Official/Secondary | timestamp | Current/stale/watch | Short conclusion |

## Product Implications

- TBD

## Recheck Triggers

- TBD

## Open Questions

- TBD
````

Prefer official primary sources. Summarize in your own words, link sources, and record when the claim should be rechecked.

## Readiness Docs

Use readiness docs for launch, store, legal, privacy, payment, AI safety, or policy audit state. Do not use them as the default place for ordinary session notes.
