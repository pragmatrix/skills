---
name: finalize-pr
description: 'Finalize the current branch as a GitHub PR: commit outstanding work (commit skill), rebase onto the target branch, review with rust-code-review, interact with the user, commit any review changes, run the formatting check and full test suite, then create or update a PR using the gh CLI. If submodules are affected, finalize their PRs first (recursively) before the parent. Use when the user wants to review and open/integrate the current branch as a PR on GitHub.'
argument-hint: 'Branch to finalize (default: current branch)'
user-invocable: true
---

# Finalize PR

Use this skill to take the current branch from "changes committed" to "PR opened/updated on GitHub": it commits any outstanding work with the **commit** skill, rebases onto the target branch, runs a code review, gets your input on the findings, commits any review changes, runs the formatting check and full test suite, then opens or updates a PR with `gh`. If submodules are affected, it finalizes their PRs first (recursively) before the parent. Stopping at the PR is the intended end state unless the user explicitly asks to go further; follow-up options include enabling auto-merge and cleaning up the branch (deleting it on GitHub, switching to the base, pulling, deleting it locally, and removing any worktree named after the branch). It does **not** merge on its own.

For the path that commits outstanding work, runs the format/test gates, and opens/updates a PR — without the rebase and code review — delegate to the **pr** skill instead.

## When To Use

Use when the request includes anything like:
- finalize this branch as a PR
- finalize this work on GitHub
- review the current branch and open/update a PR for it
- review then PR this work
- prepare this branch for review/merge

Pause at the review step and wait for the user's direction before creating the PR — do not open one without input.

## Prerequisites

- `gh` CLI is installed and authenticated (`gh auth status`).
- There is a GitHub remote for the repo.
- The current branch has unmerged commits it makes sense to review.
- Rust-based workflow: load and follow the **rust-code-review** skill for the review portion.

## Inputs

- Branch (default: current branch via `git branch --show-current`).
- Base branch (default: derive from `git`/`gh`; common defaults are `master` or `main` — fall back to the branch that HEAD diverged from, or ask if ambiguous).
- Review depth: quick or thorough. Default quick unless the diff is behavior-critical (state transitions, event ordering, protocol boundaries) — then suggest thorough.

## Procedure

1. **Establish scope.**
   - Confirm `gh` is installed: run `gh --version` (exit 0 means available).
   - Confirm auth and remote: run `gh auth status` and `git remote -v` to ensure a GitHub remote exists.
   - Capture the current branch: `git branch --show-current`.
   - Determine the base branch and the diff range `base...HEAD`.

1.5 **Finalize affected submodules first (recursive).**
   - Detect affected submodules: submodules with unmerged commits on a dedicated branch (dirty submodules per `git status` / `git submodule status`). Skip clean submodules.
   - For each affected submodule, recursively run this entire skill on the submodule's branch before proceeding with the parent: commit, rebase, review, interact, format/test, and open/update the submodule's PR. Submodules may themselves contain submodules, so recurse depth-first (submodules of submodules first).
   - Finalize submodules before the parent so the parent's submodule pointer bump references a commit that is already PR'd upstream. Ideally merge the submodule PR before finalizing the parent so the parent's pointer targets a merged commit.
   - After each submodule is finalized, the parent shows an updated pointer; include that pointer bump in the parent's own finalization.

2. **Commit outstanding work.**
   - Load and follow the **commit** skill to split any uncommitted changes in the working tree into logical, scope-prefixed commits.
   - Do not proceed until the working tree is clean (all changes committed).
3. **Rebase onto the target branch first.**
   - Rebase the current branch onto the target (base) branch so it is up to date: `git pull --rebase origin <base>` (or `git rebase <base>` against an existing local tracking ref).
   - Drop any commits upstream has already absorbed (e.g. an identical fix merged via another PR), so the diff only contains the work unique to this branch and merge will be conflict-free.
   - Resolve any conflicts that arise during the rebase, commit the resolutions to finalize each replayed commit (`git rebase --continue`), and finish the rebase.
   - Re-run the full test suite after the rebase so the reviewed and later PR'd state is verified (not just the pre-rebase commits).
   - Resolve the diff range `base...HEAD` so it reflects only this branch's commits.

4. **Review the branch.**
   - Load the **rust-code-review** skill and apply it to the diff `git diff <base>...HEAD`.
   - Run the review at the chosen depth; collect findings severity-ordered (Critical, High, Medium, Low).

5. **Interact with the user about the review.**
   - Present the findings and give the user the decision points:
     - **Fix issues first** — you address findings, then re-run the review before continuing.
     - **Proceed anyway** — open the PR with known findings (e.g., minor/acceptable risk).
     - **Hold** — stop before any PR.
   - If the user chooses to fix, apply edits, then run the **commit** skill to commit the review changes before proceeding.
   - If findings are style-only and a refactor is wanted, hand off to **rust-code-style**.
   - Do not create or update the PR until the user has explicitly approved proceeding.

