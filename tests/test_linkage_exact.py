"""An exact rosette linkage: the closure must be rational at every crank station.

The rule (spec: "Rosettes from linkages, done exactly"): a coupler joint is rational only
when the closure quadratic has a rational square discriminant. A parallelogram closes
exactly; a general Grashof crank-rocker does not.
"""

import importlib.util
import sys
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location("linkage_exact", ROOT / "scripts" / "linkage_exact.py")
linkage_exact = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(linkage_exact)


class ExactLinkage(unittest.TestCase):
    def setUp(self):
        self.points = linkage_exact.unit_points()

    def test_the_parallelogram_closes_exactly(self):
        """a = c = 2, b = d = 3 — every rational crank direction gives a rational joint."""
        exact, total, missing = linkage_exact.check_set(2, 3, 2, 3, self.points)
        self.assertEqual(exact, total, f"not exact at {missing[:2]}")
        self.assertGreater(total, 8)

    def test_the_joint_really_is_a_joint(self):
        """The returned rocker point satisfies both circle conditions, exactly."""
        A = (Fraction(0), Fraction(1))          # a = 1
        B = linkage_exact.closure(A, 1, 2, 2)   # b = 1, c = 2, d = 2
        self.assertIsNotNone(B)
        bx, by = B
        ax, ay = A
        dx, dy = Fraction(2), Fraction(0)
        self.assertEqual((bx - ax) ** 2 + (by - ay) ** 2, 1)      # |B − A| = b = 1
        self.assertEqual((bx - dx) ** 2 + (by - dy) ** 2, 4)      # |B − D| = c = 2

    def test_a_general_crank_rocker_does_not_close_everywhere(self):
        """A set that is not a parallelogram loses some rational stations, which is why
        the page's linkage figure carries the word "sampled"."""
        exact, total, _ = linkage_exact.check_set(1, 3, 2, 4, self.points)
        self.assertLess(exact, total)


if __name__ == "__main__":
    unittest.main()
