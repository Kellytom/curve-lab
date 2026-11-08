"""qAC and discrete LAC: the check is the c = 0 limit and the recurrence."""

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import qac_dlac as Q  # noqa: E402


class TestQAC(unittest.TestCase):
    def test_c_zero_recovers_the_lac(self):
        # q^α must be linear in arc length when c = 0
        for alpha in (1.5, 2.0, 3.0):
            with self.subTest(alpha=alpha):
                slope, dev = Q.lac_check(alpha)
                self.assertGreater(slope, 0)
                self.assertLess(dev, 1e-4)

    def test_qac_curves_are_finite_and_start_at_the_origin(self):
        for title, alpha, c in Q.CASES:
            with self.subTest(case=title):
                pts = Q.qac(alpha, c)
                self.assertGreater(len(pts), 100)
                self.assertLess(math.dist(pts[0], (0.0, 0.0)), 1e-12)
                for x, y in pts[::100]:
                    self.assertTrue(math.isfinite(x) and math.isfinite(y))


class TestDLAC(unittest.TestCase):
    def test_the_recurrence_holds(self):
        for title, alpha, C in Q.D_CASES:
            with self.subTest(case=title):
                a = alpha - 1
                u0 = 1.6
                us = [u0]
                for _ in range(20):
                    us.append((C - 1.0 / (us[-1] ** a)) ** (1.0 / a))
                for prev, nxt in zip(us, us[1:]):
                    self.assertAlmostEqual(nxt ** a + 1.0 / prev ** a, C, places=12)

    def test_the_curve_is_normalised_and_has_the_right_count(self):
        for title, alpha, C in Q.D_CASES:
            with self.subTest(case=title):
                pts = Q.dlac(alpha, C, n=40)
                self.assertEqual(len(pts), 42)   # the start plus n+1 segment ends
                self.assertLessEqual(max(max(abs(x) for x, _ in pts),
                                         max(abs(y) for _, y in pts)), 1.0 + 1e-12)


if __name__ == "__main__":
    unittest.main()
