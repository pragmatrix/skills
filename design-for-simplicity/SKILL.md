---
name: design-for-simplicity
description: Apply Rich Hickey's Simple Made Easy principles to software architecture, API design, refactoring plans, code review, data modeling, workflow design, and technology selection. Use when asked to simplify a design, reduce complexity, evaluate tradeoffs, separate concerns, identify complecting, distinguish simple from easy, or critique objects/state/inheritance/ORM/conditionals/loops/actors/direct calls in favor of values, data, functions, queues, declarative rules, and small abstractions.
---

# Design For Simplicity

## Operating Mode

Treat simplicity as an objective property: absence of unnecessary interleaving. Treat ease as relative: familiarity, availability, or fit to current capability. Prefer durable artifact simplicity over authoring convenience.

Reason before proposing changes, flag uncertainty, push back on false equivalences, and verify that recommendations reduce entanglement rather than merely rearranging code.

## Workflow

1. State the relevant goal in artifact terms: reliability, changeability, debugging, extensibility, operations, or long-term comprehension.
2. Identify the roles, decisions, and dimensions currently braided together. Name the complected pairs explicitly.
3. Separate simple from easy:
   - Simple: one role, one concern, independent decisions, values over changing places.
   - Easy: at hand, familiar, or near current capability.
4. Evaluate the construct by the long-lived artifact it yields, not by the authoring experience.
5. Audit the design with the questions in `references/simple-made-easy-principles.md` when the task involves architecture, refactoring, or a substantial design choice.
6. Propose the smallest changes that disentangle decisions while preserving behavior.
7. Explain tradeoffs honestly. If a simpler design is less familiar, say so. If the problem has inherent or environmental complexity, do not pretend it can be removed.
8. Verify the proposal by checking whether future change/debugging can be localized without reconstructing unrelated state or policy.

## Simplicity Heuristics

Prefer:

- Values over mutable objects when representing information.
- Functions over methods when behavior does not require identity or mutable state.
- Small abstractions that specify what, not how.
- Data maps, sets, sequences, and declarative formats over custom class wrappers for plain information.
- Explicit namespaces over classes used as poor namespaces.
- Polymorphism a la carte over inheritance, closed switches, and centralized pattern matching.
- Queues or event streams over direct component calls when timing and location should remain independent.
- Declarative data manipulation and rule systems over scattered control flow.
- Transactions and immutable snapshots when consistency matters.

Avoid claiming that:

- More files, modules, interfaces, or services automatically mean more complexity. Counting is not entanglement.
- Tests, type systems, refactoring tools, or code organization create simplicity by themselves. They are secondary guardrails.
- A familiar tool is simple because the team already knows it.
- A hidden mutable implementation is harmless if the public behavior still depends on time, identity, or prior calls.
- An abstraction is good because it hides implementation. Good abstractions draw away from irrelevant physical details and preserve independent decisions.

## Review Output Shape

For reviews, lead with findings ordered by the degree of complecting:

```text
Finding: <decision or concern is braided with another>
Why it matters: <change/debug/reliability cost>
Simpler direction: <values/functions/data/queue/rule/abstraction/etc.>
Tradeoff: <what becomes less easy, more explicit, or still uncertain>
```

For design proposals, use:

```text
Current braid: <what is interleaved>
Artifact cost: <how this affects correctness, change, debugging, or operations>
Separate into: <independent pieces>
Boundary: <data contract, function set, queue, protocol, rule table, etc.>
Validation: <how to tell the design stayed simpler>
```

## Source Basis

This skill distills Rich Hickey's Strange Loop 2011 talk transcript, "Simple Made Easy." Use the reference file for the detailed checklist and vocabulary.
