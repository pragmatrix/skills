---
name: rust-code-style
description: 'Refactor Rust code to match repository style conventions. Use for style cleanup, import normalization, derive-first refactors, function/type ordering, naming cleanup, and invariant-preserving simplification.'
argument-hint: 'What files/scope should be refactored, and do you want style-only or style+readability cleanups?'
user-invocable: true
---

# Rust Code Style Refactoring

Use this skill to perform repeatable Rust refactors that bring code into compliance with the target repository style, while preserving behavior.

## Outcome

Produce a refactor that:
- Matches local repository style and surrounding file conventions
- Preserves behavior, public APIs, and side-effect ordering unless explicitly requested otherwise
- Prioritizes correctness and maintainability over cosmetic edits
- Avoids unnecessary recomputation, writes, and structural churn
- Keeps diffs small and self-contained

## When To Use

Use when the request includes:
- code style cleanup
- refactor to conventions
- normalize imports or derives
- improve readability without behavior changes
- align with project instructions

## Inputs

Collect:
- Scope: files/modules/PR branch to refactor
- Intention: style-only vs style + readability cleanup
- Constraints: API stability, no-test-change preference, or explicit exception

If scope is missing, ask for it.

## Repository Style Baseline

Apply these conventions from the target repository instructions and local code patterns:
- Prefer small, self-contained changes.
- Keep functions small, clear, deterministic.
- Prefer deriving traits over manual implementations when equivalent.
- Use common-root imports with at most one level of brace nesting (module or item).
- Flatten any deeper nested `use` brace trees; do not preserve deeper nesting even when nearby code uses it.
- Prefer qualified enum variants when that improves clarity.
- Default to `pub`; use `pub(crate)` only when containing module is crate-public.
- Prefer adding fields to existing structs over parallel data structures.
- Prefer constructor functions and derive helpers for newtypes.
- Include `Copy` and `Clone` for newtypes when wrapped type supports them.
- Prefer named structs over tuple returns when ordering/intent is ambiguous.
- Prefer behavior-named methods over exposing raw mode enums.
- For binary options, prefer `bool` fields over two-variant enums when no additional states are expected.
- For option/flags structs, prefer `Default` as the baseline state and explicit opt-in fields for enabled behavior.
- Keep one source of truth for mutable state; avoid mirrored caches unless justified.
- Keep invariant checks and mode gating at one layer.
- Prefer explicit panic/error for invariant violations over silent fallback/continue.
- Avoid defensive fallback branches where invariants guarantee the path.
- Convert at boundaries instead of carrying optional identities through lower layers.
- Cache repeated expensive state lookups at callers when appropriate.
- During event-flow refactors, keep side-effect dispatch ordering unchanged.
- In tests, keep test cases before helpers.
- Use concise, intent-focused comments only when logic is non-obvious.

## Procedure

1. Establish scope and safety rails.
- Confirm target files and whether behavior must remain identical.
- Identify boundary-sensitive paths: event flow, state transitions, protocol/config conversions.

2. Gather local style context.
- Read the repository instruction files and neighboring modules.
- Infer local file-level conventions before transforming imports/order/comments.
- Check diagnostics first before running heavy build commands.

3. Plan minimal refactors.
- Group edits into small independent steps (imports, derives, naming, ordering, invariant cleanup).
- Skip non-essential rewrites that increase churn without maintenance benefit.

4. Apply style transformations in this order.
- Imports: normalize to common-root lines and keep brace nesting to one level maximum.
- Traits/newtypes: replace equivalent manual impls with derives; keep trait surface stable.
- Control flow: prefer exhaustive `match` for enum-driven behavior where it improves clarity.
- Use `matches!` for simple boolean pattern checks and filter predicates; do not force equivalent `match`/`if let` forms that reduce readability or trigger lint noise.
- Naming: remove ambiguous prefixes/suffixes (for example `maybe_`, `_ref`) in favor of neutral names.
- Structure: keep high-level functions first, helpers later; maintain call-hierarchy ordering when moving/extracting.
- Place local helper types and validators lower in the file when they are implementation details of a specific flow.
- Type layout: keep each type declaration contiguous with its own impl blocks; avoid interleaving impls for different types.
- State/invariants: remove silent fallbacks and redundant mirrored state where invariants can be explicit.
- Comments: keep only concise intent comments for non-obvious logic.

5. Validate behavior preservation.
- Confirm no unintended API or semantic changes.
- Re-check diagnostics in edited files.
- Run targeted build/check only when needed or requested.

6. Finalize with concise change rationale.
- Summarize what style constraints were applied.
- Call out any assumptions and residual risks.

## Decision Points

- If the file has an established local style that conflicts with generic rules:
  prefer local style unless it creates correctness or maintenance risk.
- If a style change risks behavior (event ordering, invariants, boundary conversions):
  preserve behavior first; narrow to safe transformations.
- If the request is style-only:
  avoid opportunistic refactors unrelated to explicit style constraints.
- If test changes are not requested:
  do not add tests by default; only flag missing regression tests when risk is high.

## Completion Criteria

Mark complete when all are true:
- Scope files are style-aligned with repository conventions
- Behavior and side-effect ordering are preserved
- Diff is minimal and focused
- Diagnostics are clean for edited files (or outstanding issues are explicitly reported)
- Assumptions/risks are documented

## Output Template

1. Applied Style Changes
- File: ...
- Change: ...
- Reason: ...

2. Behavior Safety Check
- Preserved invariants/event ordering: yes/no
- API compatibility notes: ...

3. Risks / Assumptions
- ...
