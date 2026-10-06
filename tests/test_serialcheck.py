import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from serialcheck import core


def op(txn, kind, item):
    return {"txn": txn, "kind": kind, "item": item}


class SerialcheckTest(unittest.TestCase):
    def test_ww_conflict_detected(self):
        ops = [op(1, "w", "x"), op(2, "w", "x")]
        self.assertTrue(core.conflicts(ops, core.Counter()))

    def test_different_items_no_edge(self):
        ops = [op(1, "w", "x"), op(2, "w", "y")]
        self.assertEqual(core.conflicts(ops, core.Counter()), set())

    def test_two_cycle_detected(self):
        ops = [op(1, "w", "x"), op(2, "w", "x"), op(2, "w", "y"), op(1, "w", "y")]
        edges = core.conflicts(ops, core.Counter())
        self.assertIsNotNone(core.find_cycle(edges))

    def test_empty_schedule_serializable(self):
        text = core.report([], core.Counter())
        self.assertIn("serializable=true", text)

    def test_report_has_summary(self):
        ops = [op(1, "w", "x"), op(2, "w", "x")]
        text = core.report(ops, core.Counter())
        self.assertIn("conflicts=", text)

    def test_edges_are_pairs(self):
        ops = [op(1, "w", "x"), op(2, "w", "x")]
        for edge in core.conflicts(ops, core.Counter()):
            self.assertEqual(len(edge), 2)


if __name__ == "__main__":
    unittest.main()
