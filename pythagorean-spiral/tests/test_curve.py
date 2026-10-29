"""The curl: resolution-driven shape, and a fit that is at the chain's floor."""

import math
import unittest

from pythagorean_spiral import design, spans as spanmod
from pythagorean_spiral.triples import for_angle, thinnest

THIN = thinnest(3125)


class TestForAngle(unittest.TestCase):
    def test_returns_the_thinnest_triangle_under_the_target(self):
        t = for_angle(6.0)
        self.assertLessEqual(t.degrees, 6.0)
        self.assertGreater(for_angle(6.1).degrees, t.degrees - 1e-12)

    def test_smaller_target_means_a_longer_hypotenuse(self):
        self.assertLess(for_angle(0.5).c, for_angle(0.1).c)
        self.assertLess(for_angle(0.5).degrees, for_angle(5.0).degrees)

    def test_rejects_impossible_budgets(self):
        for bad in (0, -1, 45, 90):
            with self.assertRaises(ValueError):
                for_angle(bad)


class TestCostGuard(unittest.TestCase):
    def test_refuses_a_budget_that_would_need_astronomical_integers(self):
        with self.assertRaises(ValueError) as caught:
            design.curl(200.0, 1.0, 1.0)
        self.assertIn("chord budget", str(caught.exception))


class TestCurl(unittest.TestCase):
    def setUp(self):
        self.path = design.curl(200.0, 6.0, 1.0)

    def test_peak_is_what_was_asked_for(self):
        """Within one chord turn: the triangle quantises the angle, so the
        peak can only land on a multiple of it."""
        widest = max(abs(k) for k in self.path.turns) * self.path.triangle.degrees
        self.assertAlmostEqual(self.path.peak_degrees, 200.0, delta=widest)

    def test_peak_reads_past_180(self):
        """A curl over the top says 200, not -160: the heading is unwrapped."""
        self.assertGreater(self.path.peak_degrees, 180.0)

    def test_chord_budget_is_respected(self):
        widest = max(abs(k) for k in self.path.turns) * self.path.triangle.degrees
        self.assertLessEqual(widest, 6.0)

    def test_ends_exactly_east_and_higher_than_it_started(self):
        self.assertEqual(self.path.coeff, 0)
        self.assertEqual(self.path.heading.axis_name(), "east")
        self.assertGreater(float(self.path.final[1]), 0.0)

    def test_is_still_a_lobe(self):
        n = len(self.path.turns) // 2
        self.assertEqual(len(self.path.turns), 2 * n)
        self.assertEqual(self.path.turns[0], 0)
        self.assertEqual(self.path.turns[-1], 0)
        self.assertEqual(max(self.path.turns), n - 1)

    def test_a_finer_budget_is_a_thinner_triangle(self):
        coarse = design.curl(200.0, 12.0, 1.0)
        fine = design.curl(200.0, 8.0, 1.0)
        self.assertLess(fine.triangle.degrees, coarse.triangle.degrees)
        self.assertGreater(len(fine.turns), len(coarse.turns))


class TestFittedCurve(unittest.TestCase):
    def setUp(self):
        self.path = design.curl(200.0, 6.0, 1.0)
        self.curves = spanmod.spans(self.path, math.radians(20))

    def test_the_path_is_g1(self):
        self.assertLess(spanmod.join_kink(self.curves), 1e-9)

    def test_the_fit_sits_on_the_chains_own_floor(self):
        nodes = self.path.floats()
        worst = max(spanmod.deviation(c, nodes, samples=81) for c in self.curves)
        floor = spanmod.sagitta(self.path)
        self.assertLess(worst, 1.2 * floor)

    def test_no_span_swallows_the_apsis(self):
        """The reversal must fall on a span boundary, not inside a cubic."""
        apex = max(range(len(self.path.turns)), key=lambda k: self.path.cumulative()[k])
        bounds = {int(c["s0"]) for c in self.curves} | {int(c["s1"]) for c in self.curves}
        self.assertIn(apex, bounds)


if __name__ == "__main__":
    unittest.main()
