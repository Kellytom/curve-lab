"""Guards the grid-explained page: box, ruler, placement kept apart."""

import math
import unittest
from pathlib import Path

from curve_lab import spine

ROOT = Path(__file__).resolve().parents[1]


class GridExplainedTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pkg = spine.load()
        cls.tri = pkg.thinnest(3125)
        cls.ch = pkg.Spiral(cls.tri, 1)
        cls.ch.extend([1] * 186)
        cls.page = (ROOT / "workbench" / "grid-explained.html").read_text(
            encoding="utf-8")

    def test_the_box_is_not_the_path(self):
        pts = self.ch.floats()
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        self.assertAlmostEqual(max(xs) - min(xs), 79.0, delta=1.0)
        self.assertAlmostEqual(max(ys) - min(ys), 79.0, delta=1.0)
        self.assertEqual(len(self.ch.turns), 186)
        self.assertIn("box 79 × 79", self.page)
        self.assertIn("turning points", self.page)

    def test_three_numbers_are_named(self):
        self.assertIn("denominator is the ruler", self.page.lower())
        self.assertIn("217", self.page)
        self.assertIn("3125", self.page)
        self.assertIn("placement grid", self.page)
        self.assertIn("not the path", self.page)

    def test_exactness_and_angle(self):
        self.assertIn("cosine", self.page)
        self.assertIn("exact", self.page.lower())
        self.assertIn("52/25", self.page)


if __name__ == "__main__":
    unittest.main()
