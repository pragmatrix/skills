---
name: rust-code-review
description: 'Review Rust changes for bugs, regressions, invariants, API compatibility, and codebase conventions. Use when asked to review a PR, diff, or Rust file changes and produce severity-ordered findings with file/line evidence.'
argument-hint: 'What should be reviewed (PR, diff, files) and review depth (quick or thorough)?'
user-invocable: true
---

# Rust Code Review

**Load `code-review-core` first** (read `~/.copilot/skills/code-review-core/SKILL.md` when the skill listing is unavailable) and follow its procedure, decision points, completion criteria, and output template. This skill binds it to Rust.

Use rust-code-style when the request is to actively refactor code style.

## Bindings

- **Shared standards**: `~/.copilot/instructions/rust-standards.instructions.md`. Its **Comments** section is the comment rules of step 4, and its **Derive each result once** rule backs the repeated-derivation check of step 3.
- **Style skill**: rust-code-style.
- **Scope**: the changed Rust files.

## Rust Convention Checks

Add these to step 4 of the core procedure:
- Prefer reference coercion (`&value`) over redundant `.as_str()` when it provides the same `&str` input.
- Prefer `then()` / `then_some()` for concise conditional `Option` construction when it keeps intent clear.
- Extract long closures (roughly more than five statements) that contain real logic into a named function placed next to its wrapper, leaving the closure body as a single call. Report each as a Low-severity finding.
- In test modules, prefer test cases before helpers when modified.
