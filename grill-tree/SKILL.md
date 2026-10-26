---
name: grill-tree
description: Settle a plan's decisions through tool-rendered question rounds over a stored decision tree and ledger.
disable-model-invocation: true
---

Drive a plan to settled decisions, fast and deterministically. Sort every decision as a **one-way door** (costly to reverse, or shapes other decisions) or a **two-way door** (cheap to reverse). One-way doors go to the user; two-way doors you decide yourself, where the user can overturn them.

`grill.py` (next to this file) owns the decision tree and the ledger in one state file, `.grill/<topic>.json` in the working directory (kebab-case topic). The frontier, its order, every round's text, and the ledger come from that file: change the tree only through the tool, and show the user its output verbatim. `<skill-dir>/grill.py <state>` without a command prints the usage.

## 1. Map

If `.grill/` holds a state file for this topic, resume: run `map` and `round` on it. Otherwise `init` it, gather the facts the plan rests on, and write the whole tree with `tree`, a JSON list on stdin:

```json
[{"id": "store", "title": "Backing store", "door": "one-way", "requires": [],
  "context": "the decision and its context",
  "options": [{"label": "Redis", "why": "why it wins here"}, {"label": "In-process LRU", "why": "its principal tradeoff"}]}]
```

`requires` lists the decisions that must be settled before this one can be decided. Show the `map` output above round 1; the user prunes or retags it in their answers.

## 2. Rounds

Before each `round`, prepare its frontier (every open decision whose prerequisites are settled):

- Gather facts before writing options: look them up yourself or via a background sub-agent; ask the user only for decisions. Only decisions downstream of a running lookup wait for it.
- Settle each two-way door on the frontier with `settle <id> auto <choice> <reason>`.
- Settle a decision with one clearly dominant option as `fact`, without asking.
- Give each remaining one-way door its options with `put`: as many genuine alternatives as the decision has (two or more), short and distinguishable. The first is the recommendation, its `why` saying why it wins _here_; each other `why` states its principal tradeoff.

Then run `round`, adding `--risk <text>` for a critical risk or dependency, and send its output. The tool refuses a round while the frontier holds an unsettled two-way door or a one-way door with fewer than two options.

Record the user's answers with `answer Q1 b Q2 <own words>`. An unanswered question stays on the frontier for the next round. When the remaining frontier holds only clear recommendations, ask once whether to accept them all; on a yes, `answer all a`.

## 3. Reshape

Keep the tree true to the conversation:

- A new decision, a retag, or a changed prerequisite: `put` the changed decisions.
- A tree whose shape no longer fits: rebuild it with `tree`, the whole list again. Settled decisions keep their settlement by id, and omitted fields carry over. The tool reopens a decision retagged from an auto-settled two-way to a one-way door, and lists each dropped settled decision in the next round's 📒 block.
- The user overturns a 🤖 auto or 📌 fact entry: `settle <id> user <choice> <reason>`.
- An answer that contradicts one of the user's own earlier answers: the tool flags the conflict. Put it to the user; when they confirm the change, `settle <id> user <choice> <reason> --override`.

Changing a settled decision reopens every settled decision downstream, which then returns through the rounds.

## 4. Done

Done when `done` exits 0. Present the `ledger` output and act only after the user confirms it.
