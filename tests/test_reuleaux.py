"""Constant width: the Reuleaux triangle, its Bézier handles, and the Pell copy.

√3 is not rational, so the exact arcs are declared outside NAMED; the Bézier
version is the practical one, and the Pell copy measures what a rational
approximation of the 60° costs.
"""

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import reuleaux as R  # noqa: E402


class TestReuleaux(unittest.TestCase):
    def test_the_exact_arcs_have_width_one(self):
        pts = R.reuleaux()
        wmax, wmin, spread = R.width(pts)
        self.assertAlmostEqual(wmax, 1.0, places=4)
        self.assertAlmostEqual(wmin, 1.0, places=4)
        self.assertLess(spread, 1e-4)
        self.assertEqual(R.closure_gap(pts), 0.0)

    def test_the_bezier_handles_track_the_arcs(self):
        pts, arcs = R.reuleaux_bezier()
        centres = [(0.0, 0.0), (1.0, 0.0), (0.5, R.ROOT_SIN)]
        err = max(R.arc_error(a, c, 1.0) for a, c in zip(arcs, centres))
        self.assertLess(err, 5e-5)
        wmax, wmin, spread = R.width(pts)
        self.assertLess(spread, 1e-4)
        self.assertEqual(R.closure_gap(pts), 0.0)

    def test_the_pell_copy_shows_the_cost(self):
        pts = R.reuleaux(R.PELL_SIN)
        gap = R.closure_gap(pts)
        self.assertGreater(gap, 1e-5)
        self.assertLess(gap, 1e-3)
        wmax, wmin, spread = R.width(pts)
        self.assertLess(spread, 1e-3)

    def test_the_sines(self):
        # sin 60° = √3/2; the Pell copy uses 26/15 → 13/15
        self.assertAlmostEqual(R.ROOT_SIN ** 2, 0.75, places=15)
        self.assertEqual(R.PELL_SIN, 13 / 15)


if __name__ == "__main__":
    unittest.main()
