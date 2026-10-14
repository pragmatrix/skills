---
name: commit
description: 'Split a dirty working tree into separated logical commits, each with a mandatory single-line `prefix: summary` message (no body, no attribution). Use when the user explicitly asks for logical/scoped commits, e.g. invoking /commit or requesting commits split by feature. Not triggered by a plain "commit".'
user-invocable: true
---

# Logical Commits

Create clear, reviewable history from a dirty working tree by splitting changes into separate logical commits and committing them one by one.

## When to Use
- User explicitly invokes the skill (e.g. `/commit`) or asks for logical/scoped commits
- Working tree has mixed/staged and unstaged changes that belong to different features
- User wants clean, logically separated history instead of one blob commit

## Procedure

1. **Format the tree.** Run `cargo fmt` (or the project's equivalent formatter) before staging anything, so the committed diff is clean and consistent. If the workspace has multiple crates or a submodule, run the formatter in each relevant root (e.g. `cargo fmt` in the workspace root and in the submodule) so all changed files are formatted. Do not stage or commit until formatting is applied.

2. **Run the narrowest relevant check.** Documentation-only commits need no tests. For code, run the nearest targeted test filter when one exists; otherwise run the changed package's compile check. Do not run full package, dependent-package, workspace, foreign-project, or benchmark suites by default. Do not run benchmarks or `cargo bench` unless explicitly requested; `cargo check --benches` is allowed only to compile changed benchmark code. Apply the same rule inside dirty submodules, but do not rerun submodule checks for a parent pointer-only commit.

3. **Verify branch state (gate).** Check that the repository and any dirty submodules are on a dedicated working branch before committing anything. Only perform this check for the repository and for submodules that actually have changes; skip submodules that are clean. A dedicated branch means `git branch --show-current` returns a non-empty branch name (i.e. not detached HEAD) and that branch isn't a shared/mainline branch like `main`, `master`, or `develop`. If the repository or a dirty submodule is in detached HEAD, on an empty/unborn branch, or on a mainline branch, stop and do not commit — ask the user to check out a dedicated branch first. Running `git status --short` won't reveal this, so verify branch state explicitly.

4. **Commit dirty submodules first.** If any submodules are present and dirty, commit them before touching the parent tree. Each dirty submodule must already be on a dedicated branch (verified in step 3); if it isn't, stop and ask the user to check out a branch inside it. For each dirty submodule, `cd` into it and apply the same procedure (format, test, group, commit) scoped to the submodule, pushing nothing. This keeps submodule changes logically separated from the parent and makes the parent's submodule pointer updates (the new commit hash after the submodule pointer change) clean. After committing inside a submodule, the parent shows the updated pointer; include that pointer bump in the appropriate parent commit. When the parent sets `submodule.recurse=true`, `reset`, `checkout` and `cherry-pick` in the parent also move the submodule checkouts: run them as `git -c submodule.recurse=false ...`, then confirm each submodule is still on its branch.

5. **Inspect the tree.** Run `git status --short` to enumerate all staged and unstaged changes, and `git diff --stat` (+ `git diff --staged --stat` if anything is staged) to gauge scope. Note newly untracked files (`??`) too.

6. **Screen for suspicious, unrelated changes (gate).** Before grouping anything into commits, look for changes that should **not** be committed at all: build/test artifacts (e.g. generated images, logs, output files), temporary scaffolding or placeholder code (e.g. `_doc`-suffixed duplicates, WIP stubs), debug leftovers, generated files that are not meant to be tracked, or changes unrelated to the intended work. Inspect the actual diff of anything that looks off rather than trusting file names alone. For each suspicious change, ask the user whether to exclude it (leave it uncommitted) or clean it up (delete/revert it) before proceeding — do not silently commit it, and do not silently drop it either. Only proceed to grouping once the user has decided.

   Two screening traps observed in practice:
   - **Untracked directories that contain nested git repos** (`dir/.git` file pointing elsewhere, no gitlink in the index) show up as one `??` path; `git add .` pulls in their entire vendored contents (thousands of files). Never bulk-add them; check `git ls-tree HEAD <path>` (already tracked?), whether the tree duplicates already-tracked paths elsewhere, and diff the copies before committing anything.

7. **Group into logical parts.** Partition the changes into coherent units — each unit is a single feature, fix, or concern. Files that belong together (implementing one behavior, or a change plus its tests) go in the same commit. Do not commit two unrelated concerns together.

8. **Commit each part, one at a time.** For each logical part:
   - Stage only the files in that part: `git add <paths>`
   - If a file contains changes belonging to multiple parts, stage only its relevant hunks with **partial staging** so each commit stays coherent. Note that a file cannot be split across commits while its hunks remain unstaged elsewhere — split by hunk, keeping the whole file's hunks accounted for across the commit sequence. Use `git add -p <path>` for this, but prefer the bundled picker `hunk-pick.sh` (next to this file) when naming the hunks up front beats answering prompts, or when the sources use CRLF — it reads and writes bytes, so the patch keeps the file's line endings, which a text-mode patch does not:
   - `<skill-dir>/hunk-pick.sh --list <path>` — number the hunks
   - `<skill-dir>/hunk-pick.sh <path> 1 3 > "$TMPDIR/pick.patch"` — keep hunks 1 and 3
     - `git apply --cached --check "$TMPDIR/pick.patch" && git apply --cached "$TMPDIR/pick.patch"`
   - Re-run `--list` after every commit: committing moves the hunks that follow, so earlier numbers no longer describe the diff.
   - After staging a split file, read `git diff --cached` once to confirm only the intended hunks are in it — a hunk boundary can carry an unrelated line (a stray blank line, a reformat) into the commit.
   - Write a **single-line** message summarizing the change in imperative mood — a subject only, never a body. Keep the subject under ~100 characters; do not pad it with long technical explanations.
   - Always prefix the message with the scope: `prefix: summary`, where `prefix` is in kebab-case (e.g. `mt: ...`, `parser: ...`, `cli-shell: ...`) and names the subproject or area the change is scoped to.
   - Never add a trailer, attribution line, or AI-assistance disclosure such as `Assisted-by`, `AI-Assisted`, or `Co-authored-by` — the message is exactly the one-line subject.
   - Commit: `git commit -m "<prefix>: <summary>"` — a single `-m` carrying only the subject.
   - Move to the next logical part.

9. **Push upstream (gate).** Before pushing, run the checks CI runs: the repository's `just qa` recipe when it has one, otherwise the lint and format commands from its CI workflow. Fix any failure before pushing. If the current branch is a dedicated working branch (verified in step 3) and it has an upstream configured, push the commits to that upstream: `git push`. If the branch is dedicated but has no upstream yet, set one and push: `git push -u origin <branch>`. If the branch is a mainline/shared branch or detached HEAD, do not push. Only push after all commits for the branch are made, so the pushed history is complete.

10. **Finish.** Run `git status --short` to confirm nothing is left, and summarize the commits created (scopes and messages) to the user.

