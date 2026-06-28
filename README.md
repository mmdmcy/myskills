# myskills

Open-source Codex skills for small, durable workflows.

## Skills

- `notetaker`: writes and maintains durable project memory so future Codex sessions can preserve what was discussed, decided, changed, completed, why it happened, and what should happen next. It includes reusable document structures plus an optional Rei workspace profile for Kapotteke-style repos.
- `repo-starter`: initializes or audits a new repository baseline before the first commit or push, including visibility, privacy, `.gitignore`, documentation, AGENTS.md, and optional GitDCY checks.
- `safe-yeet`: default publish workflow for local git changes. It commits and pushes with an explicit privacy, secret, and genericity gate before publishing, and works without the GitHub plugin.

## Use

Install or copy the skill folders into your Codex skills directory, then invoke them as `$notetaker`, `$repo-starter`, or `$safe-yeet`.

```bash
cp -R notetaker repo-starter safe-yeet "${CODEX_HOME:-$HOME/.codex}/skills/"
```

## License

MIT
