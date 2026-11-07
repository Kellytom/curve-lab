"""The discrete clothoid: a turn schedule quantised to p-triple angles.

The page claims that the quantisation does not bend the law. This checks it in
the generator's own numbers, and checks that the polygon is exact.
"""

import sys
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import discrete_clothoid as D  # noqa: E402


class TestDiscreteClothoid(unittest.TestCase):
    def test_every_turn_is_a_pythagorean_angle(self):
        d = D.build()
        angles = {r["deg"] for r in D.LADDER}
        for step in d["chosen"]:
            row = step["row"]
            with self.subTest(k=step["k"], triple=(row["a"], row["b"], row["c"])):
                self.assertEqual(row["a"] ** 2 + row["b"] ** 2, row["c"] ** 2)
                self.assertIn(row["deg"], angles)

    def test_the_schedule_rises(self):
        d = D.build()
        turns = [step["row"]["deg"] for step in d["chosen"]]
        for a, b in zip(turns, turns[1:]):
            self.assertLess(a, b)

    def test_the_exponent_stays_one(self):
        d = D.build()
        self.assertAlmostEqual(d["slope"], 1.0, delta=0.05)

    def test_the_error_is_under_half_the_largest_gap(self):
        d = D.build()
        self.assertLess(d["max_err"], d["gap"] / 2 + 1e-9)

    def test_the_nodes_are_rational_and_scale_to_integers(self):
        d = D.build()
        for x, y in d["exact"]:
            with self.subTest(node=(x, y)):
                self.assertIsInstance(x, Fraction)
                self.assertIsInstance(y, Fraction)
                self.assertEqual((x * d["scale"]).denominator, 1)
                self.assertEqual((y * d["scale"]).denominator, 1)
        self.assertGreater(d["digits"], 20)


if __name__ == "__main__":
    unittest.main()
