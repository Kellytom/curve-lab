import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ModulatedWidthPageTest(unittest.TestCase):
    def test_page(self):
        page = (ROOT / "workbench" / "modulated-width.html").read_text(
            encoding="utf-8")
        self.assertEqual(page.count("<svg"), 3)
        self.assertIn("Modulated width", page)
        self.assertIn("w(u) = w0", page)
        self.assertIn("not equidistant", page)
        self.assertIn("stage-four.html", page)
        self.assertIn("stem-library-offset.html", page)


if __name__ == "__main__":
    unittest.main()
