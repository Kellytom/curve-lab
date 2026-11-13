"""Part 2: the same sandbox over fitted showcase curves."""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "workbench" / "ph-nth-sandbox-2.html"
FITTED = ROOT / "workbench" / "ph-fitted-curves.json"


class TestNthSandbox2(unittest.TestCase):
    def test_the_fitted_table_exists_and_is_honest(self):
        document = json.loads(FITTED.read_text())
        curves = document["curves"]
        self.assertGreaterEqual(len(curves), 40)
        for curve in curves:
            self.assertEqual(len(curve["speedX"]), 6)
            self.assertEqual(len(curve["speedY"]), 6)
            self.assertTrue(curve["from"].startswith("fitted"))
            self.assertLessEqual(float(curve["from"].split()[-1]), 0.03)

    def test_the_page_carries_the_fitted_gallery(self):
        page = PAGE.read_text()
        for marker in ("phNthGallery", "n-gallery", "Part 2: fitted curves",
                       "fitted", "n-controls", "n-plot"):
            with self.subTest(marker=marker):
                self.assertIn(marker, page)
        self.assertNotIn("__GALLERY__", page)

    def test_the_page_is_generated(self):
        import subprocess
        import sys
        before = PAGE.read_text()
        subprocess.run([sys.executable, str(ROOT / "scripts" / "ph_nth_sandbox2.py")],
                       check=True, capture_output=True)
        self.assertEqual(PAGE.read_text(), before)


if __name__ == "__main__":
    unittest.main()
