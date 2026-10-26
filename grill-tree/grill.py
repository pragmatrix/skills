#!/usr/bin/env python3
"""Decision tree and ledger for a grill-tree session, kept in one JSON state file.

The state file is the single source of truth: the frontier, its order, each round's
text, and the ledger are all computed from it, so the same state renders the same round.

  grill.py <state> init <topic>
  grill.py <state> tree                 replace the whole tree from stdin (JSON list of decisions)
  grill.py <state> put                  add or change decisions from stdin (JSON list)
  grill.py <state> map                  print the tree with tags and status
  grill.py <state> settle <id> <user|auto|fact> <choice> <reason> [--override]
  grill.py <state> reopen <id>          reopen a decision and every settled decision downstream
  grill.py <state> round [--risk TEXT]  render the next round
  grill.py <state> answer <Qn> <letter|text> [<Qn> <letter|text>]...
  grill.py <state> answer all <letter>  the same letter for every open question of the last round
  grill.py <state> ledger               print every decision, settled or open
  grill.py <state> done                 exit 0 when every decision is settled

A decision in stdin JSON: {"id", "title", "door": "one-way"|"two-way", "requires": [ids],
"context", "options": [{"label", "why"}]}. options[0] is the recommendation.
"""
import json
import os
import re
import sys
import tempfile

DOORS = ("one-way", "two-way")
SETTLERS = ("user", "auto", "fact")
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
FIELDS = ("title", "door", "requires", "context", "options")


class GrillError(Exception):
    pass


# --- state file ------------------------------------------------------------------------------


def load(path):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        raise GrillError(f"no state at {path}; run `init` first")


def save(path, state):
    state["revision"] += 1
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=directory, suffix=".tmp")
    with os.fdopen(fd, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, path)


def read_decisions():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        raise GrillError(f"stdin is not JSON: {e}")
    if not isinstance(data, list):
        raise GrillError("stdin must be a JSON list of decisions")
    return data


# --- graph -----------------------------------------------------------------------------------


def validate(decisions):
    for did, d in decisions.items():
        if not ID_RE.match(did):
            raise GrillError(f"{did}: id must be kebab-case")
        if not d.get("title"):
            raise GrillError(f"{did}: missing title")
        if d.get("door") not in DOORS:
            raise GrillError(f"{did}: door must be one-way or two-way")
        for r in d["requires"]:
            if r not in decisions:
                raise GrillError(f"{did}: requires unknown decision {r}")
        for o in d["options"]:
            if not o.get("label"):
                raise GrillError(f"{did}: every option needs a label")
    depths(decisions)


def depths(decisions):
    """Longest prerequisite chain per decision; raises on a cycle."""
    result, visiting = {}, set()

    def visit(did):
        if did in result:
            return result[did]
        if did in visiting:
            raise GrillError(f"prerequisite cycle through {did}")
        visiting.add(did)
        result[did] = 1 + max((visit(r) for r in decisions[did]["requires"]), default=-1)
        visiting.discard(did)
        return result[did]

    for did in decisions:
        visit(did)
    return result


def ordered(decisions):
    """Topological order: by depth, then by position in the tree."""
    depth = depths(decisions)
    position = {did: i for i, did in enumerate(decisions)}
    return sorted(decisions, key=lambda did: (depth[did], position[did]))


def graph(decisions):
    """Topological order and the reverse prerequisite map, derived once per command."""
    dependents = {did: [] for did in decisions}
    for did, d in decisions.items():
        for r in d["requires"]:
            dependents[r].append(did)
    return ordered(decisions), dependents


def downstream(dependents, did):
    """Every decision that transitively requires `did`."""
    found, stack = set(), [did]
    while stack:
        for other in dependents[stack.pop()]:
            if other not in found:
                found.add(other)
                stack.append(other)
    return found


def frontier(decisions):
    """Open decisions whose prerequisites are all settled, most-unblocking first."""
    order, dependents = graph(decisions)
    ready = [
        did
        for did in order
        if not is_settled(decisions[did])
        and all(is_settled(decisions[r]) for r in decisions[did]["requires"])
    ]
    unblocks = {
        did: sum(1 for o in downstream(dependents, did) if not is_settled(decisions[o]))
        for did in ready
    }
    return sorted(ready, key=lambda did: -unblocks[did])


