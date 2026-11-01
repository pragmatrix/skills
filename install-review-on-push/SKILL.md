---
name: install-review-on-push
description: Install a pre-push hook that reviews the pushed commits with one or more review skills, each in a read-only background Claude Code run, and messages the findings to the Claude Code sessions open in the repository.
disable-model-invocation: true
---

# Install Review on Push

`pre-push` (next to this file) is the hook. Before each push it collects the commits the push sends that no remote branch holds yet. After a rebase it leaves out the commits whose changes the remote branch already has. It also leaves out commits whose subject ends in `(review-fix)`, which the `commit` skill writes for commits that only fix review findings, so reviews go one level deep. It then looks for interactive Claude Code sessions whose working directory lies inside the repository's worktree, or in a superproject directory that contains it, so a session in a parent repository covers its submodules' pushes. When there is at least one, it starts one headless `claude -p` run per review skill in the background, named `review-<skill>-<sha>`, which reviews the pushed commits together as one change with that skill. The push goes through at once. Each run sends those sessions its findings, which they handle with the `handle-reviews` skill, and its final answer goes to `.git/review-on-push/<skill>-<sha>.log`. A review skill whose folder holds an executable `prepare` script, such as `architecture-review`, may also call that script from its otherwise read-only run. The hook's comments explain the rest: how the run is kept read-only, and which pushes start nothing. The hook needs `claude` and `jq` on `PATH` and stays silent when either is missing.

## 1. Install

Install into exactly one repository per run. When it is unclear which one is meant, such as for a repository with submodules or inside a submodule, ask the user before installing. A submodule needs its own hook to have its pushes reviewed, and the hook covers sessions in its parent repositories.

Run `<skill-dir>/install.sh [skill...]` from inside that repository. The skills given are the review skills the hook runs, such as `review architecture-review`. Without any, an earlier copy's list is kept, and a first install runs `review` alone. When the user named no skills and the repository has an `architecture.toml`, ask whether `architecture-review` should run too. The script copies the hook to the path git resolves for `hooks/pre-push` (this honors `core.hooksPath`) and prints that path with the skill list. The copy records the skills folder it was installed from, so the background review can read the skills there. Running it again replaces an earlier copy, which is how the hook is updated, also after the skills folder moved.

When it exits with status 3, the repository already has a different `pre-push` hook. Show the user that hook's path and ask how to combine the two, for example by calling the review hook from the existing one. Leave the existing hook unchanged until the user decides.

## 2. Report

Tell the user the installed path and the review skills it runs, and that reviews start only while a Claude Code session is open in the repository or in a parent repository that contains it. A review shows up in `claude agents` only while it runs. An `architecture-review` run needs `cargo-modules` and `python3`, and extracts both revisions of the push, so it can take minutes. Its findings arrive in the open session as a message, which the session handles with the `handle-reviews` skill.
