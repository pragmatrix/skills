---
name: code-review-core
description: 'Language-agnostic code review procedure: correctness and regression checks, complecting, comment and test audits, severity-ordered findings with file/line evidence. Loaded by language review skills such as rust-code-review; use directly to review changes in a language that has no review skill of its own.'
user-invocable: false
---

# Code Review Core

The review workflow shared by every language. A language review skill loads this one and binds it: it names the **shared standards** (the house standards file whose rules settle violations), adds its convention checks to step 4, and names its style skill. Without a language skill, the shared standards are the repository's own instruction files and written conventions.

## Outcome

Produce a review that:
- Lists findings first, ordered by severity
- Focuses on correctness, behavioral regressions, and test additions before style
- Flags entangled designs (complecting) when it has a real change, debug, or policy cost
- Audits the comments on changed lines against the shared standards
- Audits added or changed tests against the opt-in test policy, including flagging unrequested tests
- Reports style/convention issues only when they have clear correctness or maintenance impact
- Delegates style refactoring work to the language's style skill
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

Use this for changes where local conventions matter.

## Inputs

Collect:
- Scope: PR, branch diff, or specific files
- Intent: bug-finding only, or bug + maintainability
- Depth: quick scan or thorough review

If scope is missing, ask for it.

## Procedure

1. Establish review scope.
- Prefer the active PR when review is about current changes.
- Otherwise identify changed files in the requested scope.

2. Gather context before judging details.
- Read surrounding modules and affected call paths.
- Identify whether changed code is on hot paths, event flows, or conversion boundaries.
- Check existing diagnostics first when available.

3. Run correctness and regression checks first.
- Validate invariants are preserved and not silently bypassed.
- Flag silent fallback/continue logic where explicit failure is expected.
- Verify mutable state has one source of truth; avoid mirrored caches unless justified.
- Flag repeated derivation: a lookup or scan repeated per loop element (often accidentally quadratic), or a second copy of a calculation another function owns.
- Confirm side-effect ordering in eventful flows is preserved.
- For refactors, ensure behavior remains backward compatible unless explicitly changed.

4. Apply language and repository convention checks.
- Run the convention checks the language review skill adds.
- Flag convention/style deviations only when they materially affect correctness, readability-under-change, or maintenance risk.
- If style refactoring is requested or required to address findings, invoke the language's style skill and keep this skill focused on review output.
- Flag designs that braid independent concerns together — state with value/time, types with implementation, policy with execution structure, timing/location with the caller — when disentangling them would localize a change, a bug, or a policy edit. Judge the artifact's changeability, not the authoring convenience, and say when the complexity is inherent instead of incidental.
- Load the comment rules of the shared standards and audit the comments on the changed lines, their surroundings, and every newly added item against each of them. Report each violation with `path:line` and the suggested replacement, new, or deletion text; name comments exempt from brevity instead of reporting them.
- Check new identifiers and comments against the `_Avoid_` terms in the repo's `GLOSSARY.md`; report each use with the canonical term that replaces it.

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

7. Prepare final review output.
- Findings first, severity ordered: Critical, High, Medium, Low. Number each item `<section>.<n>` per the template.
- For each finding include: problem, impact, evidence, and minimal fix direction.
- Include a comment audit section for the changed lines, with suggested text for each violation.
- Include a test audit section: each unrequested test that re-checks ordinary behavior (recommend deletion), each kept test with the non-obvious semantics it explains, and any required missing test.
- If no findings, state that explicitly and note residual risks or testing gaps.

## Decision Points

- If change is behavior-critical (state transitions, event ordering, protocol boundaries):
  perform thorough review and scrutinize regressions first.
- If change is local and mechanical:
  perform quick review focused on compile-time and local invariants.
- If the task is style refactoring rather than review:
  hand off to the language's style skill.
- If requested behavior is ambiguous:
  ask one targeted clarifying question, then continue.
- If a comment violates a rule of the shared standards:
  report a Low-severity finding, unless the missing why hides a real hazard (then say what breaks). A comment that is long because its subject is genuinely complicated is exempt; list it as such.
- If an added test re-checks ordinary behavior, mirrors neighbouring tests, or restates the implementation:
  report a Low-severity finding to delete it, unless the brief asked for tests or it pins down counter-intuitive semantics.
- If changed behavior is counter-intuitive or the brief asked for coverage and nothing pins it down:
  report the missing test and name the non-obvious semantics it must lock in.

## Completion Criteria

Mark review complete when all are true:
- Scope is fully covered
- Findings are severity-ordered and evidence-based
- Major regression and invariant risks were checked
- Every convention check the language review skill adds was applied
- Added and changed tests were audited against the opt-in policy: each is requested by the brief or pins down counter-intuitive semantics, and unrequested tests were flagged
- Comments on changed lines were audited against the shared comment rules, and exempt comments were named
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