# --- decisions -------------------------------------------------------------------------------


def is_settled(d):
    return d.get("settled") is not None


def label(d):
    """A decision's number, fixed at creation, and its title."""
    return f"#{d['n']} {d['title']}"


def normalize(raw, existing=None):
    if not isinstance(raw, dict) or not raw.get("id"):
        raise GrillError(f"every decision needs an id: {raw!r}")
    d = dict(existing or {"requires": [], "context": "", "options": [], "settled": None})
    for field in FIELDS:
        if field in raw:
            d[field] = raw[field]
    return raw["id"], d


def note(state, line):
    state["notes"].append(line)


def reopen(state, did, cause, tree_graph, include_self=True):
    """Reopen `did` and every settled decision downstream of it; returns the reopened ids."""
    decisions = state["decisions"]
    order, dependents = tree_graph
    below = downstream(dependents, did)
    reopened = []
    for other in ([did] if include_self else []) + [k for k in order if k in below]:
        if is_settled(decisions[other]):
            decisions[other]["settled"] = None
            reopened.append(other)
            note(state, f"- {label(decisions[other])}: reopened: {cause}")
    return reopened


def settle(state, did, by, choice, reason, override=False):
    decisions = state["decisions"]
    if did not in decisions:
        raise GrillError(f"unknown decision {did}")
    if by not in SETTLERS:
        raise GrillError(f"settled by must be one of {', '.join(SETTLERS)}")
    d = decisions[did]
    if by == "auto" and d["door"] == "one-way":
        raise GrillError(f"{did} is a one-way door: settle it by user or fact, not auto")
    blocked = [r for r in d["requires"] if not is_settled(decisions[r])]
    if blocked:
        raise GrillError(f"{did} waits on open prerequisites: {', '.join(blocked)}")
    current = d["settled"]
    if current is not None:
        if current["choice"] == choice:
            return []
        # Overturning an auto or fact entry is the user's right; only their own answers conflict.
        if current["by"] == "user" and not override:
            raise GrillError(
                f"conflict on {did}: ledger has '{current['choice']}' (user), "
                f"new '{choice}' ({by}); flag it to the user, then pass --override to replace it"
            )
    reopened = []
    if current is not None:
        reopened = reopen(
            state, did, f"{label(d)} changed to {choice}", graph(decisions), include_self=False
        )
    d["settled"] = {"choice": choice, "reason": reason, "by": by}
    if by != "user":
        note(state, f"- {label(d)}: {choice} ({by}): {reason}")
    return reopened


def merge(state, raws, replace):
    """Apply decisions from stdin; a settled two-way door retagged one-way reopens unless the user settled it."""
    old = state["decisions"]
    new = {} if replace else dict(old)
    next_number = state["next_number"]
    for raw in raws:
        did, d = normalize(raw, old.get(raw.get("id")) if isinstance(raw, dict) else None)
        if "n" not in d:
            d["n"] = next_number
            next_number += 1
        new[did] = d
    validate(new)
    state["next_number"] = next_number
    dropped = [did for did in old if did not in new]
    for did in dropped:
        d = old[did]
        if is_settled(d):
            state["dropped"].append(
                {"id": did, "n": d["n"], "title": d["title"], "door": d["door"], **d["settled"]}
            )
            note(state, f"- {label(d)}: dropped by a rebuild (was {d['settled']['choice']})")
    state["decisions"] = new
    lines = [f"dropped: {did}" for did in dropped]
    tree_graph = graph(new)
    for did, d in new.items():
        s = d["settled"]
        if s and s["by"] == "auto" and d["door"] == "one-way":
            reopen(state, did, "retagged one-way", tree_graph)
            lines.append(f"reopened: {did} (retagged one-way)")
        elif s and any(not is_settled(new[r]) for r in d["requires"]):
            reopen(state, did, "a prerequisite is open", tree_graph)
            lines.append(f"reopened: {did} (a prerequisite is open)")
    return lines


