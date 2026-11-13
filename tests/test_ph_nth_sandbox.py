"""The eleventh-power page: generated from the checked-in JavaScript."""

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "workbench" / "ph-nth-sandbox.html"
JS = ROOT / "scripts" / "ph_nth_panels.js"


class TestNthSandbox(unittest.TestCase):
    def test_the_page_holds_the_degree_11_sandbox(self):
        page = PAGE.read_text()
        for marker in ("n-controls", "n-plot", "n-bars", "n-close", "n-open",
                       "n-open-value", "n-json", "n-saved", "n-paste",
                       "The eleventh power", "degree 11"):
            with self.subTest(marker=marker):
                self.assertIn(marker, page)

    def test_the_page_inlines_the_checked_in_javascript(self):
        page = PAGE.read_text()
        self.assertIn(JS.read_text().strip()[:200], page)
        self.assertIn("window.recipeMetrics", page)   # the shared maths came along

    def test_the_javascript_parses(self):
        result = subprocess.run(["node", "--check", str(JS)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_the_generator_reproduces_the_page(self):
        before = PAGE.read_text()
        subprocess.run([sys.executable, str(ROOT / "scripts" / "ph_nth_sandbox.py")],
                       check=True, capture_output=True)
        self.assertEqual(PAGE.read_text(), before,
                         "the page is not what scripts/ph_nth_sandbox.py emits")

    def test_the_degree_is_eleven_not_seven(self):
        text = JS.read_text()
        self.assertIn("const SPEED_DEGREE = 5;", text)
        self.assertIn("const DEGREE = 2 * SPEED_DEGREE + 1;", text)


if __name__ == "__main__":
    unittest.main()
