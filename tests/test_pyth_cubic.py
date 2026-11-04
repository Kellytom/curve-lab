import math
import unittest

from curve_lab import pyth_cubic


class PythagoreanCubicTest(unittest.TestCase):
    def test_base_case(self):
        c = pyth_cubic.case(3, 4, 5)
        self.assertEqual(c["p0"], (0, 0))
        self.assertEqual(c["p1"], (3, -4))
        self.assertEqual(c["p2"], (7, 4))
        self.assertEqual(c["p3"], (10, 0))
        self.assertEqual(c["chord"], 10)
        self.assertEqual(c["arm"], 5)
        self.assertAlmostEqual(c["angle"], -53.13010235415598, places=12)
        self.assertTrue(pyth_cubic.checks(c))

    def test_all_cases_are_integer(self):
        for c in pyth_cubic.cases():
            for key in ("p0", "p1", "p2", "p3"):
                self.assertEqual(len(c[key]), 2)
                self.assertTrue(all(isinstance(v, int) for v in c[key]))
            self.assertTrue(pyth_cubic.checks(c))
        self.assertTrue(all(c["p1"] != c["p2"] for c in pyth_cubic.cases()))

    def test_rotation_scale(self):
        c = pyth_cubic.case(3, 4, 5)
        # Rotate by 53.13 degrees (cos=3/5, sin=4/5) and scale by 5.
        pts = pyth_cubic.rotate_scale(
            (c["p0"], c["p1"], c["p2"], c["p3"]), 3 / 5, 4 / 5, 5)
        expected = [(0.0, 0.0), (25.0, 0.0), (5.0, 40.0), (30.0, 40.0)]
        for got, want in zip(pts, expected):
            self.assertAlmostEqual(got[0], want[0], places=9)
            self.assertAlmostEqual(got[1], want[1], places=9)
        # Rotate by 36.87 degrees (cos=4/5, sin=3/5) and scale by 5.
        pts = pyth_cubic.rotate_scale(
            (c["p0"], c["p1"], c["p2"], c["p3"]), 4 / 5, 3 / 5, 5)
        expected = [(0.0, 0.0), (24.0, -7.0), (16.0, 37.0), (40.0, 30.0)]
        for got, want in zip(pts, expected):
            self.assertAlmostEqual(got[0], want[0], places=9)
            self.assertAlmostEqual(got[1], want[1], places=9)

    def test_complement_angles(self):
        a = pyth_cubic.case(3, 4, 5)
        b = pyth_cubic.case(4, 3, 5)
        self.assertAlmostEqual(abs(a["angle"] + b["angle"]), 90.0, places=10)


if __name__ == "__main__":
    unittest.main()
