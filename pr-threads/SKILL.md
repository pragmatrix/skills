---
name: pr-threads
description: 'Review threads on a GitHub PR: list every thread with its resolution state, or resolve threads. Use when checking whether PR review comments are addressed, or resolving them.'
---

# PR Review Threads

`threads.sh` (next to this file) is the source for a PR's review threads. It reads GitHub's GraphQL `reviewThreads`, which include threads from unsubmitted reviews and each thread's resolution state.

- List: `<skill-dir>/threads.sh list <owner/repo> <pr>`. Each thread prints as `<id> OPEN|resolved [outdated] <path>:<line>`, followed by its comments.
- Resolve: `<skill-dir>/threads.sh resolve <thread-id>...`. It resolves without posting a reply.

## Checking whether threads are addressed

1. List the threads of every PR in scope. With submodules, that includes the submodule PRs.
2. For each `OPEN` thread, read the code at its `path:line` on the current branch and decide whether the comment is addressed. `outdated` only means the line changed; it is not evidence that the comment was addressed.
3. Resolve only the threads you verified as addressed. Report the open ones with their location and what is missing.
