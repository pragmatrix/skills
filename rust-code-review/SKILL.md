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
- Focuses on correctness, behavioral regressions, and test additions before style
- Flags entangled designs (complecting) when it has a real change, debug, or policy cost
- Audits the comments on changed lines: short, why-focused, no restatement of the code
- Audits added or changed tests against the opt-in test policy, including flagging unrequested tests
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
- Extract long closures (roughly more than five statements) that contain real logic into a named function placed next to its wrapper, leaving the closure body as a single call.
- Flag designs that braid independent concerns together — state with value/time, types with implementation, policy with execution structure, timing/location with the caller — when disentangling them would localize a change, a bug, or a policy edit. Judge the artifact's changeability, not the authoring convenience, and say when the complexity is inherent instead of incidental.
- Audit comments on the changed lines and their surroundings against three axes: every comment must be very short, must not restate what the code plainly shows, and must make the why of the change visible. Flag a missing why, an over-long comment, and superfluous description, each with `path:line` and suggested replacement or deletion text. Brevity has open exceptions: a genuinely complicated subject — an involved algorithm, a subtle invariant, a workaround — may keep a longer comment when every sentence states a why; name such comments as exempt instead of reporting them.
- Flag a comment that contrasts the code with a design not visible at that spot ("owned outright rather than mutex-guarded", "a compile error instead of a runtime check"): it explains the change, not the code. Give the rewritten text stating the reason. Do not flag deliberate history or open notes — a dated measurement, a rejected alternative, a `TODO` or `Architecture:` question each carry a reason. Only a comment whose content is merely that the code changed ("previously X", "replaces the old ...") is a finding.
- The user explicitly requests concise rationale comments for non-obvious behavior, invariants, coordinate conversions, and architectural constraints without a per-task request. Verify relevant rationale is preserved or updated when commented code changes, preferably in one line; flag its unexplained removal.

5. Evaluate error handling and boundary conversions.
- Prefer explicit errors over defensive fallbacks for unexpected states.
- Verify application-level errors carry useful context.
- At data/protocol boundaries, check that source-format types convert explicitly into runtime/domain types.

6. Evaluate tests as risk controls.
- Tests are opt-in: an added test is justified only when the brief asked for tests, or when a test is the only reasonable way to pin down counter-intuitive or exceptional semantics.
- Flag any added test that re-checks ordinary behavior, mirrors neighbouring test files, or restates the implementation in assertions: report a Low-severity finding naming the behavior it merely repeats, and recommend deleting it.
- For an added test that stays, name the non-obvious semantics it explains; if you cannot, the finding above applies.
- Flag a missing regression test only when the brief asked for that coverage or the changed semantics are counter-intuitive or exceptional; otherwise state the behavior is uncovered and needs no test under this policy.
- Check test quality where tests are kept: each must assert the behavior and be able to fail, not be a tautology or a snapshot of the implementation.
- In test modules, prefer test cases before helpers when modified.

7. Prepare final review output.
- Findings first, severity ordered: Critical, High, Medium, Low. Number each item `<section>.<n>` per the template.
- For each finding include: problem, impact, evidence, and minimal fix direction.
- Include a comment audit section for the changed lines: missing why, over-long comments, and superfluous restatement, with suggested short text.
- Include a test audit section: each unrequested test that re-checks ordinary behavior (recommend deletion), each kept test with the non-obvious semantics it explains, and any required missing test.
- If no findings, state that explicitly and note residual risks or testing gaps.

## Decision Points

- If change is behavior-critical (state transitions, event ordering, protocol boundaries):
  perform thorough review and scrutinize regressions first.
- If change is local and mechanical:
  perform quick review focused on compile-time and local invariants.
- If the task is style refactoring rather than review:
  hand off to rust-code-style.
- If a long closure contains real logic:
  report a Low-severity finding and direct extraction into a named function next to its wrapper.
- If requested behavior is ambiguous:
  ask one targeted clarifying question, then continue.
- If a comment does not make its why visible, is longer than a sentence or two, or restates the code:
  report a Low-severity finding and give the shorter replacement text or say to delete it.
- If a comment contrasts the code with a design that is not visible at that spot:
  report a Low-severity finding and give the rewritten text stating the reason. Deliberate history and open notes (dated measurements, rejected alternatives, `TODO`/`Architecture:` questions) are not this; leave them.
- If a comment's only content is that the code changed:
  report a Low-severity finding; that record belongs in git and the ADR, not in the code.
- If a comment is long because its subject is genuinely complicated:
  leave it, list it as an exempt exception, and require only that each sentence carries a why.
- If an added test re-checks ordinary behavior, mirrors neighbouring tests, or restates the implementation:
  report a Low-severity finding to delete it, unless the brief asked for tests or it pins down counter-intuitive semantics.
- If changed behavior is counter-intuitive or the brief asked for coverage and nothing pins it down:
  report the missing test and name the non-obvious semantics it must lock in.

## Completion Criteria

Mark review complete when all are true:
- Scope is fully covered
- Findings are severity-ordered and evidence-based
- Major regression and invariant risks were checked
- Added and changed tests were audited against the opt-in policy: each is requested by the brief or pins down counter-intuitive semantics, and unrequested tests were flagged
- Comments on changed lines were audited for a visible why, brevity, and no restatement
- Any comment exempt from brevity was named with its reason
- Residual risks/assumptions are called out

## Review Output Template

Number every individual item as `<section>.<n>` (1.1, 1.2, 2.1, …) so the user can refer to it.

1. Findings
- 1.1 [Severity] Short title
- Problem: ...
- Impact: ...
- Evidence: file:line
- Suggested fix: ...

2. Comment Audit
- 2.1 [path:line] Missing why / too long / restates code
- Suggested short text or delete
- Exempt from brevity: 2.2 [path:line] reason

3. Test Audit
- 3.1 [path:line] Unrequested test that re-checks ordinary behavior — recommend delete
- 3.2 [path:line] Kept test — the counter-intuitive semantics it pins down
- 3.3 Missing test required by the brief or by counter-intuitive semantics (or: none required under the opt-in test policy)

4. Open Questions / Assumptions
- 4.1 ...

5. Change Summary (brief)
- ...
