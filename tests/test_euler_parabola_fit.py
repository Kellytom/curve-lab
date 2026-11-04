import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EulerParabolaFitPageTest(unittest.TestCase):
    def test_page(self):
        page = (ROOT / "workbench" / "euler-parabola-fit.html").read_text(
            encoding="utf-8")
        self.assertIn('<canvas id="editor" width="1440" height="780"', page)
        self.assertIn("fine quarter-unit grid", page)
        self.assertIn("Fig. E1", page)
        self.assertIn("Fig. E2", page)
        self.assertIn("Fig. E3", page)
        self.assertIn("Fig. E4", page)
        self.assertIn("Second example", page)
        self.assertIn("two spans", page)
        self.assertIn("two-piece control points", page)
        self.assertIn("control + handles", page)
        self.assertIn("current cubic seam", page)
        self.assertIn("asymptotic slope", page)
        self.assertIn("kurbo PR #169", page)
        self.assertIn('id="offset-d"', page)
        self.assertIn("dense normal offsets", page)
        self.assertIn('id="show-target"', page)
        self.assertIn('id="snap-int"', page)
        self.assertIn('id="preset-345"', page)
        self.assertIn('id="preset-345-handles"', page)
        self.assertIn('id="free-handles"', page)
        self.assertIn('id="snap-handles"', page)
        self.assertIn("12u = 4", page)
        self.assertIn('id="save-state"', page)
        self.assertIn('id="save-json"', page)
        self.assertIn("6-8-10 chord", page)
        self.assertIn("true Euler segment through the current endpoints", page)


if __name__ == "__main__":
    unittest.main()
