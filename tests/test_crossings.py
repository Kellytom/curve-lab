"""Every stored crossing count is the one the router measures today.

The fault, as the operator saw it: the page said `crosses itself 5` for
`lace-1of10-1of5-3` and the record said 4. The record was the stale one: the
galleries' `self` numbers were written before the parameter-pair dedupe replaced
the distance dedupe (DESIGN-int), and nothing recomputed them afterwards. On
2026-11-16 the audit found 100 stale numbers across seven files.

What the number means. A **crossing pair** is two parameters where the stroke
passes through the same place. Three passes through one point are three pairs,
which is why this curve holds 5 pairs at 3 places. The number is scale-free; it
is not a count of distinct places, and it must not be called one.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import crossing_audit  # noqa: E402

CURVES = ROOT / "curves"


class TestCrossings(unittest.TestCase):
    def test_every_record_matches_the_router(self):
        """Run scripts/crossing_audit.py --write when this fails, then rebuild pages."""
        problems = crossing_audit.audit()
        self.assertEqual([], [(name, was, now) for name, was, now, _ in problems])

    def test_the_triple_point_counts_as_three_pairs(self):
        """5 pairs at 3 places: the operator's 5, and the record's old 4 was stale."""
        import json

        record = json.loads((CURVES / "lace-1of10-1of5-3" / "curve.json").read_text())
        self.assertEqual(5, record["crossings"])

    def test_the_number_is_scale_free(self):
        """Two copies of one curve at different sizes cross the same number of times."""
        import json

        record = json.loads((CURVES / "wide-knot-x20" / "curve.json").read_text())
        small = crossing_audit.pairs(record["speedX"], record["speedY"])
        big = crossing_audit.pairs([value * 1000 for value in record["speedX"]],
                                   [value * 1000 for value in record["speedY"]])
        self.assertEqual(small, big)


if __name__ == "__main__":
    unittest.main()
