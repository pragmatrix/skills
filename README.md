# Agent Skills

Personal collection of agent skills for GitHub Copilot and compatible coding agents: workflow orchestration (git, PRs), an interview technique for stress-testing plans, Rust code review/style, and project scaffolding.

## Skills

| Skill | Kind | Description |
|---|---|---|
| [`grill-me`](./grill-me/) | user-invoked | Entry point for a grilling session about a plan or design. |
| [`grill-with-docs`](./grill-with-docs/) | user-invoked | Grilling session that also builds domain docs (`CONTEXT.md`, ADRs) as you go. |
| [`grilling`](./grilling/) | model-invoked | The reusable interview primitive: relentless, frontiere-based questioning until every decision is settled. |
| [`domain-modeling`](./domain-modeling/) | model-invoked | Actively build and sharpen a project's domain model; update glossary and ADRs inline. |
| [`design-for-simplicity`](./design-for-simplicity/) | model-invoked | Apply Rich Hickey's "Simple Made Easy" to architecture, API design, and reviews. |
| [`read-only`](./read-only/) | user-invoked | Restrict the session to inspection and analysis, no modifications. |
| [`commit`](./commit/) | user-invoked | Split a dirty working tree into logical, scope-prefixed commits with format/test gates. |
| [`pr`](./pr/) | user-invoked | Commit outstanding work, run gates, and open/update a GitHub PR via `gh`. |
| [`finalize-pr`](./finalize-pr/) | user-invoked | Full finalize flow: commit, rebase, review, gates, then open/update the PR. |
| [`rust-code-review`](./rust-code-review/) | user-invoked | Severity-ordered Rust code review with file/line evidence. |
| [`rust-code-style`](./rust-code-style/) | user-invoked | Behavior-preserving Rust style refactors aligned to repository conventions. |
| [`project-setup`](./project-setup/) | user-invoked | Scaffold a Rust workspace with tooling conventions and the three-layer AI instruction architecture. |

### Dependencies

Some skills delegate to others and expect them to be installed:

- `grill-me`, `grill-with-docs` → `grilling`
- `grill-with-docs` → `domain-modeling`
- `pr` → `commit`
- `finalize-pr` → `commit`, `pr`, `rust-code-review` (+ `rust-code-style` for style refactors)

## Installation

Clone or copy the skills into your agent's skills directory, e.g. for GitHub Copilot:

```
~/.copilot/skills/
```

Each skill lives in its own folder with a `SKILL.md`; user-invoked skills are reachable as slash commands (e.g. `/grill-me`).

## Credits

See [NOTICE.md](./NOTICE.md). The grilling-family and domain-modeling skills are adapted from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT). Everything else is original work.

## License

[MIT](./LICENSE)