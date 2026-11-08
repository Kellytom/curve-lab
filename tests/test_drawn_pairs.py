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

    def test_yin_yang_is_two_exact_semicircles(self):
        pts = D.yin_yang(n=120)
        self.assertLess(math.dist(pts[0], (0.0, 1.0)), 1e-12)
        self.assertLess(math.dist(pts[121], (0.0, 0.0)), 1e-12)
        self.assertLess(math.dist(pts[-1], (0.0, -1.0)), 1e-12)
        for x, y in pts[:121]:
            self.assertAlmostEqual(math.dist((x, y), (0.0, 0.5)), 0.5, places=12)
        for x, y in pts[121:]:
            self.assertAlmostEqual(math.dist((x, y), (0.0, -0.5)), 0.5, places=12)


if __name__ == "__main__":
    unittest.main()
