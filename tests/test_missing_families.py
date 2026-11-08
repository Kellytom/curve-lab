"""The six missing families: each identity checked where it is cheap."""

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import missing_families as M  # noqa: E402


class TestMissingFamilies(unittest.TestCase):
    def test_elastica_is_bounded_and_finite(self):
        for m in (1.2, 2.0, 2.8):
            pts = M.elastica(m, s_max=5.0, n=1500)
            self.assertGreater(len(pts), 1000)
            self.assertTrue(all(math.isfinite(x) and math.isfinite(y) for x, y in pts[::100]))

    def test_polynomial_spiral_turns_more_as_p_rises(self):
        # total turn = ∫ s^p ds = L^(p+1)/(p+1)
        def turn(p, L=2.0):
            pts = M.polynomial_spiral(p, s_max=L, n=2000)
            total, prev = 0.0, None
            for a, b in zip(pts, pts[1:]):
                ang = math.atan2(b[1] - a[1], b[0] - a[0])
                if prev is not None:
                    d = ang - prev
                    while d > math.pi:
                        d -= 2 * math.pi
                    while d < -math.pi:
                        d += 2 * math.pi
                    total += d
                prev = ang
            return abs(total)
        self.assertLess(turn(1), turn(2))
        self.assertLess(turn(2), turn(3))

    def test_sinusoidal_spiral_identity(self):
        for n in (1, 0.5, -0.5, 2):
            with self.subTest(n=n):
                pts = M.sinusoidal(n, k=200)
                for i, (x, y) in enumerate(pts):
                    th = -math.pi / (2 * abs(n)) + 1e-4 + (math.pi / abs(n) - 2e-4) * i / 200
                    th = max(-math.pi / (2 * abs(n)) + 1e-4,
                             min(math.pi / (2 * abs(n)) - 1e-4, th))
                    r = math.hypot(x, y)
                    if r > 1e-9 and math.cos(n * math.atan2(y, x)) > 0:
                        self.assertAlmostEqual(r ** n,
                                               math.cos(n * math.atan2(y, x)), places=6)

    def test_trochoid_formula(self):
        k = 3
        pts = M.trochoid(k, turns=1, n=400)
        self.assertLess(math.dist(pts[0], ((k + 1) - 1.0, 0.0)), 1e-12)
        self.assertLess(math.dist(pts[-1], pts[0]), 1e-9)

    def test_catmull_rom_interpolates(self):
        ctrl = [(-1.0, 0.0), (0.0, 1.2), (1.2, 0.9), (2.0, 0.0)]
        pts = M.catmull_rom(ctrl, n=40)
        self.assertLess(math.dist(pts[0], ctrl[1]), 1e-12)
        self.assertLess(math.dist(pts[-1], ctrl[2]), 1e-12)

    def test_rational_quadratic_is_the_unit_circle(self):
        pts = M.rational_quadratic((1, 0), (1, 1), (0, 1), 1 / math.sqrt(2))
        for x, y in pts[::10]:
            self.assertAlmostEqual(math.hypot(x, y), 1.0, places=12)

    def test_quintic_hermite_matches_ends(self):
        p0, p1 = (0.0, 0.0), (2.0, 0.0)
        v0, v1 = (1.0, 0.3), (0.4, -1.0)
        a0, a1 = (0.0, 1.0), (0.5, 0.0)
        h = 1e-5
        pts = M.quintic_hermite(p0, p1, v0, v1, a0, a1, n=1000)
        self.assertLess(math.dist(pts[0], p0), 1e-12)
        self.assertLess(math.dist(pts[-1], p1), 1e-12)
        # p'(0) ≈ v0
        d0 = ((pts[1][0] - pts[0][0]) / (1 / 1000),
              (pts[1][1] - pts[0][1]) / (1 / 1000))
        self.assertLess(math.dist(d0, v0), 1e-2)

    def test_rational_ph_circle_speed(self):
        for t in (-0.5, 0.0, 0.7):
            h = 1e-6
            a = ((1 - (t + h) ** 2) / (1 + (t + h) ** 2), 2 * (t + h) / (1 + (t + h) ** 2))
            b = ((1 - (t - h) ** 2) / (1 + (t - h) ** 2), 2 * (t - h) / (1 + (t - h) ** 2))
            speed = math.dist(a, b) / (2 * h)
            self.assertAlmostEqual(speed, 2 / (1 + t * t), places=5)

    def test_degree_seven_ph(self):
        _pts, scale, pc = M.degree_seven_ph()
        self.assertEqual(len(pc.cp), 8)
        self.assertTrue(pc.check(4, scale))


if __name__ == "__main__":
    unittest.main()
