---
name: architecture-review
description: 'Review a change''s effect on a Rust workspace''s architecture: note every change to its code graph, external crates, and declared components, and judge the dependency structure. Use when reviewing commits or a push for dependency or layering changes, or when the review-on-push hook runs it.'
argument-hint: 'The commits to review, oldest first'
user-invocable: true
---

# Architecture review

You review what a change does to the workspace's architecture, as the [`architecture`](../architecture/SKILL.md) skill defines it: the derived code graph, and the components declared in `architecture.toml`. Read that skill's model section first. The goal of every judgment is a dependency graph that stays as simple as possible, with clearly separated components and modules. You report and do not edit.

## 1. Prepare

The change runs from the parent of its oldest commit to its newest commit. Find the parent with `git log -1 --format=%H <oldest>^`. When the oldest commit has no parent, the base is `-`.

Run `<skill-dir>/prepare <base> <newest>` by its absolute path, as the command itself, without `sh` or `cd` in front. It extracts both revisions in temporary worktrees, prints the change summary, and writes the diff view. Extraction runs `cargo-modules` on every crate, so it can take minutes.

When `prepare` fails, report its error as an unverified concern and judge only what the commits' diffs show.

Done when you have the change summary, or the failure is reported.

## 2. Note every change

Every line of the change summary becomes one item under **Graph changes**, in the summary's groups: modules, code edges with their reaches, external crate uses, crate dependencies, components, and check findings that are new or resolved. Keep each line's `+`, `−`, or `~`. A summary of "No architecture changes" is the whole section.

Done when every summary line is an item.

## 3. Judge

Judge the changes as a whole, so a problem that a later commit of the change fixes is no finding. Read the code behind an edge before judging it, and cite the `path:line` of the `use` or signature that creates it. Look for:

- **New check findings:** an unexplained or transitive dependency, an unmapped module, a cycle among components, or an unused crate dependency.
- **Deep reaches:** a reach that goes several levels into a sibling's subtree. It couples the source to that sibling's inner structure, and a shallower item would often serve.
- **Sibling cycles:** a new code edge whose reverse edge already exists under the same parent.
- **Spreading externals:** an external crate that a module of another component now uses as well, or that spreads across many modules.
- **Declarations that paper over code:** a component dependency or mapping added only to silence a finding, where changing the code would keep the graph simpler.
- **Stale document:** the code graph changed, but the change leaves `ARCHITECTURE.md` or `architecture.toml` untouched.

Every finding must require a change or raise a concern. When nothing qualifies, the verdict says "no findings".

Done when every graph change and every new check finding has been judged.

## Output

Number every item `<section>.<n>` so the user can refer to it.

1. **Verdict:** one line, blocking findings or none.
2. **Graph changes:** every summary line, grouped.
3. **Judgments:** severity-ordered (`high`, `medium`, `low`): what grows more complex or less separated, the `path:line` evidence, and the simpler alternative.
4. **Diff view:** the path of `view.md`, which renders in VS Code's Markdown preview.
