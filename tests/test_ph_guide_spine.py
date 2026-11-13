"""The guide spine: the two worked examples from the design notes."""

import sys
import unittest
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ph_guide_spine import GuideSpine  # noqa: E402


class TestGuideSpine(unittest.TestCase):
    def test_the_decelerating_arch_anchors(self):
        spine = GuideSpine((1.0, -0.5, 0.5, -0.5, 0.3, -0.2, 0.1), 625)
        rows = spine.anchor_table(5)
        self.assertEqual([(r["x"], r["y"]) for r in rows],
                         [(0, 0), (125, 115), (250, 214), (375, 300), (500, 374), (625, 438)])

    def test_the_s_curve_anchors(self):
        spine = GuideSpine((0.2, -1.5, 4.5, -2.0, 1.8, -2.4, 0.4), 625)
        rows = spine.anchor_table(5)
        self.assertEqual([(r["x"], r["y"]) for r in rows],
                         [(0, 0), (125, 8), (250, 54), (375, 207), (500, 456), (625, 625)])

    def test_the_s_curve_slopes(self):
        spine = GuideSpine((0.2, -1.5, 4.5, -2.0, 1.8, -2.4, 0.4), 625)
        expected = [0.2, 0.086, 0.742, 1.709, 2.046, 0.1]
        for row, want in zip(spine.anchor_table(5), expected):
            with self.subTest(t=float(row["t"])):
                self.assertAlmostEqual(row["slope"], want, delta=0.01)

    def test_the_control_vectors_are_the_derivatives_at_zero(self):
        spine = GuideSpine((1.0, -0.5, 0.5, -0.5, 0.3, -0.2, 0.1), 625)
        vectors = spine.control_vectors()
        self.assertEqual(vectors[4:], [22500, -90000, 315000])
        self.assertEqual(vectors[0], 625)

    def test_the_endpoint_is_the_sum_of_the_orders(self):
        n = (0.2, -1.5, 4.5, -2.0, 1.8, -2.4, 0.4)
        spine = GuideSpine(n, 625)
        self.assertEqual(spine.point(F(1))[1], F(625))
        self.assertAlmostEqual(float(sum(n)), 1.0)

    def test_the_x_steps_are_exact(self):
        spine = GuideSpine((0.2, -1.5, 4.5, -2.0, 1.8, -2.4, 0.4), 625)
        self.assertEqual([r["x"] for r in spine.anchor_table(5)], [0, 125, 250, 375, 500, 625])


if __name__ == "__main__":
    unittest.main()
