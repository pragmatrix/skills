---
applyTo: "**/*.rs"
---

# Rust House Standards

The criteria the Reviewer audits every Rust change against. Apply them while writing — a violation comes back as a review finding. Mirrors `skills/rust-code-review` and `skills/design-for-simplicity` for the author's side; the Reviewer owns enforcement.

## Simplicity

- **Simple means unbraided — one role, one concern.** Do not confuse it with *easy* (familiar, at hand, quick to write). Judge the artifact that will be read, changed, and debugged, not the authoring convenience.
- **Do not complect.** Keep independent decisions independent: state from value/time, types from implementation (inheritance), function from state (methods), what-is-done from how-it-iterates (loops), policy from execution structure (scattered conditionals), timing/location from the caller (direct calls).
- **Prefer plain data and functions**: values over mutable state where possible, functions over methods when there is no state or identity, small abstractions that say *what* rather than *how*, declarative rules or policy tables over scattered imperative branches, a queue or value boundary when timing and location should vary independently.
- **Derive each result once.** No lookup or scan repeated per element of a loop when one pass or one table serves them all, and no second copy of a calculation another function already owns; reuse its result or call it. One source per fact keeps a change in one place and stops quadratic work from creeping in.
- **Abstractions must draw away from irrelevant detail, not hide complexity behind a name.** An abstraction is good when its callers do not need to know hidden state, call order, location, or policy.
- **A return type holds only the outcomes its function can produce.** A function that chooses among outcomes returns an enum whose variants name what happens. `Option`, `Result`, and `bool` fit only when absence, failure, or a yes/no fact is the outcome itself. A shared enum with variants some caller can never receive is a finding.
- **A mutation reports what it did.** When the caller needs facts about what a mutation changed or removed, the mutation returns them from the same walk that performs it. Querying the state beforehand and attaching the answer to the result afterwards splits one fact across two walks that nothing keeps in step.
- **A decision function decides, it does not select.** It takes the facts behind its decision and returns the choice. Passing it the candidate values to pick from, or a context it reads one fact from, moves the caller's work into it.
- **Counting files, modules, layers, or services is not simplicity** — only independence behind abstractions is. Equally, tests and type checks are guardrails, not simplicity.
- **A change is simpler only if a future action gets easier**: the change localizes to one dimension, a bug is investigated without recreating hidden state, a policy changes without touching plumbing, or a boundary lets a component be replaced. Otherwise it is merely rearranged.
- Say honestly when a simpler design is less familiar, and when the complexity is inherent rather than incidental.

## Tests

- Add a test only when the brief asks for tests, or when a test is the only reasonable way to pin down semantics that are counter-intuitive or exceptional.
- Do not add tests that re-check ordinary behavior, mirror neighbouring test files, or restate the implementation in assertions — those are reported as findings to delete.
- A test that stays must assert the behavior (not a snapshot), be able to fail, and sit where the repository keeps tests of that kind.
- A concurrency or ordering finding comes with a test that goes red on it, before any fix.

## Comments

- **Explicit user request:** Add rationale comments for non-obvious behavior, invariants, coordinate conversions, and architectural constraints; no per-task request is needed. When changing commented code, preserve or update its relevant rationale.
- Every comment states a why — the reason, the constraint, the non-obvious behavior. The why is the point.
- A newly added item (module, type, trait, function, constant) gets a comment that places it in the bigger picture — the role it plays for its callers or the surrounding design — and says why it exists.
- The general rule for comments in `agent-behavior.instructions.md` applies. In addition, a term that is only familiar from the current work ("drawn", "re-base", "spare placement") is spelled out in plain words, and a lone abstract word ("invariant", "safety", "cleanup") gets the words that say which one ("lock-ordering invariant", "cancel safety").
- A code comment is one or two plain sentences that name the cause and its effect. A rationale that a test pins names that test.
- A doc comment longer than two sentences opens with a one-sentence overview in a paragraph of its own, separated by an empty `///` line, so rustdoc's summary and a skimming reader get the item's role first.
- Only an involved algorithm gets as many sentences as it takes, as long as each one carries a reason.
- Do not restate the code: no echoing signatures or identifiers, no narrating the next statement, no history ("previously X", "was Y").
- A comment that is both needless and uninformative is removed, not rewritten.
- When an ADR or the glossary holds the reasoning, the comment links it, such as "(ADR 0029)", and stays a line or two instead of restating it.
- A comment that contrasts the code with a design the reader cannot see ("owned outright rather than mutex-guarded", "a compile error instead of a runtime check") explains the change, not the code — rewrite it as the reason the code is as it is. The why of the decision belongs at the code, not the contrast.
- History that carries a reason stays: a dated measurement behind a constant, a rejected alternative that stops a future reader from "fixing" a subtlety, a `TODO`, or an open `Architecture:` question. Only a comment whose whole content is that the code changed ("previously X", "now does Z", "replaces the old ...") is a finding — that record lives in git and in the ADR's own context section, whose rejected alternatives stay there too.

