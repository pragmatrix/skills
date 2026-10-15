---
name: grill-fast
description: Settle a plan's decisions fast through batched question rounds and a decision ledger.
disable-model-invocation: true
---

Drive a plan to settled decisions, fast. Sort every decision as a **one-way door** (costly to reverse, or shapes other decisions) or a **two-way door** (cheap to reverse). One-way doors go to the user; two-way doors you decide yourself and record in the ledger, where the user can overturn them.

## 0. Map

Before the first round, show the decision tree in a few lines: each expected decision, tagged one-way or two-way. The user prunes or retags it.

## Rounds

The **frontier** is every one-way door whose prerequisites are settled. Each round asks the _independent_ frontier decisions, those that unblock the most others first, as numbered questions. Wait for the answers, recompute the frontier, repeat.

Format a round like so:

```
📒 **Settled since last round**
- <decision>: <choice> (auto|fact): <short reason>

❓ **Q1** - **<question title>**: <the decision and its context>

- ➡️ **a) <recommended option>**: <why it wins _here_>
- 🔸 **b) <option>**: <its principal tradeoff>
- 🔸 **c)** ...

---

❓ **Q2** - ...
```

- The 📒 block lists every ledger entry settled without the user since the previous round, so each auto or fact decision is visible the round it is made. Omit the block only when there are none.
- Gather facts before writing options: look them up yourself or via a background sub-agent; ask the user only for decisions. Only questions downstream of a running lookup wait for it.
- A decision with one clearly dominant option is a fact: record it, do not ask.
- Before the round, state in a line any critical risk or dependency.
- Options are as many genuine alternatives as the decision has (two or more), with short, distinguishable labels, lettered so the user can answer tersely (`Q1 b`). Write them as list items: renderers strip leading spaces, so plain indented lines collapse into the question. The recommended one is always `a)`, marked ➡️; the others are marked 🔸.
- When the remaining frontier holds only clear recommendations, ask once: accept the remaining ➡️ options?

## Decision ledger

One line per settled decision: choice, a short reason, and how it was settled (user, auto, fact). The ledger and conversation are the source of truth: ask only what neither settles. When an answer contradicts an entry, flag the conflict instead of overwriting it.

## Done

Done when every one-way door is settled by the user and every two-way door is in the ledger. Present the full ledger and act only after the user confirms it.
