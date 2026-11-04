import unittest
from fractions import Fraction
from pathlib import Path

from curve_lab.quadratic import at, elevate

ROOT = Path(__file__).resolve().parents[1]


class QuadraticElevationTest(unittest.TestCase):
    def test_elevation_preserves_the_quadratic(self):
        q = [(0, 0), (4, -3), (10, 0)]
        c = elevate(*q)
        self.assertEqual(c[0], (0, 0))
        self.assertEqual(c[3], (10, 0))
        for k in (0, 1, 3, 7, 25):
            t = Fraction(k, 25)
            self.assertEqual(at(q, t), at(c, t))

    def test_probe_page(self):
        page = (ROOT / "workbench" / "quadratic-s.html").read_text(
            encoding="utf-8")
        self.assertIn("Fig. Q1", page)
        self.assertIn("G1", page)
        self.assertIn("G2", page)
        self.assertIn("curvature sign reverses", page)
        self.assertIn("(10,−10)", page)


if __name__ == "__main__":
    unittest.main()
