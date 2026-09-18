---
name: pr
description: 'Commit all outstanding changes, run formatting and tests, and create or update a GitHub PR or GitLab MR using gh or glab. Use when the user wants to commit work and open or update a PR or MR.'
argument-hint: 'Base branch (default: derived from git and the hosting CLI)'
user-invocable: true
---

# Create PR

Commit all outstanding work, run the formatting and test gates, and open/update a GitHub PR or GitLab MR for the current branch. This path does **not** rebase or run a code review.

## When to Use

Use when the request includes anything like:
- commit and open a PR
- commit this and PR it
- create/update a PR for the current branch
- `/pr`

Do not use when the user wants a rebase or a code review as part of the workflow.

## Prerequisites

- The CLI matching the remote host is installed and authenticated.
- There is a GitHub or GitLab remote for the repo.
- The current branch has unmerged commits it makes sense to review.

## Inputs

- Base branch (default: derive from `git`/`gh`; common defaults are `master` or `main` — fall back to the branch that HEAD diverged from, or ask if ambiguous).

## Procedure

1. **Confirm prerequisites.**
   - Inspect `git remote -v` to determine whether the repository is hosted on GitHub or GitLab.
   - Invoke the matching host CLI directly when creating or inspecting the PR. If it is unavailable or authentication fails, report that failure then.
   - Derive the GitLab repository path from the remote and pass it explicitly with `--repo <group/project>` because automatic lookup can fail for self-hosted GitLab remotes.
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

4. **Create or update the PR/MR.**
   - Draft the proposed title and complete body, including any required submodule references and the AI disclosure block. Present both to the user and ask for explicit permission to post or update the remote PR/MR. Do not create or update the PR/MR until the user approves the exact text, or provides revised text.
    - On GitHub, detect with `gh pr view <branch>`, create with `gh pr create --base <base> --head <branch> --title <title> --body-file <file>`, or update with `gh pr edit <pr> --title <title> --body-file <file>`.
    - On GitLab, detect with `glab mr view <branch> --repo <group/project>`, create with `glab mr create --repo <group/project> --source-branch <branch> --target-branch <base> --title <title> --description-file <file> --yes`, or update with `glab mr update <mr> --repo <group/project> --title <title> --description-file <file> --yes`.
   - **When multiple PRs exist (submodule and parent), reference the submodule PRs from the parent's PR body.** Add a "Submodule PRs" section listing each affected submodule, its branch, and its PR link (e.g. `- mylib@branch: <url>`), placed before the AI disclosure block so reviewers can see the dependent changes. The submodule's own PR body must not mention the parent project in return (see step 2).
   - **Always end the PR body with an AI disclosure block** (unless the user says otherwise). Append a `> [!NOTE]` block at the end of the body:
     ```markdown
     ---

     > [!NOTE]
     > This pull request was developed with assistance from an AI coding agent alongside the author.
     ```
   - Use a concise body structure with a `## Rationale` section explaining why the change is needed, followed by a `## Summary` section. Add other sections only when they improve reviewability.
   Author the body in a temp file and pass it through `--body-file` for `gh` or `--description-file` for `glab` so the disclosure is included reliably.
   - Confirm the PR was created/updated successfully. This is the skill's end state by default — do **not** merge on your own.

5. **Wrap up.**
   - Report the PR result (number/URL, base → head).
   - Note any residual risks or deferred findings.
   - If the user asks to merge or clean up the branch, that is a separate step done only on their explicit request.

## Decision Points

- If the matching host CLI is not installed or authenticated, or there is no supported GitHub/GitLab remote: stop and tell the user what's needed.
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
   - Created or updated: host, title, number/URL, base → head
   - If submodules were affected: each submodule PR finalized first (title, number/URL), referenced from the parent's PR body
2. Notes
   - Residual risks, deferred findings, next steps (e.g. awaiting user to merge/auto-merge, or to clean up the branch)
