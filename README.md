# myskills

Open-source Codex skills for small, durable workflows.

## Skills

- `notetaker`: writes and maintains durable project memory so future Codex sessions can preserve what was discussed, decided, changed, completed, why it happened, and what should happen next. It includes reusable document structures plus an optional Rei workspace profile for Kapotteke-style repos.
- `repo-starter`: initializes or audits a new repository baseline before the first commit or push, including visibility, privacy, `.gitignore`, documentation, AGENTS.md, and optional GitDCY checks.
- `safe-yeet`: default publish workflow for local git changes. It commits and pushes with an explicit privacy, secret, and genericity gate before publishing, and works without the GitHub plugin.
- `decision-lenses`: reviews a medium- or high-impact decision through built-in SEO, marketing, engineering, and infrastructure perspectives, then returns one practical recommendation.
- `lean-engineering`: an engineering philosophy for designing, building, reviewing and refactoring software: keep it simple, small parts that compose, few dependencies, generic not personal, secure by default, never destructive, measured, documented.
- `wrap-up`: closes a long agent session without losing its context: the handoff where the folder keeps its state, corrections turned into rules, a project memory, what is unpushed or waiting, and the line that starts the next session.

## Use

Install or copy the skill folders into your Codex skills directory, then invoke them as `$notetaker`, `$repo-starter`, `$safe-yeet`, `$decision-lenses`, `$lean-engineering` or `$wrap-up`.

```bash
cp -R notetaker repo-starter safe-yeet decision-lenses lean-engineering wrap-up "${CODEX_HOME:-$HOME/.codex}/skills/"
```

## License

MIT