# --- rendering -------------------------------------------------------------------------------


DOOR_ICONS = {"one-way": "🚪", "two-way": "🔁"}
SETTLER_ICONS = {"user": "👤", "auto": "🤖", "fact": "📌", None: "⏳"}
LEDGER_HEADER = "| # | | Decision | Choice | Reason |\n|---|---|---|---|---|"


def cell(text):
    return text.replace("|", "\\|").replace("\n", " ")


def ledger_row(n, title, door, settled):
    s = settled or {}
    icons = DOOR_ICONS[door] + SETTLER_ICONS[s.get("by")]
    return (
        f"| {n} | {icons} | {cell(title)} | {cell(s.get('choice', ''))} "
        f"| {cell(s.get('reason', ''))} |"
    )


def render_round(state, risk):
    decisions = state["decisions"]
    ready = frontier(decisions)
    pending = [did for did in ready if decisions[did]["door"] == "two-way"]
    if pending:
        raise GrillError(
            "settle these two-way doors first (auto, fact, or user): " + ", ".join(pending)
        )
    unready = [did for did in ready if len(decisions[did]["options"]) < 2]
    if unready:
        raise GrillError(
            "these one-way doors need two or more options (or settle as fact): "
            + ", ".join(unready)
        )
    parts = []
    if state["notes"]:
        parts.append("📒 **Ledger changes since last round**\n" + "\n".join(state["notes"]))
    if risk:
        parts.append(f"⚠️ {risk}")
    questions = []
    for n, did in enumerate(ready, 1):
        d = decisions[did]
        context = f": {d['context']}" if d["context"] else ""
        lines = [f"❓ **Q{n}** - **{label(d)}**{context}", ""]
        for i, o in enumerate(d["options"]):
            mark = "➡️" if i == 0 else "🔸"
            why = f": {o['why']}" if o.get("why") else ""
            lines.append(f"- {mark} **{chr(ord('a') + i)}) {o['label']}**{why}")
        questions.append("\n".join(lines))
    if questions:
        parts.append("\n\n---\n\n".join(questions))
    elif any(not is_settled(d) for d in decisions.values()):
        raise GrillError("open decisions remain but none is ready; check `map`")
    else:
        parts.append("✅ Every decision is settled: present the `ledger` for confirmation.")
    return "\n\n".join(parts), ready


# --- commands --------------------------------------------------------------------------------


def cmd_init(path, args):
    if len(args) != 1:
        raise GrillError("usage: init <topic>")
    if os.path.exists(path):
        raise GrillError(f"{path} exists; pick another topic or continue it")
    save(path, {
        "topic": args[0], "revision": 0, "decisions": {}, "dropped": [],
        "next_number": 1, "notes": [], "shown_notes": 0, "asked": [], "rendered": None,
    })
    print(f"created {path}")


def cmd_tree(path, args, replace=True):
    state = load(path)
    lines = merge(state, read_decisions(), replace)
    save(path, state)
    print("\n".join(lines) or "ok")


def cmd_map(path, args):
    decisions = load(path)["decisions"]
    print("| # | | Decision | Choice | Requires |\n|---|---|---|---|---|")
    for d in sorted(decisions.values(), key=lambda d: d["n"]):
        s = d["settled"] or {}
        icons = DOOR_ICONS[d["door"]] + SETTLER_ICONS[s.get("by")]
        requires = ", ".join(f"#{decisions[r]['n']}" for r in d["requires"])
        print(f"| {d['n']} | {icons} | {cell(d['title'])} | {cell(s.get('choice', ''))} | {requires} |")


def cmd_settle(path, args):
    override = "--override" in args
    args = [a for a in args if a != "--override"]
    if len(args) != 4:
        raise GrillError("usage: settle <id> <user|auto|fact> <choice> <reason> [--override]")
    state = load(path)
    reopened = settle(state, *args, override=override)
    save(path, state)
    print("ok" + (f"; reopened {', '.join(reopened)}" if reopened else ""))


