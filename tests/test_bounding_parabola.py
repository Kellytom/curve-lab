import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class BoundingParabolaPageTest(unittest.TestCase):
    def test_page(self):
        page = (ROOT / "workbench" / "bounding-parabola.html").read_text(
            encoding="utf-8")
        self.assertIn('<canvas id="plot"', page)
        self.assertIn("Fig. B1", page)
        self.assertIn("bounding strip", page)
        self.assertIn("hybrid quadratics", page)
        self.assertIn("curve/curve intersection", page)
        self.assertIn("raphlinus.github.io/issues/79", page)


if __name__ == "__main__":
    unittest.main()
