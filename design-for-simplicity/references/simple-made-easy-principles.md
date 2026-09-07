# Simple Made Easy Principles

Use this reference when auditing substantial software designs or explaining tradeoffs.

Source: Rich Hickey, "Simple Made Easy," Strange Loop 2011 transcript at https://github.com/matthiasn/talk-transcripts/blob/master/Hickey_Rich/SimpleMadeEasy.md

> This file is an original summary of the talk's ideas, not a reproduction of the transcript. The talk itself belongs to Rich Hickey; the transcript belongs to its transcription project. Do not paste transcript text here.

## Core Vocabulary

- Simple means unbraided: one role, task, concept, or dimension, without unnecessary interleaving.
- Easy means nearby: available, familiar, quick to reach, or within current capability.
- Complex means braided together.
- Complect means interleave concerns that could otherwise vary independently.
- Compose means place independent things together without entangling them.

## Audit Questions

Ask:

- Which decisions must change together today?
- Which parts require the reader to know hidden state, call order, location, or policy?
- What user-visible artifact quality is at stake: correctness, reliability, maintenance, change, debugging, or operational behavior?
- Is the proposal optimizing programmer convenience or replaceability instead of the artifact produced by long-term use?
- Does this abstraction specify what is needed, or does it prescribe how it must happen?
- Does the abstraction draw away from irrelevant physical details, or does it merely hide complexity behind a name?
- Is information represented as plain data or wrapped in behavior/state that blocks generic manipulation?
- Could the same behavior be implemented with values, functions, data, queues, rules, or declarative queries?
- Are modules merely partitioned, or are they genuinely independent behind abstractions?
- What complexity is inherent in the problem or environment, and what complexity is incidental?

## Slide-Derived Review Lenses

Use these lenses as quick prompts during reviews:

- Construct vs artifact: evaluate the software that runs and changes over time, not the code shape or typing experience.
- Limits: assume ordinary human reasoning is the bottleneck; every interleaving forces more things to be considered together.
- Change: ask what will be impacted and where the change must be made before trusting a refactor.
- Debugging: if type checks and tests already passed, ask what reasoning path remains when a field bug appears.
- Development speed: ease-first choices can be fastest early and slowest later; simplicity-first choices require upfront thinking.
- Making things easy: installation and learning can move tools closer, but mental-capability limits are addressed by simplifying the thing itself.
- Modularity: partitioning and layering do not imply simplicity; they only help when pieces are independent behind abstractions.
- Environmental complexity: resource contention and global operational policies may be inherent; per-component local policy can make them worse.
- Simplifying: identify individual threads, roles, and dimensions, follow them through the story/code, label them, then disentangle.

## Common Complections

- State complects value and time.
- Objects often complect state, identity, and value.
- Methods can complect function and state; classes can also act as weak namespaces.
- Inheritance complects types and implementation relationships.
- Switches and pattern matches can complect multiple "who does what" pairs in one closed place.
- Syntax can complect meaning and order.
- Loops often complect what is being done with how iteration proceeds.
- Actors can complect what work happens with who performs it.
- ORM complects domain data, object identity, persistence, and relational representation.
- Direct calls can complect timing and location.
- Scattered conditionals complect policy with execution structure.

## Simpler Replacements

- Values and immutable aggregates for information.
- Managed references only where state is essential, with extraction back to values.
- Functions and small named sets of functions for behavior.
- Namespaces for names.
- Data structures and declarative formats for information exchange.
- Polymorphism a la carte for open extension.
- Set-oriented operations and declarative queries for data manipulation.
- Queues for decoupling producers from consumers in time and location.
- Rule systems or explicit policy tables for business rules.
- Transactions and value snapshots for consistency.

## Ease Audit

When a team calls something simple, test whether they mean easy:

- At hand: already installed, approved, in the toolset, or quick to start.
- Familiar: close to the team's current language, framework, or habits.
- Near capability: within what people can reason about at once.

The first two can be improved by installation, training, examples, editor support, and practice. The third usually requires reducing entanglement.

## Abstraction Split

Use who, what, when, where, why, and how to find independent dimensions:

- What: operations and named specifications, expressed using values and other abstractions.
- Who: entities or data involved, injected rather than hardwired.
- How: implementation work; keep it as isolated as possible.
- When/where: timing and location; avoid direct component coupling when these should vary.
- Why: policies and rules; move them out of scattered imperative code when practical.

Keep the design posture "I don't know; I don't want to know" for details outside the current dimension. Cross-boundary curiosity is often an entanglement smell.

## Verification

A design is simpler only if at least one important future action becomes easier to reason about:

- A change can be localized to one decision dimension.
- A bug can be investigated without recreating broad hidden state.
- A policy can change without touching execution plumbing.
- A representation can change without rewriting business logic.
- A component can be replaced through a value/data/function boundary.

If none of these improve, the proposal may be merely reorganized, not simplified.