def cmd_reopen(path, args):
    if len(args) != 1:
        raise GrillError("usage: reopen <id>")
    state = load(path)
    if args[0] not in state["decisions"]:
        raise GrillError(f"unknown decision {args[0]}")
    reopened = reopen(state, args[0], "reopened on request", graph(state["decisions"]))
    save(path, state)
    print(f"reopened {', '.join(reopened)}" if reopened else "already open")


def cmd_round(path, args):
    risk = None
    if args[:1] == ["--risk"] and len(args) == 2:
        risk = args[1]
    elif args:
        raise GrillError("usage: round [--risk TEXT]")
    state = load(path)
    rendered = state["rendered"]
    if rendered and rendered["revision"] == state["revision"] and rendered["risk"] == risk:
        print(rendered["text"])
        return
    text, asked = render_round(state, risk)
    # The notes stay until the user answers, so a re-render after a fix still shows them.
    state["shown_notes"] = len(state["notes"])
    state["asked"] = asked
    # `save` bumps the revision; a rerun with nothing changed in between prints this text again.
    state["rendered"] = {"revision": state["revision"] + 1, "risk": risk, "text": text}
    save(path, state)
    print(text)


def cmd_answer(path, args):
    if not args or len(args) % 2:
        raise GrillError("usage: answer <Qn> <letter|text> [<Qn> <letter|text>]... | all <letter>")
    state = load(path)
    asked, decisions = state["asked"], state["decisions"]
    if args[0] == "all":
        args = [
            part
            for n, did in enumerate(asked, 1)
            if did in decisions and not is_settled(decisions[did])
            for part in (f"Q{n}", args[1])
        ]
    reopened = []
    for q, answer in zip(args[::2], args[1::2]):
        m = re.fullmatch(r"[Qq](\d+)", q)
        if not m or not 1 <= int(m.group(1)) <= len(asked):
            raise GrillError(f"{q}: the last round asked Q1..Q{len(asked)}")
        did = asked[int(m.group(1)) - 1]
        if did not in decisions:
            raise GrillError(f"{q}: {did} was dropped by a rebuild; run `round` again")
        options = decisions[did]["options"]
        if re.fullmatch(r"[a-z]", answer):
            index = ord(answer) - ord("a")
            if index >= len(options):
                raise GrillError(f"{q} has options a..{chr(ord('a') + len(options) - 1)}")
            why = options[index].get("why", "")
            # Only the recommendation's why is a motive; the others describe their tradeoff.
            reason = why if index == 0 or not why else f"accepts: {why}"
            choice = options[index]["label"]
        else:
            choice, reason = answer, "the user's own answer"
        reopened += settle(state, did, "user", choice, reason)
    state["notes"] = state["notes"][state["shown_notes"]:]
    state["shown_notes"] = 0
    save(path, state)
    print("ok" + (f"; reopened {', '.join(reopened)}" if reopened else ""))


def cmd_ledger(path, args):
    state = load(path)
    decisions = state["decisions"]
    print(f"# {state['topic']}\n\n{LEDGER_HEADER}")
    for d in sorted(decisions.values(), key=lambda d: d["n"]):
        print(ledger_row(d["n"], d["title"], d["door"], d["settled"]))
    if state["dropped"]:
        print(f"\nDropped by a rebuild:\n\n{LEDGER_HEADER}")
        for d in state["dropped"]:
            print(ledger_row(d["n"], d["title"], d["door"], d))


def cmd_done(path, args):
    decisions = load(path)["decisions"]
    open_ids = [did for did in ordered(decisions) if not is_settled(decisions[did])]
    if open_ids:
        print("open: " + ", ".join(open_ids))
        sys.exit(1)
    print("done")


COMMANDS = {
    "init": cmd_init,
    "tree": cmd_tree,
    "put": lambda path, args: cmd_tree(path, args, replace=False),
    "map": cmd_map,
    "settle": cmd_settle,
    "reopen": cmd_reopen,
    "round": cmd_round,
    "answer": cmd_answer,
    "ledger": cmd_ledger,
    "done": cmd_done,
}


def main(argv):
    if len(argv) < 2 or argv[1] not in COMMANDS:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    try:
        COMMANDS[argv[1]](argv[0], argv[2:])
    except GrillError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
