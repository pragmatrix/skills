---
name: update-pr
description: 'Post a comment on the GitHub or GitLab PR for the current branch with a concise summary of what changed in the current session (not the whole branch), plus what is still open. Never @mentions or addresses other participants. Use when the user wants to post an update on the PR about the work done in this session, e.g. invoking /update-pr or "update the PR with what we did".'
argument-hint: 'Optional: extra notes to include in the comment'
user-invocable: true
---

# Update PR

Post a comment on the PR for the current branch reflecting **what we did in this session** — not the whole branch. It does **not** commit, rebase, or review code, and it never edits the PR description.

## When to Use

Use when the request includes anything like:
- update the PR with what we did this session
- post an update on the PR
- `/update-pr`

## Prerequisites

- `gh` (GitHub) or `glab` (GitLab) CLI is installed and authenticated.
- There's a remote for the repo.
- The current branch has an open PR.

## Procedure

1. **Check the basics.**
   - Pick the CLI: `gh` for GitHub, `glab` for GitLab. Invoke it directly when inspecting or posting to the PR; report an availability or authentication failure only if that operation fails.
   - Get the current branch: `git branch --show-current`.
   - Confirm the branch has an open PR (`gh pr view <branch>` / `glab mr view <branch>`). If there's no PR, stop and tell the user — don't create one (use the `pr` skill for that).

2. **Recall what we did this session.**
   - Summarize from memory what changed in this session — the areas worked on and the outcome, at the level of detail the ticket's audience cares about (see step 4). Don't query the session store; use what you remember from the conversation.
   - Keep it short: a few bullet points.
   - Fold in any optional user notes.
   - If nothing worth noting is committed, stop and don't post — tell the user there's nothing to report.

3. **Check for uncommitted changes (gate).**
   - Run `git status --short`. If the working tree is dirty, ask the user whether it's OK to proceed before drafting anything. If the user declines, stop.
   - If they agree, exclude the uncommitted changes from the summary — the others won't see them, so don't describe work that isn't committed yet.

4. **Draft the comment.**
   - **Never trigger interactions with other participants.** No @mentions, and no questions addressed to reviewers or anyone else — state open items plainly. The only exception is something genuinely blocked that the user cannot resolve alone, and even then phrase it as a neutral remark, without an @mention and without asking anyone to act.
   - **Write for the ticket's audience, not for yourself.** Post only what the other participants can observe or care about: user-visible changes, the feedback a change answers, and whether it was verified. Leave out internal mechanics — refactors, constants, parameter plumbing, build/test noise, and per-commit recaps of what each diff did.
   - **List every commit from this session**, each with a short one-line description, however small or off-topic it looks. Never drop one as uninteresting — the list is what makes the work traceable, and reviewers use it to jump into the code. This is deliberately *not* governed by the audience rule above: the descriptions are audience-facing, the list is complete.
   - **Make the SHAs auto-link**: plain text, 7+ characters — no backticks, no code span, no manual link, no URL. GitHub and GitLab both link a bare SHA that exists in the repo, and neither links one inside a code span. Prefer 8+ characters (GitLab's default display length).
   - Write in the same language as the rest of the PR, even if that differs from the session's language.
   - Two sections, then the commit list as reference material:
     ```markdown
     **What's changed**

     <concise session summary>

     **What's open**

     <unfinished / deferred / in-progress items, stated plainly; or omit this section if none>

     Commits:

     - <sha> — <one-line description>
     - <sha> — <one-line description>

     ---

     _This comment was created entirely with AI assistance._
     ```
   - **If this skill was already used earlier in the session**, don't draft a full duplicate — check the PR comment thread for a prior update comment and draft only the *updates* since then, so the thread stays concise.

5. **Review the comment (gate).**
   - Show the user the full comment text and ask for approval before posting. Do not post until they approve; if they request changes, revise and re-show until approved. If the user declines to post, stop.

6. **Post the comment.**
   - Post the content as a new comment on the PR. Use `gh pr comment <pr> --body-file <file>` (or `glab mr note <mr> --message <file>`), building the body in a temp file.
   - Confirm the comment was posted and report the URL the command prints.

7. **Wrap up.**
   - Report the PR number/URL and a one-line recap of the comment you wrote, in the form:
     - PR: commented on title, number/URL
     - Summary: one-line recap of the comment written
