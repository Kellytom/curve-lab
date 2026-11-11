"""The PH quintic Hermite interpolant and PPH: endpoint, tangents, C² join."""

import cmath
import math
import unittest

from curve_lab.ph_hermite import (arc_length, continue_span, control_points,
                                  curvature, derivatives, hermite, join_defects,
                                  point_at, w_at)


class TestPHHermite(unittest.TestCase):
    CASES = [
        ((0.0, 0.0), (4.0, 1.5), math.radians(10), math.radians(-40), 1),
        ((0.0, 0.0), (4.0, 1.5), math.radians(10), math.radians(-40), -1),
        ((-1.0, 2.0), (2.5, -0.5), 0.0, math.radians(120), 1),
        ((0.0, 0.0), (0.0, 3.0), math.radians(90), math.radians(60), 1),
    ]

    def test_the_endpoint_is_hit(self):
        for p0, p1, t0, t1, root in self.CASES:
            with self.subTest(p1=p1, root=root):
                s = hermite(p0, p1, t0, t1, root=root)
                self.assertLess(abs(point_at(s, 1.0) - complex(*p1)), 1e-12)

    def test_the_start_is_the_start(self):
        for p0, p1, t0, t1, root in self.CASES:
            with self.subTest(p1=p1):
                s = hermite(p0, p1, t0, t1, root=root)
                self.assertLess(abs(point_at(s, 0.0) - complex(*p0)), 1e-12)

    def test_the_endpoint_tangents_are_the_prescribed_ones(self):
        for p0, p1, t0, t1, root in self.CASES:
            with self.subTest(p1=p1, root=root):
                s = hermite(p0, p1, t0, t1, root=root)
                for t, want in ((0.0, t0), (1.0, t1)):
                    _, d, _ = derivatives(s, t)
                    self.assertLess(abs(cmath.phase(d) - want), 1e-12)

    def test_the_speed_is_the_polynomial(self):
        for p0, p1, t0, t1, root in self.CASES:
            with self.subTest(p1=p1, root=root):
                s = hermite(p0, p1, t0, t1, root=root)
                for i in range(1, 20):
                    t = i / 20
                    _, d, _ = derivatives(s, t)
                    w = w_at(s, t)
                    self.assertLess(abs(abs(d) - abs(w * w)), 1e-12)
                    self.assertLess(abs(abs(w) ** 2 - abs(w * w)), 1e-12)

    def test_the_arc_length_is_the_polynomial_integral(self):
        for p0, p1, t0, t1, root in self.CASES:
            with self.subTest(p1=p1, root=root):
                s = hermite(p0, p1, t0, t1, root=root)
                numeric = 0.0
                prev = None
                for i in range(0, 4001):
                    t = i / 4000
                    p = point_at(s, t)
                    if prev is not None:
                        numeric += abs(p - prev)
                    prev = p
                self.assertLess(abs(numeric - arc_length(s)) / arc_length(s), 1e-4)

    def test_the_arc_length_beats_the_chord(self):
        for p0, p1, t0, t1, root in self.CASES:
            with self.subTest(p1=p1):
                s = hermite(p0, p1, t0, t1, root=root)
                self.assertGreaterEqual(arc_length(s), abs(complex(*p1) - complex(*p0)) - 1e-12)

    def test_the_declared_speed_rule(self):
        s = hermite((0.0, 0.0), (4.0, 1.5), 0.1, -0.4)
        d = abs(complex(4.0, 1.5))
        self.assertAlmostEqual(abs(s["w"][0]), math.sqrt(d), places=12)
        self.assertAlmostEqual(abs(s["w"][2]), math.sqrt(d), places=12)

    def test_two_points_are_required(self):
        with self.assertRaises(ValueError):
            hermite((1.0, 1.0), (1.0, 1.0), 0.0, 0.0)

    def test_the_five_control_points_start_and_end_on_the_data(self):
        s = hermite((0.0, 0.0), (4.0, 1.5), 0.1, -0.4)
        cp = control_points(s)
        self.assertEqual(len(cp), 6)
        self.assertLess(abs(cp[0]), 1e-12)
        self.assertLess(abs(cp[-1] - complex(4.0, 1.5)), 1e-12)


class TestPHPSpline(unittest.TestCase):
    def setUp(self):
        self.s1 = hermite((0.0, 0.0), (4.0, 1.5),
                          math.radians(10), math.radians(-40))
        self.s2 = continue_span(self.s1, math.radians(-95), 1.2)

    def test_the_join_is_c2(self):
        d = join_defects(self.s1, self.s2)
        for key, value in d.items():
            with self.subTest(key=key):
                self.assertLess(value, 1e-12)

    def test_the_second_span_continues_forward(self):
        _, d1, _ = derivatives(self.s1, 1.0)
        _, d2, _ = derivatives(self.s2, 0.0)
        self.assertGreater((d1 * d2.conjugate()).real, 0.0)

    def test_the_join_takes_no_fitting(self):
        # a is the previous c, exactly
        self.assertEqual(self.s2["w"][0], self.s1["w"][2])

    def test_the_curvature_is_continuous_at_the_join(self):
        self.assertAlmostEqual(curvature(self.s1, 1.0), curvature(self.s2, 0.0), places=12)

    def test_the_second_span_is_ph(self):
        for i in range(1, 20):
            t = i / 20
            _, d, _ = derivatives(self.s2, t)
            w = w_at(self.s2, t)
            self.assertLess(abs(abs(d) - abs(w * w)), 1e-12)


if __name__ == "__main__":
    unittest.main()
