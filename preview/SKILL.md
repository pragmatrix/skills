---
name: preview
description: Preview pending code changes as compact diagrams before the user reads the diff. Use when the user asks to preview, visualize, or "show me" what changed or will change, or wants the shape of a change before reviewing it.
argument-hint: 'Which changes: unstaged, staged, or unpushed'
---

Draw the shape of pending changes so the user grasps them before reading the diff. Read-only: edit nothing, compile nothing.

## Source

Check which of these are non-empty (`git diff`, `git diff --cached`, unpushed commits against the upstream, else the default branch). Ask the user which to preview, offering only the non-empty ones.

When all are empty, preview the plan agreed in this session instead. When there is no concrete plan either, say what is missing and stop.

## Views

Open each view with one line saying what it shows. Keep prose brief; the diagram carries the point. Pick the smallest set that covers the change, usually one or two.

**Type changes** are the primary view. Show new and changed types, traits or interfaces, and signatures as a `diff` block of declarations only: fields, variants, method signatures, visibility. Leave bodies out (`...`). Add a Mermaid `classDiagram` when relationships between types change.

**Integration** shows where large new code plugs into existing modules. Use a `diff` block over a call tree, or a Mermaid `sequenceDiagram` when several modules interact. Mark each existing module with its path, mark new elements `(new)`.

**Layout** is a shallow file tree `diff`, only when files move, appear, or split.

Ground every name and path by reading the code. Mark anything not yet in the code `(new)`.

## Done

- Every change in the chosen source appears in at least one view, marked `+`, `-`, or `~`.
- Unresolved design questions are listed as open questions, never drawn as settled.

Then stop and ask which parts the user wants to change. Implementation waits for their answer.
