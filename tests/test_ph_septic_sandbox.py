"""The septic sandbox: both panels, generated from the checked-in JavaScript."""

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "workbench" / "ph-septic-sandbox.html"
JS = ROOT / "scripts" / "ph_septic_panels.js"


class TestSepticSandbox(unittest.TestCase):
    def test_the_page_exists_and_holds_both_panels(self):
        page = PAGE.read_text()
        for marker in ("a-controls", "a-plot", "b-controls", "b-plot",
                       "the general polynomial", "the PH septic"):
            with self.subTest(marker=marker):
                self.assertIn(marker, page)

    def test_the_page_inlines_the_checked_in_javascript(self):
        page = PAGE.read_text()
        self.assertIn(JS.read_text().strip()[:200], page)

    def test_the_javascript_parses(self):
        result = subprocess.run(["node", "--check", str(JS)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_the_build_pipeline_keeps_both_panels(self):
        """generator, then the hub bar; the panels survive both."""
        subprocess.run([sys.executable, str(ROOT / "scripts" / "ph_septic_sandbox.py")],
                       check=True, capture_output=True)
        subprocess.run([sys.executable, str(ROOT / "scripts" / "hub.py")],
                       check=True, capture_output=True)
        page = PAGE.read_text()
        for marker in ("a-controls", "b-controls", "all inputs"):
            with self.subTest(marker=marker):
                self.assertIn(marker, page)


if __name__ == "__main__":
    unittest.main()
