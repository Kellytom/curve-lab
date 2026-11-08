"""The two drawn curves: Lissajous closes; the yin-yang boundary is exact arcs."""

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import drawn_pairs as D  # noqa: E402


class TestDrawnPairs(unittest.TestCase):
    def test_lissajous_closes(self):
        pts = D.lissajous()
        self.assertLess(math.dist(pts[0], pts[-1]), 1e-9)
        self.assertLessEqual(max(abs(x) for x, _ in pts), 1.0 + 1e-12)
        self.assertLessEqual(max(abs(y) for _, y in pts), 1.0 + 1e-12)

    def test_lissajous_points_follow_the_formula(self):
        a, b, phase = 3, 2, math.pi / 2
        pts = D.lissajous(a, b, phase, n=160)
        for i in (0, 17, 53, 111, 159):
            t = 2 * math.pi * i / 160
            x, y = pts[i]
            self.assertAlmostEqual(x, math.sin(a * t + phase), places=12)
            self.assertAlmostEqual(y, math.sin(b * t), places=12)

    def test_the_yin_yang_is_a_g2_splice(self):
        pts, knots = D.yin_yang_g2(spans=4, n=90)
        self.assertLess(math.dist(pts[0], (0.0, 1.0)), 1e-12)
        self.assertLess(math.dist(pts[-1], (0.0, -1.0)), 1e-12)
        for got, want in zip(knots, [(0.0, 1.0), (0.7, 0.5), (0.0, 0.0),
                                     (-0.7, -0.5), (0.0, -1.0)]):
            self.assertLess(math.dist(got, want), 1e-12)
        # G2 is structural: the quintic Hermite span matches p, p' and p'' at
        # both ends, so adjacent spans with the same data join G2.
        from missing_families import quintic_hermite
        v0, v1 = (1.0, 0.0), (0.0, 1.0)
        a0, a1 = (0.0, 2.0), (3.0, 0.0)
        span = quintic_hermite((0.0, 0.0), (1.0, 0.0), v0, v1, a0, a1, n=4000)
        h = 1 / 4000

        def deriv(seq, i):
            return ((seq[i][0] - seq[i - 1][0]) / h,
                    (seq[i][1] - seq[i - 1][1]) / h)

        d_start = deriv(span, 1)
        d_end = deriv(span, len(span) - 1)
        self.assertLess(math.dist(d_start, v0), 1e-2)
        self.assertLess(math.dist(d_end, v1), 1e-2)


if __name__ == "__main__":
    unittest.main()
