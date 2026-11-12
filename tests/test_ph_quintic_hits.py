"""Integer hits: the stops, the exact gcd method, and the near misses."""

import sys
import unittest
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ph_quintic_hits as H  # noqa: E402


class TestHits(unittest.TestCase):
    def test_the_curve_polynomials(self):
        x, y = H.curve_polynomials((1, 0, 0), (0, 1, 0))
        self.assertEqual(x, [F(0), F(1), F(0), F(-1, 3)])
        self.assertEqual(y, [F(0), F(0), F(1)])

    def test_the_pick_hits_at_the_stops(self):
        hits = H.hits_at_stops((2, -3, 3), (2, -12, 12))
        self.assertEqual([(t, x, y) for t, x, y in hits],
                         [(F(0), 0, 0), (F(1), 15, 4)])

    def test_the_target_hits_at_the_stops(self):
        hits = H.hits_at_stops((F(1, 5), -2, 2), (F(2, 5), F(-3, 2), F(8, 5)))
        self.assertEqual([(x, y) for _t, x, y in hits], [(0, 0), (-13, -20)])

    def test_the_stops_are_not_complete_in_general(self):
        # w = 1 + i t has pitch 3; its scaled curve ends at (2, 3)
        hits = H.hits_at_stops((1, 0, 0), (0, 1, 0))
        self.assertEqual([(x, y) for _t, x, y in hits], [(0, 0), (2, 3)])

    def test_the_exact_method_finds_the_same_points(self):
        hits = H.hits_exact((2, -3, 3), (2, -12, 12), box=(0, 15, 0, 4))
        points = sorted(hit["point"] for hit in hits)
        self.assertEqual(points, [(0, 0), (15, 4)])
        parameters = sorted(hit["parameters"][0] for hit in hits)
        self.assertEqual(parameters, [0.0, 1.0])

    def test_the_exact_method_confirms_with_the_gcd(self):
        hits = H.hits_exact((1, 0, 0), (0, 1, 0), box=(0, 2, 0, 3))
        self.assertEqual(sorted(hit["point"] for hit in hits), [(0, 0), (2, 3)])
        for hit in hits:
            self.assertEqual(hit["gcd_degree"], 1)

    def test_the_exact_method_refuses_a_huge_box(self):
        with self.assertRaises(ValueError):
            H.hits_exact((2, -3, 3), (2, -12, 12), box=(0, 1000, 0, 1000), max_points=100)

    def test_the_near_misses_reach_zero_at_a_hit(self):
        misses = H.near_misses((2, -3, 3), (2, -12, 12), samples=2000)
        self.assertAlmostEqual(misses[0][0], 0.0, places=6)

    def test_a_curve_with_no_integer_hits_reports_none(self):
        # the 5.07 curve, box around the start only
        hits = H.hits_exact((F(1, 5), -2, 2), (F(2, 5), F(-8, 5), F(31, 20)),
                            box=(0, 1, 0, 1))
        self.assertIsInstance(hits, list)


if __name__ == "__main__":
    unittest.main()
