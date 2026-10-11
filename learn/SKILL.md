---
name: learn
description: Update agent memory/skills from what was surprising in the session. Use when the user invokes /learn.
user-invocable: true
disable-model-invocation: true
---

# Learn

Turn this session's surprises into durable knowledge. Not a session summary — a delta against what is already known.

## 1. Collect evidence

Review the session end to end (your recollection of turns, any session notes, tool outputs). Look for:

- **Contradicted knowledge** — something you believed (from memory, docs, or intuition) that turned out wrong.
- **Repeated iteration** — anything that cost more than one attempt (silently failed edits, wrong tool, wrong command, hang).
- **Near misses** — mistakes you caught just in time; they are cheap to record now, expensive later.
- **Workarounds discovered** — environment or tool behavior that required a non-obvious fix.

Do **not** capture things that worked as expected. Surprising only.

Scope each candidate by what it actually is:

- **Environment/tool behavior** (sandbox, shell, editor, package manager) → user memory.
- **Codebase conventions, build commands, project facts** → repo memory for that workspace.
- **A reusable workflow or judgment** → consider a skill or an edit to one, if the insight changes *how* you should act, not just *what* you know.

Everything else is session trivia — discard it.

## 2. Distill into transferable rules

For each candidate, write the lesson **as a mechanism, not an anecdote**:

- Generalize away project names, dates, and session specifics — keep them only when the *reason* for a behavior lives there.
- Structure: the **mechanism** (why it happens), the **symptom** (how it looks from the agent's chair), the **fix or mitigation** (what to do next time).
- One fact per entry, brief. If an entry needs a preamble explaining the old behavior, it is too long.
- Prefer editing an **existing** memory file (grouping by topic) over creating a new one; merge near-duplicates into the sharper formulation.
- Verify against existing memory first: if an entry already covers it, update it — don't add a parallel one.

## 3. Remove

Removal is part of learning. Delete or rewrite entries that:

- This session **proved wrong**.
- Were already merged into a better formulation.
- Describe a behavior that has since changed (mark with a re-test date instead if uncertain).

## 4. Apply with a gate

Before writing anything, show the user the final set of changes — additions, edits, and deletions as a compact list (file → what changes). Apply on confirmation.

- [ ] Every captured item was genuinely surprising, and a plausible mechanism exists.
- [ ] Each entry states mechanism + symptom + fix, usable in an unrelated project.
- [ ] Duplicates merged; outdated entries removed; existing files preferred.
- [ ] Changes scoped to the right memory tier.