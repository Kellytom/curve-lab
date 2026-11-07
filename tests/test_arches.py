"""Arches from elliptic and Fermat curves: exact ends, no rational parametrisation."""

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import arches as A  # noqa: E402


class TestArches(unittest.TestCase):
    def test_the_elliptic_oval_and_branch(self):
        oval = A.elliptic_arch(0, 1, -1.0, 0.0)
        branch = A.elliptic_arch(0, 1, 0.0, 2.0)
        self.assertLess(math.dist(oval[0], (-1.0, 0.0)), 1e-9)
        self.assertLess(math.dist(oval[-1], (0.0, 1.0)), 1e-9)
        self.assertLess(math.dist(branch[0], (0.0, 1.0)), 1e-9)
        self.assertLess(math.dist(branch[-1], (2.0, 3.0)), 1e-9)
        for x, y in branch:
            self.assertAlmostEqual(y * y, x ** 3 + 1, places=9)

    def test_the_elliptic_integer_points(self):
        pts = A.integer_points_elliptic(0, 1, 60)
        for p in ((-1, 0), (0, 1), (0, -1), (2, 3), (2, -3)):
            self.assertIn(p, pts)

    def test_the_fermat_arcs(self):
        for n in (3, 4):
            with self.subTest(n=n):
                pts = A.fermat_arc(n)
                self.assertLess(math.dist(pts[0], (0.0, 1.0)), 1e-9)
                self.assertLess(math.dist(pts[-1], (1.0, 0.0)), 1e-9)
                for x, y in pts[::20]:
                    self.assertAlmostEqual(x ** n + y ** n, 1.0, places=9)

    def test_fermat_integer_points_are_only_the_trivial_ones(self):
        # a finite check, not the theorem: up to |x|,|y| = 40
        self.assertEqual(sorted(A.fermat_integer_solutions(3, 40)),
                         [(0, 1), (1, 0)])
        self.assertEqual(sorted(A.fermat_integer_solutions(4, 40)),
                         [(-1, 0), (0, -1), (0, 1), (1, 0)])


if __name__ == "__main__":
    unittest.main()
