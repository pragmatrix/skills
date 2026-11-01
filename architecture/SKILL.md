---
name: architecture
description: 'Keep a Rust workspace''s ARCHITECTURE.md current: regenerate its code graph of crates, modules, and external crates, and check it against the components declared in architecture.toml. Use when asked to update or set up the architecture document or components, after adding or removing a crate, module, or dependency, or when a check finding needs a decision.'
argument-hint: 'Workspace root (default: the current directory)'
user-invocable: true
---

# Architecture

Two things make up a workspace's architecture here:

- The **code graph** is derived from the code, so it is never edited by hand. It holds every crate and module, public or private, at any depth. A module-level `use`, or a type named in an item signature, becomes one edge between the two siblings it lies in, under their common parent. The used items behind an edge are its **reaches**. Each module also records the external crates it uses.
- **Components** are declared by the user in `architecture.toml`. A component is an abstract part of the architecture as the user sees it, and it may span several modules or crates. Each component has a name, a one-sentence responsibility, the `realized_by` paths that implement it, and the components it `depends_on`. The `depends_on` lists form a DAG. A module belongs to the components of its most specific listed path, so a path covers its subtree down to the next path that is listed for itself. The same path may be listed under several components.

The **check** compares the two. A code dependency between modules is *explained* when a component of the source is, or directly depends on, a component of the target. It is *transitive* when only a longer component path connects them, and *unexplained* when nothing does. The check also reports unmapped modules, stale declared dependencies, cycles among components, and `Cargo.toml` dependencies that nothing reaches.

`architecture.py` (next to this file) does all deterministic work. Its docstring lists the commands. `update` regenerates the block between the markers in `ARCHITECTURE.md` and rewrites `architecture.toml` in canonical form. Text outside the markers is the user's prose and stays as it is.

## 1. Prepare

The script needs `python3` 3.11 or newer and `cargo-modules`. When `cargo-modules` is missing, ask the user before running `cargo install cargo-modules`, because it installs globally. The workspace root is the directory with the workspace's `Cargo.toml`. `ARCHITECTURE.md` and `architecture.toml` live there.

Done when both tools run.

## 2. Regenerate

Run `python3 <skill-dir>/architecture.py update --root <workspace root>`. It prints the check findings, which also appear in the document's Check section.

Done when the command succeeded.

## 3. Declare components (first run only)

When no components are declared yet, propose them from the code graph in `ARCHITECTURE.md`. Good candidates are crates, clusters of modules that mostly use each other, and modules that many others use. Draw each proposed component's `depends_on` from the code edges between its modules, so the first check comes out close to clean. Settle the proposals with the user, about three decisions at a time, each one naming the modules it covers and the dependencies it implies. Write the settled components to `architecture.toml` and regenerate.

Done when every component the user settled is in `architecture.toml` and the regenerated check shows no unknown paths or names.

## 4. Settle findings

Take every finding to the user, a few at a time, each with its options and their effects:

- **Unexplained:** declare the component dependency, map the source or target module to another component, or change the code.
- **Transitive:** declare the direct dependency, route the code through the component in between, or keep it as it is.
- **Unmapped:** add the module to a component, or list a more specific path.
- **Stale:** remove the declaration, or keep it for code that is on its way.
- **Cycle:** break it by moving code or splitting a component.
- **Unused crate dependency:** function bodies are not analyzed, so first search the crate for the dependency's name. Remove it from `Cargo.toml` only when nothing uses it.

Apply each decision to `architecture.toml` or to the code, then regenerate.

Done when the user has decided every finding. A finding the user keeps stays in the Check section.

## 5. Report

Name the files that changed and summarize the decisions. `architecture.py view --base <rev>` writes a diff view against a revision, which the user can open in VS Code's Markdown preview.

## Limits

The graph comes from `cargo-modules`, which sees module-level `use` declarations and item signatures but not function bodies. A dependency used only inside a body, by a full path or a local `use`, has no edge. Reaches name each item where it is defined, not the path written in the `use`. Each package contributes one target, its library or else its first binary, analyzed with default features and without test code.