6. **Run formatting and lint checks, then the full test suite.**
   - Run the repo's formatting check **before** the test run and before touching the PR, so CI's formatting job (e.g. `cargo fmt -- --check`) does not fail after the PR is opened/updated.
   - If `cargo fmt -- --check` (or the `justfile`'s fmt recipe) reports a diff, run `cargo fmt` (or the equivalent formatter) to apply it, then confirm the check is clean. Treat a clean `cargo fmt -- --check` as a required gate — format changes must be committed with the **commit** skill before proceeding.
   - Then run a full test run (e.g. `cargo test`, plus the repo's other lint steps via its `justfile` if defined). The PR must reflect a state that builds and passes tests.
   - Only proceed to the PR step if formatting and tests are green; otherwise fix, re-run the **commit** skill, and re-run the checks.

7. **Create or update the PR.**
   - Follow the **pr** skill's PR-creation/update procedure (detect an existing PR, create with `gh pr create` or update with `gh pr edit`, and always append the AI disclosure block). The **pr** skill owns the shared mechanics for opening/updating a PR; reuse it here rather than duplicating the steps.
   - Confirm the PR was created/updated successfully. This is the skill's end state by default — do **not** merge on your own.
   - Present the optional next steps and wait for direction: enable auto-merge (`gh pr merge <pr> --auto --merge`) so the PR merges once CI passes, and/or clean up the branch.

8. **Merge (optional, only on explicit request).**
   - Auto-merge: run `gh pr merge <pr> --auto --merge` to merge with a merge commit. Confirm merge commits are allowed first via `gh repo view --json mergeCommitAllowed`. The PR merges automatically once required checks pass; it may merge immediately if CI has already passed.
   - A direct `gh pr merge <pr>` (without `--auto`) is a separate explicit step, done only on the user's request.

9. **Clean up the branch (optional, only on explicit request).**
   - Delete the GitHub branch with `git push origin --delete <branch>` (reliable and works regardless of `gh` subcommand availability; safe once the PR is merged).
   - Switch to the base branch and sync: `git checkout <base> && git pull origin <base>`.
   - Delete the local branch: `git branch -d <branch>` (only after it is merged).
   - Prune stale remote-tracking refs: `git fetch --prune origin`.
   - **Also clean up any git worktree named after the branch you finalize.** If the worktree currently checked out in this workspace matches the branch's name, remove it so it does not linger after the merge: switch back to the base branch, then `git worktree remove <branch>` (optionally with `--force` if it has uncommitted changes, after confirming they are not wanted), and `git worktree prune`. Do this only after the PR is merged and the branch is deleted/synced, so the stale worktree does not keep the deleted branch checked out.
   - `--force` removes the worktree even when another process has its folder open. Git does not check for (and is not blocked by) other processes holding the folder, so this succeeds while VS Code is running there. But doing so leaves that VS Code window pointed at a deleted folder (buffers orphaned, workspace marked removed). Prefer closing the relevant VS Code window before removal, and if you remove while it is open, tell the user that window should be closed/reopened afterward.

10. **Wrap up.**
    - Report the PR result (number/URL, base → head).
    - Note any residual risks or deferred findings from the review step.
    - If the user asks to merge or clean up, that is a separate step done only on their explicit request.

## Decision Points

- If `gh` is not installed, not authenticated, or there is no GitHub remote: stop and tell the user what's needed — do not open a PR.
- If the base branch is ambiguous: ask which base to diff against and target.
- If the working tree is dirty: run the **commit** skill to commit outstanding work before reviewing.
- If submodules are affected: finalize each affected submodule's PR first (recursively) before the parent, so the parent's pointer bump references an already-PR'd commit.
- If the diff is behavior-critical: recommend a thorough review before the user decides.
- If the user picks "fix issues first": commit the fixes with the **commit** skill, loop back to reviewing until findings are resolved or accepted, then continue through the full test run and PR step.
- If the full test run or formatting check fails: fix, commit via the **commit** skill, and re-run the checks before creating/updating the PR.
- If the user picks "hold": stop entirely; nothing is created or updated.
- If the user requests auto-merge or branch cleanup: only act after the PR is created and the user has explicitly asked for those steps.

## Completion Criteria

Mark the skill complete when all of the current request's steps are true:
- Outstanding work was committed with the commit skill
- If submodules were affected: each affected submodule's PR was finalized (recursively) before the parent's PR
- The branch was rebased onto the target branch and dropped any upstream-absorbed commits
- The branch was reviewed with the rust-code-review skill (if part of the request)
- Findings were presented to the user and the user chose a path (fix, proceed, or hold)
- Any review fixes were committed with the commit skill
- The formatting check (e.g. `cargo fmt -- --check`) passed cleanly before creating/updating the PR
- A full test run passed before creating/updating the PR
- A PR exists for the branch (created or updated) reflecting the final state
- If auto-merge was requested: auto-merge was enabled for the PR
- If branch cleanup was requested: the branch was deleted on GitHub, the base branch was checked out and pulled, the local branch was deleted, and any worktree named after the branch was removed
- The PR was merged only on an explicit user request (auto-merge or a direct merge step)

## Output Template

1. Review Result
   - Findings ordered by severity ([Critical]/[High]/[Medium]/[Low]) or "no findings"
   - Which path the user chose: fix / proceed / hold
2. PR
   - Created or updated: title, number/URL, base → head
   - If submodules were affected: each submodule PR finalized first (title, number/URL)
3. Notes
   - Residual risks, deferred findings, next steps (e.g. awaiting user to merge/auto-merge, or to clean up the branch)
