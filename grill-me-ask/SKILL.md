---
name: grill-me-ask
description: Settle a plan's decisions fast through batched AskUserQuestion rounds and a decision ledger.
disable-model-invocation: true
---

Drive a plan to settled decisions, fast. Sort every decision as a **one-way door** (costly to reverse, or shapes other decisions) or a **two-way door** (cheap to reverse). One-way doors go to the user; two-way doors you decide yourself and record in the ledger, where the user can overturn them.

## 0. Map

Before the first round, show the decision tree in a few lines: each expected decision, tagged one-way or two-way. The user prunes or retags it.

## Rounds

The **frontier** is every one-way door whose prerequisites are settled. Each round is one AskUserQuestion call with up to 4 _independent_ frontier decisions, those that unblock the most others first. Wait for the answers, recompute the frontier, repeat.

- Gather facts before writing options: look them up yourself or via a background sub-agent; ask the user only for decisions. Only questions downstream of a running lookup wait for it.
- A decision with one clearly dominant option is a fact: record it, do not ask.
- Before the call, state in a line any critical risk or dependency.
- Options are genuine alternatives with short, distinguishable labels. The recommended one comes first, prefixed `[REC]`, its description saying why it wins _here_; every other description states its principal tradeoff.
- When the remaining frontier holds only clear recommendations, ask once: accept the remaining `[REC]`s?

## Decision ledger

One line per settled decision: choice, a short reason, and how it was settled (user, auto, fact). The ledger and conversation are the source of truth: ask only what neither settles. When an answer contradicts an entry, flag the conflict instead of overwriting it.

## Done

Done when every one-way door is settled by the user and every two-way door is in the ledger. Present the full ledger and act only after the user confirms it.
