"""The Maclaurin trisectrix: exact at √3, and what the Pell copy costs."""

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import maclaurin as M  # noqa: E402


class TestMaclaurin(unittest.TestCase):
    def test_the_points_are_on_the_curve(self):
        for k in (M.ROOT3, M.PELL3):
            with self.subTest(k=k):
                for x, y in M.loop(k)[::25]:
                    self.assertLess(abs(M.equation(x, y)), 1e-12)

    def test_the_exact_loop_closes_at_the_node(self):
        pts = M.loop(M.ROOT3)
        self.assertLess(math.dist(pts[0], pts[-1]), 1e-12)
        self.assertLess(math.dist(pts[0], (0.0, 0.0)), 1e-12)

    def test_the_pell_copy_leaves_a_measured_gap(self):
        pts = M.loop(M.PELL3)
        gap = math.dist(pts[0], pts[-1])
        self.assertGreater(gap, 1e-4)
        self.assertLess(gap, 1e-2)

    def test_the_trisectrix_point(self):
        # t = 0 gives (3, 0)
        self.assertEqual(M.point(0.0), (3.0, 0.0))


if __name__ == "__main__":
    unittest.main()
