---
name: rust-code-review
description: 'Review Rust changes for bugs, regressions, invariants, API compatibility, and codebase conventions. Use when asked to review a PR, diff, or Rust file changes and produce severity-ordered findings with file/line evidence.'
argument-hint: 'What should be reviewed (PR, diff, files) and review depth (quick or thorough)?'
user-invocable: true
---

# Rust Code Review

Use this skill to run a repeatable Rust code review workflow for a Rust codebase.

## Outcome

Produce a review that:
- Lists findings first, ordered by severity
- Focuses on correctness, behavioral regressions, and missing tests before style
- Reports style/convention issues only when they have clear correctness or maintenance impact
- Delegates style refactoring work to the rust-code-style skill
- Includes concrete evidence (file and line references)
- Calls out risks and assumptions when behavior is unclear

## When To Use

Use when the request includes words like:
- review
- PR feedback
- code audit
- regressions
- bug risk
- missing tests

Use this for Rust changes where local conventions matter.

Use rust-code-style when the request is to actively refactor code style.

## Inputs

Collect:
- Scope: PR, branch diff, or specific files
- Intent: bug-finding only, or bug + maintainability
- Depth: quick scan or thorough review

If scope is missing, ask for it.

## Procedure

1. Establish review scope.
- Prefer the active PR when review is about current changes.
- Otherwise identify changed Rust files in the requested scope.

2. Gather context before judging details.
- Read surrounding modules and affected call paths.
- Identify whether changed code is on hot paths, event flows, or conversion boundaries.
- Check existing diagnostics first when available.

3. Run correctness and regression checks first.
- Validate invariants are preserved and not silently bypassed.
- Flag silent fallback/continue logic where explicit failure is expected.
- Verify mutable state has one source of truth; avoid mirrored caches unless justified.
- Confirm side-effect ordering in eventful flows is preserved.
- For refactors, ensure behavior remains backward compatible unless explicitly changed.

4. Apply Rust and repository convention checks.
- Flag convention/style deviations only when they materially affect correctness, readability-under-change, or maintenance risk.
- If style refactoring is requested or required to address findings, invoke rust-code-style and keep this skill focused on review output.
- Prefer reference coercion (`&value`) over redundant `.as_str()` when it provides the same `&str` input.
- Prefer `then()` / `then_some()` for concise conditional `Option` construction when it keeps intent clear.

5. Evaluate error handling and boundary conversions.
- Prefer explicit errors over defensive fallbacks for unexpected states.
- Verify application-level errors carry useful context.
- At data/protocol boundaries, check that source-format types convert explicitly into runtime/domain types.

6. Evaluate tests as risk controls.
- Do not require adding tests by default.
- Still flag missing regression tests when behavioral risk is high.
- In test modules, prefer test cases before helpers when modified.

7. Prepare final review output.
- Findings first, severity ordered: Critical, High, Medium, Low.
- For each finding include: problem, impact, evidence, and minimal fix direction.
- If no findings, state that explicitly and note residual risks or testing gaps.

## Decision Points

- If change is behavior-critical (state transitions, event ordering, protocol boundaries):
  perform thorough review and scrutinize regressions first.
- If change is local and mechanical:
  perform quick review focused on compile-time and local invariants.
- If the task is style refactoring rather than review:
  hand off to rust-code-style.
- If requested behavior is ambiguous:
  ask one targeted clarifying question, then continue.

## Completion Criteria

Mark review complete when all are true:
- Scope is fully covered
- Findings are severity-ordered and evidence-based
- Major regression and invariant risks were checked
- Missing test risk is explicitly evaluated
- Residual risks/assumptions are called out

## Review Output Template

1. Findings
- [Severity] Short title
- Problem: ...
- Impact: ...
- Evidence: file:line
- Suggested fix: ...

2. Open Questions / Assumptions
- ...

3. Change Summary (brief)
- ...
