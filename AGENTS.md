# Agent skills

This repository publishes skills that other people install. Each skill is written for everyone who works within its
scope, not for the person or project that prompted it.

## Write skills for everyone in their scope

- **Scope** is the deliberate restriction of a skill: a domain, a jurisdiction, a language, a platform, or a tool. The
  Rust skills, for example, are limited to Rust workspaces, and `install-review-on-push` is limited to Claude Code. A
  skill names its scope in its description or its first section.
- Within its scope a skill works for every user. It serves any repository, any project, any organisation, and any
  account, not the one it was first used on.
- Facts that vary from user to user come from the user's project at run time. The skill tells the agent where to find
  them, such as the project's `AGENTS.md`, a `README.md`, or a configuration file, and what to do when they are
  missing. Examples of such facts are the people involved, the names of the project and its parts, its paths, its
  hosts, or the tools it uses.
- A rule learned in one project is stated in general terms, as a mechanism that applies to the next case. The
  `writing-for-agents` skill describes how (section Pruning, "lesson").

## Keep personal and project information out

- A skill, its scripts, and its examples contain no personal or project information. That covers names of people and
  companies, addresses, customer and account numbers, host names, amounts, dates, and file or folder names taken from
  a real project.
- Examples use invented values that look realistic, such as "Jane Doe", "acme-api", or "example.com".
- Before a commit, every added or changed line is checked for such information. A finding is rewritten in general
  terms or replaced by an invented value.
