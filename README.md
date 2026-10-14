# Agent Skills

Personal collection of agent skills for GitHub Copilot and compatible coding agents: workflow orchestration (git, PRs), an interview technique for stress-testing plans, Rust code review/style, and project scaffolding.

## Skills

| Skill | Kind | Description |
|---|---|---|
| [`grill-me`](./grill-me/) | user-invoked | Entry point for a grilling session about a plan or design. |
| [`grill-me-ask`](./grill-me-ask/) | user-invoked | Settle a plan's decisions fast: one-way doors asked in batched AskUserQuestion rounds, two-way doors auto-resolved, all recorded in a decision ledger. |
| [`grill-with-docs`](./grill-with-docs/) | user-invoked | Grilling session that also builds domain docs (`CONTEXT.md`, ADRs) as you go. |
| [`grilling`](./grilling/) | model-invoked | The reusable interview primitive: relentless, frontiere-based questioning until every decision is settled. |
| [`domain-modeling`](./domain-modeling/) | model-invoked | Actively build and sharpen a project's domain model; update glossary and ADRs inline. |
| [`design-for-simplicity`](./design-for-simplicity/) | model-invoked | Apply Rich Hickey's "Simple Made Easy" to architecture, API design, and reviews. |
| [`learn`](./learn/) | user-invoked | Update agent memory from what was surprising in the session; merges, generalizes, and prunes entries. |
| [`read-only`](./read-only/) | user-invoked | Restrict the session to inspection and analysis, no modifications. |
| [`commit`](./commit/) | user-invoked | Split a dirty working tree into logical, scope-prefixed commits with format/test gates. |
| [`pr`](./pr/) | user-invoked | Commit outstanding work, run gates, and open/update a GitHub PR via `gh`. |
| [`finalize-pr`](./finalize-pr/) | user-invoked | Full finalize flow: commit, rebase, review, gates, then open/update the PR. |
| [`pr-threads`](./pr-threads/) | model-invoked | List a GitHub PR's review threads with their resolution state, and resolve them. |
| [`rust-code-review`](./rust-code-review/) | user-invoked | Severity-ordered Rust code review with file/line evidence. |
| [`preview`](./preview/) | model-invoked | Preview pending changes (unstaged, staged, unpushed) as type-change and integration diagrams before reading the diff. |
| [`review`](./review/) | user-invoked | Any-language code review: loads the matching review skill and shared standards, audits comments and tests, severity-ordered findings. |
| [`rust-code-style`](./rust-code-style/) | user-invoked | Behavior-preserving Rust style refactors aligned to repository conventions. |
| [`project-setup`](./project-setup/) | user-invoked | Scaffold a Rust workspace with tooling conventions and the three-layer AI instruction architecture. |

### Dependencies

Some skills delegate to others and expect them to be installed:

- `grill-me`, `grill-with-docs` → `grilling`
- `grill-with-docs` → `domain-modeling`
- `pr` → `commit`
- `finalize-pr` → `commit`, `pr`, `review`, `pr-threads` (+ `rust-code-style` for style refactors)
- `update-pr` → `pr-threads`
- `review` → the matching review skill for the language (`rust-code-review` for Rust) and the shared standards instruction file

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