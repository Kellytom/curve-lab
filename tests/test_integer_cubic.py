import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class IntegerCubicPageTest(unittest.TestCase):
    def test_page(self):
        page = (ROOT / "workbench" / "integer-cubic.html").read_text(
            encoding="utf-8")
        self.assertIn("Integer cubic Béziers", page)
        self.assertIn("Fig. P1", page)
        self.assertIn("P0 = (0, 0)", page)
        self.assertIn("P1 = (a, −b)", page)
        self.assertIn("P2 = (2c − a, b)", page)
        self.assertIn("P3 = (2c, 0)", page)
        self.assertIn("(3,4,5)", page.replace(" ", ""))
        self.assertIn("P0=(0,0), P1=(3,−4), P2=(7,4), P3=(10,0)", page)
        self.assertIn("5-12-13", page)
        self.assertIn("24-7-25", page)
        self.assertIn("3125", page)
        self.assertIn("53.13", page)
        self.assertIn("36.87", page)
        self.assertIn("cos=3/5, sin=4/5", page)
        self.assertIn("cos=4/5, sin=3/5", page)
        self.assertIn('id="tri-canvas"', page)
        self.assertIn('id="tri-buttons"', page)
        self.assertIn("curve_lab/pyth_cubic.py", page)
        self.assertIn("What this means for the curve system", page)
        self.assertIn("Points along the curve", page)
        self.assertIn("Offsets are a separate promise", page)
        self.assertIn("G2 joins, symmetric and asymmetric", page)
        self.assertIn("P1=(27,−36)", page)
        self.assertIn("(88,−24)", page)
        self.assertIn("asymmetric", page)
        self.assertIn("Fig. P2", page)
        self.assertIn("The 60³ grid", page)
        self.assertIn("3³ · 4³ · 5³", page)
        self.assertIn("216000", page)
        self.assertIn("Another route: elevate a quadratic", page)
        self.assertIn("What was done, in plain English", page)
        self.assertIn("Worked example, and a correction", page)
        self.assertIn("Grid ledger", page)
        self.assertIn("canonical integer-cubic grid", page)
        self.assertIn("360,000", page)
        self.assertIn("15625", page)
        self.assertIn("−3/4 → 4/3", page)
        self.assertIn("9,720,000", page)
        self.assertIn("A simple 360-grid demo", page)
        self.assertIn("Fig. P3", page)
        self.assertIn("Q=(0,−240)", page)
        self.assertIn("(−270,135)", page)
        self.assertIn("√148", page)
        self.assertIn("±9/8", page)
        self.assertIn("R1=(Q0+2Q1)/3", page)
        self.assertIn("two-parabola S probe", page)

    def test_15625_grid_has_25_integer_cubic_samples(self):
        curves = (
            [(0, 0), (4, -3), (7, -4), (10, 0)],
            [(0, 0), (24, -7), (43, -24), (50, 0)],
            [(0, 0), (3, -4), (6, -7), (30, 0)],
        )
        for points in curves:
            samples = []
            for k in range(1, 26):
                t = Fraction(k, 25)
                u = 1 - t
                x = u**3 * points[0][0] + 3*u*u*t*points[1][0] + 3*u*t*t*points[2][0] + t**3*points[3][0]
                y = u**3 * points[0][1] + 3*u*u*t*points[1][1] + 3*u*t*t*points[2][1] + t**3*points[3][1]
                samples.append((x * 15625, y * 15625))
            self.assertEqual(len(set(samples)), 25)
            self.assertTrue(all(v.denominator == 1 for p in samples for v in p))

    def test_euler_page_no_longer_carries_section_ii(self):
        page = (ROOT / "workbench" / "euler-parabola-fit.html").read_text(
            encoding="utf-8")
        self.assertNotIn("Section II", page)
        self.assertNotIn('id="pyth-canvas"', page)
        self.assertNotIn("__PYTH_", page)


if __name__ == "__main__":
    unittest.main()
