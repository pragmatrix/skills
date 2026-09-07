---
name: project-setup
description: 'Scaffold a new Rust project with a workspace layout, tooling conventions, and the three-layer AI instruction architecture. Use when setting up a new Rust project from scratch or adding agent/instruction scaffolding to an existing one.'
argument-hint: 'Project name, crate type (binary/library/workspace), and any known dependencies or conventions.'
user-invocable: true
---

# Project Setup

Use this skill to scaffold a new Rust project with a consistent, maintainable structure and a complete AI/agent instruction setup. It encodes conventions proven in a large multi-crate terminal workspace.

## Outcome

Produce a project that:
- Uses a Cargo workspace layout from day one
- Has a `justfile` centralizing non-obvious commands
- Pins formatting/lint policy in committed config
- Ships the three-layer instruction architecture
- Includes the "review at finalization" rule
- Keeps generic skills global, not per-repo

## When To Use

Use when the request includes words like:
- new project
- set up a Rust project
- scaffold
- initialize workspace
- add agent instructions

Use for both greenfield projects and adding instruction scaffolding to an existing project.

## Inputs

Collect:
- Project name and location
- Crate type: binary, library, or workspace
- Known dependencies or conventions (optional)
- Whether to include the AI instruction scaffolding

If the crate type or location is missing, ask for it.

## Procedure

1. Establish the workspace layout.
- Create a root `Cargo.toml` with `[workspace]` members.
- Put the first crate under a top-level folder (e.g. `src/` for a single binary, or a named crate folder for a workspace).
- Keep shared dependency versions aligned across any nested workspaces or submodules.

2. Add tooling conventions.
- Create a `justfile` with the non-obvious commands (build, run examples, feature-flag runs, env vars).
- Add `rustfmt.toml` and `clippy.toml` to pin formatting and lint policy; commit them so CI enforces style and reviewers focus on correctness.
- Document feature flags explicitly (e.g. a `metrics` feature gating a dependency, with the run command).

3. Add the three-layer instruction architecture.
- `.github/copilot-instructions.md` — project-specific facts: crate layout, commands, architecture anchors, submodule notes.
- `shared-instructions.md` — generic reusable guidance: code style, design principles, Rust idioms, safety & quality, communication, continuous learning, documentation.
- `.github/instructions/*.instructions.md` — topic-specific rules (testing, error handling, data loading) with `applyTo` globs so they load only when relevant.

4. Add the "review at finalization" rule.
- In `shared-instructions.md`, add a `## Code Review` section: run the `rust-code-review` skill after the series of edits is complete and before declaring the work done, for any non-trivial change; exempt trivial/mechanical changes.

5. Write instructions with "why".
- For each consequential rule, include the reasoning (e.g. "derives are less error-prone and stay in sync with the type").
- Keep authoring rules always-on; do not strip them just because a review skill overlaps. The overlap is intentional: the reviewer verifies the author followed the rules.

6. Keep skills global, not per-repo.
- For generic skills (code review, code style), reference the global ones in `~/.copilot/skills/` rather than duplicating them in the repo.
- Only create repo-level skills for genuinely project-specific workflows.

## Decision Points

- If the project will have submodules or nested workspaces: document the version-alignment rule up front.
- If the project is a library vs. binary: adjust the workspace layout and example entry points accordingly.
- If the user only wants scaffolding (no code): skip the workspace/tooling steps and focus on the instruction architecture.

## Completion Criteria

Mark setup complete when all are true:
- Workspace layout is in place
- Tooling conventions are committed
- Three-layer instruction architecture exists
- "Review at finalization" rule is present
- Generic skills are referenced globally, not duplicated

## Output Template

1. Project structure
- ...

2. Tooling
- ...

3. Instruction files
- ...

4. Next steps
- ...
