import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EulerParabolaFitPageTest(unittest.TestCase):
    def test_page(self):
        page = (ROOT / "workbench" / "euler-parabola-fit.html").read_text(
            encoding="utf-8")
        self.assertIn('<canvas id="editor"', page)
        self.assertIn("Fig. E1", page)
        self.assertIn("Fig. E2", page)
        self.assertIn("Fig. E3", page)
        self.assertIn("current cubic seam", page)
        self.assertIn("asymptotic slope", page)
        self.assertIn("kurbo PR #169", page)
        self.assertIn('id="offset-d"', page)
        self.assertIn("dense normal offsets", page)
        self.assertIn('id="show-target"', page)
        self.assertIn("true Euler segment through the current endpoints", page)


if __name__ == "__main__":
    unittest.main()
