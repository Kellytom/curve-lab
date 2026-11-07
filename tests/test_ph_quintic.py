"""PH quintics: degree five, integer controls, rational arc length."""

import sys
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ph_quintic as PQ  # noqa: E402

CASES = PQ.CASES


class TestPHQuintics(unittest.TestCase):
    def test_degree_is_five(self):
        for title, h, u, v in CASES:
            with self.subTest(case=title):
                p = max(len(u) - 1, len(v) - 1)
                self.assertEqual(len(h) - 1 + 2 * p + 1, 5)
                d = PQ.build_case(h, u, v)
                self.assertEqual(len(d["pc"].cp), 6)

    def test_controls_are_integers_at_the_scale(self):
        for title, h, u, v in CASES:
            with self.subTest(case=title):
                d = PQ.build_case(h, u, v)
                self.assertTrue(d["pc"].check(PQ.M, d["scale"]))
                for x, y in d["pc"].integer_control(d["scale"]):
                    self.assertIsInstance(x, int)
                    self.assertIsInstance(y, int)

    def test_arc_length_is_rational(self):
        for title, h, u, v in CASES:
            with self.subTest(case=title):
                d = PQ.build_case(h, u, v)
                self.assertIsInstance(d["arc"], Fraction)
                self.assertGreater(d["arc"], 0)

    def test_the_curve_starts_and_ends_at_its_controls(self):
        for title, h, u, v in CASES:
            with self.subTest(case=title):
                d = PQ.build_case(h, u, v)
                for got, want in ((d["pc"].bezier(0.0), d["pc"].cp[0]),
                                  (d["pc"].bezier(1.0), d["pc"].cp[-1])):
                    self.assertAlmostEqual(got[0], float(want[0]), places=12)
                    self.assertAlmostEqual(got[1], float(want[1]), places=12)


if __name__ == "__main__":
    unittest.main()
