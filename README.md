# Agent Skills

Agent skills for Claude Code, GitHub Copilot, and other coding agents that read `SKILL.md` folders: workflow orchestration (git, PRs, reviews), an interview technique for stress-testing plans, Rust code review/style, and project scaffolding.

## Skills

**Invoked by** says who starts a skill: _you_ (as a slash command, e.g. `/grill-me`), the _agent_ (when the task matches the skill's description), or _both_. **Agents** says where a skill works: _any_ agent that reads skill folders, or _Claude Code_ only.

| Skill | Invoked by | Agents | Description |
|---|---|---|---|
| [`grill-me`](./grill-me/) | you | any | Entry point for a grilling session about a plan or design. |
| [`grill-fast`](./grill-fast/) | you | any | Settle a plan's decisions fast: one-way doors asked in batched question rounds, two-way doors auto-resolved, all recorded in a decision ledger. |
| [`grill-tree`](./grill-tree/) | you | any | Like `grill-fast`, but a bundled tool keeps the decision tree and ledger in a state file and renders each round, so the same state yields the same questions. |
| [`grill-with-docs`](./grill-with-docs/) | you | any | Grilling session that also builds domain docs (`GLOSSARY.md`, ADRs) as you go. |
| [`grilling`](./grilling/) | both | any | The reusable interview primitive: relentless, frontier-based questioning until every decision is settled. |
| [`domain-modeling`](./domain-modeling/) | both | any | Actively build and sharpen a project's domain model; update glossary and ADRs inline. |
| [`design-for-simplicity`](./design-for-simplicity/) | both | any | Apply Rich Hickey's "Simple Made Easy" to architecture, API design, and reviews. |
| [`writing-for-agents`](./writing-for-agents/) | both | any | How to write skills, `AGENTS.md`, `CLAUDE.md`, and other documents agents consume. |
| [`retro`](./retro/) | you | any | Run a retrospective on a coding session and suggest improvements to the agent's environment. |
| [`learn`](./learn/) | you | any | Update agent memory from what was surprising in the session; merges, generalizes, and prunes entries. |
| [`read-only`](./read-only/) | you | any | Restrict the session to inspection and analysis, no modifications. |
| [`bugfix`](./bugfix/) | both | any | Bug-fixing workflow: root-cause evidence and a focused hypothesis test before production edits. |
| [`diagnosing-bugs`](./diagnosing-bugs/) | both | any | Diagnosis loop for hard bugs and performance regressions. |
| [`commit`](./commit/) | both | any | Split a dirty working tree into logical, scope-prefixed commits with format/test gates. |
| [`pr`](./pr/) | both | any | Commit outstanding work, run gates, and open/update a GitHub PR or GitLab MR. |
| [`finalize-pr`](./finalize-pr/) | both | any | Full finalize flow: commit, rebase, review, gates, then open/update the PR. |
| [`update-pr`](./update-pr/) | both | any | Post a PR comment summarizing what changed in the current session and what is still open. |
| [`pr-threads`](./pr-threads/) | both | any | List a GitHub PR's review threads with their resolution state, and resolve them. |
| [`preview`](./preview/) | both | any | Preview pending changes (unstaged, staged, unpushed) as type-change and integration diagrams before reading the diff. |
| [`review`](./review/) | both | any | Any-language code review: loads the matching review skill and shared standards, audits comments and tests, severity-ordered findings. |
| [`code-review-core`](./code-review-core/) | agent | any | Language-agnostic review procedure, audits, and output template that language review skills load. |
| [`rust-code-review`](./rust-code-review/) | both | any | Severity-ordered Rust code review with file/line evidence. Ships the Rust standards file the other Rust skills use. |
| [`rust-code-style`](./rust-code-style/) | both | any | Behavior-preserving Rust style refactors aligned to repository conventions. |
| [`handle-reviews`](./handle-reviews/) | both | Claude Code | Handle review results that reach the session: background review findings, review subagent reports, PR review comments. |
| [`install-review-on-push`](./install-review-on-push/) | you | Claude Code | Install a pre-push hook that reviews the pushed commits with one or more review skills, each in a read-only background Claude Code run, and messages the findings to the open sessions. |
| [`architecture`](./architecture/) | both | any | Keep a Rust workspace's `ARCHITECTURE.md` current: a derived code graph of crates, modules, and external crates, checked against the components declared in `architecture.toml`. |
| [`architecture-review`](./architecture-review/) | both | any | Review a change's effect on the architecture: note every graph change and judge the dependency structure. Runs on push via `install-review-on-push`. |
| [`project-setup`](./project-setup/) | both | any | Scaffold a Rust workspace with tooling conventions and the three-layer AI instruction architecture. |
| [`youtube-summary`](./youtube-summary/) | both | any | Download a YouTube transcript and summarize it: notable points, action plan, critique of weak claims. |

### Dependencies

Some skills use others by name and expect them to be installed next to them:

- `grill-me` → `grilling`
- `grill-with-docs` → `grilling`, `domain-modeling`
- `retro` → `writing-for-agents`
- `pr` → `commit`
- `finalize-pr` → `commit`, `pr`, `review`, `pr-threads`, `rust-code-style`
- `update-pr` → `pr-threads`
- `review` → the review skill for the language (`rust-code-review` for Rust)
- `rust-code-review` → `code-review-core`
- `rust-code-style` → `rust-code-review` (for its standards file)
- `handle-reviews` → `grill-fast`
- `install-review-on-push` → `handle-reviews`, and the review skills it runs (`review`, optionally `architecture-review`)
- `architecture-review` → `architecture`
- `project-setup` → `review`

Some skills also need command-line tools:

- `gh` (GitHub) or `glab` (GitLab): `pr`, `finalize-pr`, `update-pr`, `pr-threads`
- `python3`: `grill-tree`, `youtube-summary`, and (3.11 or newer) `architecture`, `architecture-review`
- `claude` and `jq`: the hook that `install-review-on-push` installs
- `cargo-modules`: `architecture`, `architecture-review`

## Installation

Clone the repository anywhere:

```sh
git clone https://github.com/pragmatrix/skills.git ~/src/agent-skills
```

Then make the skills visible in your agent's user-level skills folder: `~/.claude/skills` for Claude Code, `~/.copilot/skills` for GitHub Copilot. Either link the whole clone, when that folder does not exist yet:

```sh
ln -s ~/src/agent-skills ~/.claude/skills
```

or link only the skills you want, together with the skills they depend on (see [Dependencies](#dependencies)):

```sh
mkdir -p ~/.claude/skills
for skill in grill-me grilling; do
    ln -s ~/src/agent-skills/$skill ~/.claude/skills/$skill
done
```

To update, run `git pull` in the clone. If you use `install-review-on-push` and move the clone, run its installer again in each repository, because the installed hook records where the skills are.

The Rust skills audit against [`rust-code-review/rust-standards.instructions.md`](./rust-code-review/rust-standards.instructions.md). GitHub Copilot users can also link it into `~/.copilot/instructions/` so the same standards apply while writing Rust, not only during review.

## Credits

See [NOTICE.md](./NOTICE.md). The grilling-family, domain-modeling, diagnosing-bugs, retro, and writing-for-agents skills come from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT). `youtube-summary` ports the transcript download of [lstrzepek/obsidian-yt-transcript](https://github.com/lstrzepek/obsidian-yt-transcript) (MIT). Everything else is original work.

## License

[MIT](./LICENSE)
