import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PlantFormsPageTest(unittest.TestCase):
    def test_page_has_the_proof(self):
        page = (ROOT / "workbench" / "plant-forms.html").read_text(
            encoding="utf-8")
        self.assertEqual(page.count("<svg"), 6)
        self.assertIn("Plant forms", page)
        self.assertIn("Cone terminal", page)
        self.assertIn("Seagrass", page)
        self.assertIn("Flower", page)
        self.assertIn("pyramids on both rails", page)
        self.assertIn("lower branch bigger than upper", page)
        self.assertIn("R = 2 × offset", page)


if __name__ == "__main__":
    unittest.main()
