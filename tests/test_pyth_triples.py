import unittest
from pathlib import Path

from curve_lab import pyth_triples

ROOT = Path(__file__).resolve().parents[1]


class PythagoreanFamiliesTest(unittest.TestCase):
    def test_triples_are_exact_and_unique(self):
        points = pyth_triples.base_triples(500)
        self.assertGreater(len(points), 100)
        self.assertTrue(all(
            p["a"] ** 2 + p["b"] ** 2 == p["c"] ** 2 for p in points))
        self.assertEqual(len({(p["a"], p["b"], p["c"]) for p in points}),
                         len(points))

    def test_fixed_n_parabola(self):
        for n in (1, 2, 3):
            for p in pyth_triples.family(n, 3500):
                self.assertAlmostEqual(
                    p["a"], (p["b"] / (2 * n)) ** 2 - n ** 2, places=9)

    def test_selected_n2_sweep_reaches_four_degrees(self):
        chain = pyth_triples.selected_chain(2, 3500, 44.0, 4.0)
        self.assertGreater(len(chain), 30)
        self.assertAlmostEqual(pyth_triples.angle_deg(chain[0]), 43.6028,
                               places=3)
        self.assertAlmostEqual(pyth_triples.angle_deg(chain[-1]), 4.0191,
                               places=3)
        self.assertLess(pyth_triples.angle_deg(chain[-1]),
                        pyth_triples.angle_deg(chain[0]))

    def test_euclid_n_and_m_curves(self):
        for n in (1, 2, 5):
            for a, b in pyth_triples.euclid_n_curve(n, 1000):
                self.assertAlmostEqual(a, (b / (2 * n)) ** 2 - n ** 2,
                                       places=8)
        for m in (2, 5, 10):
            for a, b in pyth_triples.euclid_m_curve(m, 1000):
                self.assertAlmostEqual(b, m * m - a * a / (4 * m * m),
                                       places=8)

    def test_fassler_curve_is_the_reflected_parabola(self):
        curve = pyth_triples.fassler_curve(4, 10)
        self.assertAlmostEqual(dict(curve)[4], 3.0, places=9)
        self.assertAlmostEqual(dict(curve)[8], 0.0, places=9)
        self.assertAlmostEqual(dict(curve)[10], 2.25, places=9)

    def test_page(self):
        page = (ROOT / "workbench" / "pythagorean-families.html").read_text(
            encoding="utf-8")
        self.assertIn("Fig. T1", page)
        self.assertIn("43.60", page)
        self.assertIn("4.02", page)
        self.assertIn("n=2", page)
        self.assertIn("(20,21,29)", page)
        self.assertIn("Fässler", page)
        self.assertIn("N=(b+c)/2", page)
        self.assertIn("1450", page)
        self.assertIn("Fässler N≈1450", page)
        self.assertIn("Euclid n=1..59", page)
        self.assertIn("Euclid m=2..59", page)
        self.assertIn("The 800 band: n=20", page)
        self.assertIn("(41,840,841)", page)
        self.assertIn("87.21", page)
        self.assertIn("39.97", page)
        self.assertIn("From triangles to curves", page)
        self.assertIn("triple tangent chain", page)
        self.assertIn("5,200,000", page)
        self.assertIn("Parabola census", page)
        self.assertIn("2n²", page)
        self.assertIn("n=14→392", page)
        self.assertIn("m²", page)


if __name__ == "__main__":
    unittest.main()
