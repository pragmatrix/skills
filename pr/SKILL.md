---
name: pr
description: 'Commit all outstanding changes, run the formatting and test gates, and create or update a GitHub PR for the current branch using the gh CLI. Use when the user wants to commit work and open/update a PR.'
argument-hint: 'Base branch (default: derived from git/gh)'
user-invocable: true
---

# Create PR

Commit all outstanding work, run the formatting and test gates, and open/update a GitHub PR for the current branch. This is the path from "changes committed" to "PR opened/updated" with the format/test gates enforced; it does **not** rebase or run a code review.

## When to Use

Use when the request includes anything like:
- commit and open a PR
- commit this and PR it
- create/update a PR for the current branch
- `/pr`

Do not use when the user wants a rebase or a code review as part of the workflow.

## Prerequisites

- `gh` CLI is installed and authenticated (`gh auth status`).
- There is a GitHub remote for the repo.
- The current branch has unmerged commits it makes sense to review.

## Inputs

- Base branch (default: derive from `git`/`gh`; common defaults are `master` or `main` — fall back to the branch that HEAD diverged from, or ask if ambiguous).

## Procedure

1. **Confirm prerequisites.**
   - Run `gh --version` (exit 0 means available).
   - Run `gh auth status` and `git remote -v` to confirm auth and a GitHub remote.
   - Capture the current branch: `git branch --show-current`.
   - Determine the base branch and the diff range `base...HEAD`.
   - Detect affected submodules: submodules with unmerged commits on a dedicated branch (check `git status` / `git submodule status`); note each one's repo and branch. Skip clean submodules.

2. **Finalize affected submodule PRs first (recursive).**
   - For each affected submodule, recursively run this entire skill inside the submodule on its branch before proceeding with the parent: commit outstanding work, then create or update the submodule's PR. Submodules may themselves contain submodules, so recurse depth-first (submodules of submodules first).
   - **Do not mention the parent project in a submodule's PR body.** A submodule PR describes only the submodule's own changes and must stand alone (no references to the parent repo, its branches, or its feature names). Cross-references flow one way only: the parent's PR references the submodule PRs, never the reverse.
   - Finalize submodules before the parent so the parent's submodule pointer bump references a commit that is already PR'd upstream. Ideally merge the submodule PR before finalizing the parent so the parent's pointer targets a merged commit.
   - After each submodule is finalized, the parent shows an updated pointer; include that pointer bump in the parent's own finalization.

3. **Commit outstanding work.**
   - Load and follow the **commit** skill to split any uncommitted changes in the working tree into logical, scope-prefixed commits. The **commit** skill runs the formatting and test gates before committing, so the committed state is formatted and passes tests.
   - Do not proceed until the working tree is clean (all changes committed).

4. **Create or update the PR.**
   - If no PR exists for the branch, create one with `gh pr create`:
     - `--base <base> --head <branch>`
     - `--title` from the branch's primary intent
     - `--body` summarizing the change
   - If a PR already exists, update it instead of creating a duplicate:
     - `gh pr status` / `gh pr view <branch>` to detect an existing PR
     - Update title/body/description with `gh pr edit <pr> --title ... --body ...`
   - **When multiple PRs exist (submodule and parent), reference the submodule PRs from the parent's PR body.** Add a "Submodule PRs" section listing each affected submodule, its branch, and its PR link (e.g. `- mylib@branch: <url>`), placed before the AI disclosure block so reviewers can see the dependent changes. The submodule's own PR body must not mention the parent project in return (see step 2).
   - **Always end the PR body with an AI disclosure block** (unless the user says otherwise). Append a `> [!NOTE]` block at the end of the body:
     ```markdown
     ---

     > [!NOTE]
     > This pull request was developed with assistance from an AI coding assistant (Copilot) alongside the author.
     ```
     When authoring the body, apply `gh pr create --body-file <file>` or `gh pr edit <pr> --body-file <file>` from a temp file so the disclosure is included reliably.
   - Confirm the PR was created/updated successfully. This is the skill's end state by default — do **not** merge on your own.

5. **Wrap up.**
   - Report the PR result (number/URL, base → head).
   - Note any residual risks or deferred findings.
   - If the user asks to merge or clean up the branch, that is a separate step done only on their explicit request.

## Decision Points

- If `gh` is not installed, not authenticated, or there is no GitHub remote: stop and tell the user what's needed — do not open a PR.
- If the base branch is ambiguous: ask which base to diff against and target.
- If the working tree is dirty: run the **commit** skill to commit outstanding work before creating the PR.
- If submodules are affected: finalize each affected submodule's PR first (recursively) before the parent, so the parent's pointer bump references an already-PR'd commit, and reference the submodule PRs in the parent's PR body.
- If the user wants a rebase or a code review as part of the workflow, note that this skill does not perform those steps.

## Completion Criteria

Mark the skill complete when all of the current request's steps are true:
- Outstanding work was committed with the commit skill (which enforces the formatting and test gates)
- If submodules were affected: each affected submodule's PR was finalized (recursively) before the parent's PR, and the parent's PR body references the submodule PRs
- A PR exists for the branch (created or updated) reflecting the final state
- The PR was merged only on an explicit user request

## Output Template

1. PR
   - Created or updated: title, number/URL, base → head
   - If submodules were affected: each submodule PR finalized first (title, number/URL), referenced from the parent's PR body
2. Notes
   - Residual risks, deferred findings, next steps (e.g. awaiting user to merge/auto-merge, or to clean up the branch)
