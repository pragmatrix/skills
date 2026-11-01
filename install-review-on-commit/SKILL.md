---
name: install-review-on-commit
description: Install a post-commit hook that reviews each commit in a read-only background Claude Code run and messages the findings to the Claude Code sessions open in the repository.
disable-model-invocation: true
---

# Install Review on Commit

`post-commit` (next to this file) is the hook. After each commit it looks for interactive Claude Code sessions whose working directory lies inside the repository's worktree. When there is at least one, it starts a headless `claude -p` run named `review-<sha>` that reviews the commit with the `review` skill and then ends. The run sends those sessions a start notice and then its findings, and its final answer goes to `.git/review-on-commit/<sha>.log`. The hook's comments explain the rest: how the run is kept read-only, and which commits are skipped. The hook needs `claude` and `jq` on `PATH` and stays silent when either is missing.

## 1. Install

Run `<skill-dir>/install.sh` from inside the repository. It copies the hook to the path git resolves for `hooks/post-commit` (this honors `core.hooksPath`) and prints that path. Running it again replaces an earlier copy, which is how the hook is updated.

When it exits with status 3, the repository already has a different `post-commit` hook. Show the user that hook's path and ask how to combine the two, for example by calling the review hook from the existing one. Leave the existing hook unchanged until the user decides.

## 2. Report

Tell the user the installed path, and that reviews start only while a Claude Code session is open in the repository. A review shows up in `claude agents` only while it runs, and its findings arrive in the open session as a message.
