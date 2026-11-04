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


if __name__ == "__main__":
    unittest.main()
