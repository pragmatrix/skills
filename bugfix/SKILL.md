---
name: bugfix
description: "Use when debugging a bug, hang, regression, runtime failure, or unexpected behavior. Requires root-cause evidence, a focused hypothesis test before production edits, and explicit communication of experiments."
---

# Bugfix Workflow

Use this workflow for bugs, hangs, regressions, runtime failures, and unexpected behavior.

## 1. State the hypothesis

- Identify the concrete observed symptom and the narrowest code path that could control it.
- State one falsifiable hypothesis about the root cause.
- Name the cheapest focused check that could confirm or falsify it.
- Do not broaden repository exploration once the controlling path and discriminating check are known.

## 2. Test before editing

- Prefer building a focused test case first: a unit test, regression test, minimal reproduction, diagnostic, trace, or targeted log.
- Make the check fail for the reported behavior and pass when the hypothesized cause is absent or corrected.
- If a test cannot be added, explain why and use the narrowest available runtime or diagnostic check instead.
- Do not change production code merely because a hypothesis is plausible.

## 3. Edit with evidence

- Change the smallest code surface that directly controls the verified failure.
- Preserve unrelated user changes.
- If evidence is incomplete and an edit is useful to test the hypothesis, announce it as an experiment before applying it.
- Keep experiments minimal and reversible; do not present them as fixes until validation supports them.

## 4. Validate immediately

- After the first substantive edit, run the same focused test or diagnostic that tests the hypothesis.
- If it fails, repair the same slice and rerun the focused check before expanding scope.
- If it falsifies the hypothesis, step to the nearest more direct controlling path and form a new falsifiable hypothesis.
- Finish with an executable post-edit validation whenever the environment provides one.

## 5. Report precisely

- Separate verified facts, hypotheses, experiments, and remaining uncertainty.
- Distinguish independent causes when debugging multiple symptoms.
- Report the focused checks run and their results.
- Do not claim a root cause or fix based only on a symptom disappearing.