## Structure

- Items that leave their module are plain `pub`; the module declaration (`mod` vs `pub mod`) is the one place that decides how far they reach. A restricted modifier (`pub(crate)`, `pub(super)`) belongs only on an item inside a `pub mod` that must stay out of the external API, because inside a private module it repeats what the module already enforces.
- A module named after its main type (`tool_host` for `ToolHost`) lives in `tool_host.rs`, with its helper submodules in `tool_host/`, so the type sits in the file that carries its name. A `lib.rs` or `mod.rs` stays small and preferably holds no items: the crate or module documentation, the submodule declarations, and the re-exports. At most, it holds the few basic types its submodules share (messages, ids, small enums). Everything else, a crate's entry function included, lives in a named submodule and is re-exported, so the crate's or module's shape reads at a glance and its machinery sits apart.
- A decision function is named after its situation, as a gerund (`removing_slot_content`, `calling_tool`), and lives in the module that owns such decisions, whose name makes it read right (`when::`, `security::`). A query that gathers a fact is named after the fact it returns, as a noun phrase (`project_depth`, `deepest_project_after`, `has_instances_below`). The caller passes the fact to the decision, and no wrapper outside that module carries the gerund name, because without its module a gerund reads like a list (`nesting_projects` like "the nested projects").
- Imports nest one level at most: a single `{ }` group is fine (`use std::{fs, io};`, `use std::io::{self, Cursor};`), a group inside a group is not (`use std::{fs, io::{self, Cursor}};`).
- Functions are ordered by invocation structure: public high-level functions first, helpers below the callers that use them.
- Implement or derive `Debug` wherever possible, at minimum on every type reachable from a public API.
- A long closure (roughly more than five statements) containing real logic is extracted into a named function next to its wrapper.

## Correctness (reviewed first)

- **Radically fail-fast: no defensive programming.** Code never protects itself against states it believes cannot happen — no fallbacks, no swallowed errors, no "just in case" branches. Model valid states explicitly so impossible states are unrepresentable; reserve `Option` and `Result` for genuine absence and fallible operations. Where a runtime boundary still lets an inconsistent state through, that is a broken invariant: surface it at the decision point with `assert!`/`assert_eq!` (or `debug_assert!` when the check is hot-path expensive) — never by returning `Err`/`None` or a default, which invites the caller to handle what no one can handle. A panic stops the bug where it was introduced.
- **Type before assert.** When independent flags or options have a combination that must never occur, the fix is a type with no case for it (an enum instead of two `bool`s), built in one place that asserts the invariant once, so its consumers match without a check of their own. A review that finds such a combination proposes the type first, and a lone assertion only when no type can carry the rule.
- Mutable state has one source of truth; no mirrored caches without justification.
- Errors carry useful context; data/protocol boundary types convert explicitly (source format → runtime/domain type).

## Crates

- Look up a crate's newest version, features, and repository with `cargo info <crate>`, and its API in the source under `~/.cargo/registry/src/` after `cargo fetch`. Fetch docs.rs or crates.io only for what neither shows, because their pages run to hundreds of thousands of characters.

## Verification

- Verify a change with `cargo clippy`, passing the targets and features you would pass to `cargo check`. Clippy runs the full check, so a separate `cargo check` first only repeats the build.
