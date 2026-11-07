"""Gen-Arch: r = a + b·φ^(1/c), and the radial of a log-aesthetic curve.

The page's claim is the paper's: the radial of a LA curve is a Gen-Arch spiral
with c = α − 1. Here that is checked on the formulas, exactly to floating
point, and the three dials (α, the repo's p, and c) are checked against each
other so they cannot silently drift apart in the prose.
"""

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import gen_arch as G  # noqa: E402


class TestGenArch(unittest.TestCase):
    def test_the_polar_law(self):
        for c in (-2, -1, 1, 2):
            with self.subTest(c=c):
                pts = G.spiral(c, phi0=0.6, phi1=3.0, n=50)
                for i, (x, y) in enumerate(pts):
                    phi = 0.6 + (3.0 - 0.6) * i / 50
                    r = math.hypot(x, y)
                    self.assertAlmostEqual(r, phi ** (1.0 / c), places=6)

    def test_the_radial_constant(self):
        for alpha in (-1.0, -2.0, 2.0, 3.0):
            with self.subTest(alpha=alpha):
                want = ((alpha - 1) / alpha) ** (1 / (alpha - 1))
                for s in (0.2, 0.7, 1.4, 2.0):
                    self.assertAlmostEqual(G.la_radius_ratio(s, alpha) / want,
                                           1.0, places=12)

    def test_the_fitted_exponent_is_one_over_alpha_minus_one(self):
        for row in G.analysis():
            with self.subTest(alpha=row["alpha"]):
                self.assertAlmostEqual(row["slope"], 1 / (row["alpha"] - 1), places=6)
                self.assertLess(row["dev"], 1e-12)

    def test_the_three_dials_agree(self):
        for row in G.analysis():
            with self.subTest(alpha=row["alpha"]):
                self.assertAlmostEqual(row["c"], row["alpha"] - 1)
                self.assertAlmostEqual(row["p"], -1 / row["alpha"])
                # c = -1/p - 1, the form the page quotes
                self.assertAlmostEqual(row["c"], -1 / row["p"] - 1)

    def test_the_classical_cases(self):
        # clothoid alpha=-1 -> c=-2 (lituus); involute alpha=2 -> c=1
        self.assertEqual(G.radial_row(-1.0)["c"], -2.0)
        self.assertEqual(G.radial_row(2.0)["c"], 1.0)


if __name__ == "__main__":
    unittest.main()
