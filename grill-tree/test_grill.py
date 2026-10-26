"""Pins the rules grill-tree relies on. Run: python3 -m unittest test_grill (in this folder)."""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

import grill


def two(label="x"):
    return [{"label": label}, {"label": "other"}]


class GrillTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.state = os.path.join(self.dir.name, "t.json")
        self.ok("init", "topic")

    def tearDown(self):
        self.dir.cleanup()

    def run_tool(self, *args, stdin=None):
        out, err = io.StringIO(), io.StringIO()
        saved = sys.stdin
        sys.stdin = io.StringIO(json.dumps(stdin) if stdin is not None else "")
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = grill.main([self.state, *args])
        finally:
            sys.stdin = saved
        return code, out.getvalue() + err.getvalue()

    def ok(self, *args, stdin=None):
        code, output = self.run_tool(*args, stdin=stdin)
        self.assertEqual(code, 0, output)
        return output

    def fails(self, *args, stdin=None):
        code, output = self.run_tool(*args, stdin=stdin)
        self.assertEqual(code, 1, output)
        return output

    def test_frontier_puts_the_most_unblocking_decision_first(self):
        self.ok("tree", stdin=[
            {"id": "leaf", "title": "Leaf", "door": "one-way", "options": two()},
            {"id": "root", "title": "Root", "door": "one-way", "options": two()},
            {"id": "child", "title": "Child", "door": "one-way", "requires": ["root"]},
        ])
        text = self.ok("round")
        self.assertLess(text.index("**Q1** - **#2 Root**"), text.index("**Q2** - **#1 Leaf**"))

    def test_round_is_refused_while_a_ready_two_way_door_is_open(self):
        self.ok("tree", stdin=[{"id": "a", "title": "A", "door": "two-way"}])
        self.assertIn("settle these two-way doors first", self.fails("round"))

    def test_one_way_door_cannot_be_settled_auto(self):
        self.ok("tree", stdin=[{"id": "a", "title": "A", "door": "one-way"}])
        self.assertIn("one-way door", self.fails("settle", "a", "auto", "x", "r"))

    def test_rerun_without_changes_renders_the_same_round(self):
        self.ok("tree", stdin=[{"id": "a", "title": "A", "door": "one-way", "options": two()}])
        self.assertEqual(self.ok("round", "--risk", "r"), self.ok("round", "--risk", "r"))

    def test_conflict_needs_override_and_override_reopens_downstream(self):
        self.ok("tree", stdin=[
            {"id": "a", "title": "A", "door": "one-way"},
            {"id": "b", "title": "B", "door": "two-way", "requires": ["a"]},
        ])
        self.ok("settle", "a", "user", "x", "r")
        self.ok("settle", "b", "auto", "y", "r")
        self.assertIn("conflict on a", self.fails("settle", "a", "user", "z", "r"))
        self.assertIn("reopened b", self.ok("settle", "a", "user", "z", "r", "--override"))

    def test_rebuild_keeps_settlements_and_reopens_a_retag_to_one_way(self):
        self.ok("tree", stdin=[
            {"id": "a", "title": "A", "door": "two-way"},
            {"id": "b", "title": "B", "door": "one-way"},
        ])
        self.ok("settle", "a", "auto", "x", "r")
        self.ok("settle", "b", "user", "y", "r")
        self.ok("tree", stdin=[
            {"id": "a", "title": "A", "door": "one-way"},
            {"id": "b", "title": "B", "door": "one-way"},
        ])
        self.assertIn("| 1 | 🚪⏳ | A |  |", self.ok("map"))
        self.assertIn("| 2 | 🚪👤 | B | y |", self.ok("map"))

    def test_dropped_settled_decision_shows_in_the_next_round(self):
        self.ok("tree", stdin=[
            {"id": "a", "title": "A", "door": "one-way"},
            {"id": "b", "title": "B", "door": "one-way", "options": two()},
        ])
        self.ok("settle", "a", "user", "x", "r")
        self.ok("tree", stdin=[{"id": "b", "title": "B", "door": "one-way"}])
        self.assertIn("- #1 A: dropped by a rebuild (was x)", self.ok("round"))

    def test_user_overturns_an_auto_entry_without_a_conflict(self):
        self.ok("tree", stdin=[{"id": "a", "title": "A", "door": "two-way"}])
        self.ok("settle", "a", "auto", "x", "r")
        self.ok("settle", "a", "user", "y", "r")
        self.assertIn("| 1 | 🔁👤 | A | y |", self.ok("map"))

    def test_notes_survive_a_rerender_until_the_user_answers(self):
        self.ok("tree", stdin=[
            {"id": "a", "title": "A", "door": "two-way"},
            {"id": "b", "title": "B", "door": "one-way", "options": two()},
        ])
        self.ok("settle", "a", "auto", "x", "r")
        self.ok("round")
        self.ok("put", stdin=[{"id": "b", "context": "fixed"}])
        self.assertIn("#1 A: x (auto)", self.ok("round"))
        self.ok("answer", "Q1", "a")
        self.ok("put", stdin=[{"id": "c", "title": "C", "door": "one-way", "options": two()}])
        self.assertNotIn("📒", self.ok("round"))

    def test_choosing_an_alternative_records_its_tradeoff_as_accepted(self):
        self.ok("tree", stdin=[{"id": "a", "title": "A", "door": "one-way",
                                "options": [{"label": "x", "why": "best"}, {"label": "y", "why": "slow"}]}])
        self.ok("round")
        self.ok("answer", "Q1", "b")
        self.assertIn("| y | accepts: slow |", self.ok("ledger"))

    def test_numbers_are_fixed_at_creation_across_rebuilds(self):
        self.ok("tree", stdin=[
            {"id": "a", "title": "A", "door": "one-way"},
            {"id": "b", "title": "B", "door": "one-way"},
        ])
        self.ok("tree", stdin=[
            {"id": "c", "title": "C", "door": "one-way"},
            {"id": "b", "title": "B", "door": "one-way"},
        ])
        ledger = self.ok("ledger")
        self.assertIn("| 2 | 🚪⏳ | B |", ledger)
        self.assertIn("| 3 | 🚪⏳ | C |", ledger)

    def test_answer_on_a_dropped_decision_is_an_error(self):
        self.ok("tree", stdin=[{"id": "a", "title": "A", "door": "one-way", "options": two()}])
        self.ok("round")
        self.ok("tree", stdin=[{"id": "b", "title": "B", "door": "one-way"}])
        self.assertIn("dropped by a rebuild", self.fails("answer", "Q1", "a"))

    def test_answer_all_settles_only_the_open_questions(self):
        self.ok("tree", stdin=[
            {"id": "a", "title": "A", "door": "one-way", "options": two("first")},
            {"id": "b", "title": "B", "door": "one-way", "options": two("first")},
        ])
        self.ok("round")
        self.ok("answer", "Q1", "b")
        self.ok("answer", "all", "a")
        ledger = self.ok("ledger")
        self.assertIn("| A | other |", ledger)
        self.assertIn("| B | first |", ledger)

    def test_cycle_is_rejected_and_state_kept(self):
        self.ok("tree", stdin=[{"id": "a", "title": "A", "door": "one-way"}])
        self.fails("tree", stdin=[
            {"id": "a", "title": "A", "door": "one-way", "requires": ["b"]},
            {"id": "b", "title": "B", "door": "one-way", "requires": ["a"]},
        ])
        self.assertNotIn("| B |", self.ok("map"))


if __name__ == "__main__":
    unittest.main()
