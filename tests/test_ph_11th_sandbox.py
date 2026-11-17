"""The eleventh-power page: generated from the checked-in JavaScript."""

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests.stamps import without_build_stamp  # noqa: E402
PAGE = ROOT / "workbench" / "ph-11th-sandbox.html"
JS = ROOT / "scripts" / "ph_nth_panels.js"


class Test11thSandbox(unittest.TestCase):
    def test_the_page_holds_the_degree_11_sandbox(self):
        page = PAGE.read_text()
        for marker in ("n-controls", "n-plot", "n-bars", "n-close", "n-open",
                       "n-open-value", "n-json", "n-saved", "n-paste",
                       "n-rotate", "n-rails", "n-character", "n-char-l", "n-char-r", "n-prof", "n-shear", "n-hook", "n-hook-y", "n-terminal-start", "n-terminal-end", "n-d", "n-rename",
                       "ph-11th-serif-notes.html", "n-gallery", "phNthGallery", "integer-105", "integer-70",
                       "The eleventh power", "degree 11"):
            with self.subTest(marker=marker):
                self.assertIn(marker, page)

    def test_the_page_loads_the_checked_in_javascript(self):
        """The page loads the shared file; it does not inline a copy of its own."""
        page = PAGE.read_text()
        self.assertIn('src="ph_nth_panels.js"', page)
        self.assertIn('src="ph_math.js"', page)
        self.assertNotIn("window.phNthSaved = {", page)

    def test_the_seeds_travel_with_the_panels_file(self):
        """Seed names live in the shared file now, so the page cannot carry them."""
        panels = JS.read_text()
        for marker in ("euler-hook", "amper"):
            with self.subTest(marker=marker):
                self.assertIn(marker, panels)

    def test_the_javascript_parses(self):
        result = subprocess.run(["node", "--check", str(JS)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_the_generator_reproduces_the_page(self):
        before = PAGE.read_text()
        subprocess.run([sys.executable, str(ROOT / "scripts" / "ph_11th_sandbox.py")],
                       check=True, capture_output=True)
        self.assertEqual(without_build_stamp(PAGE.read_text()),
                         without_build_stamp(before),
                         "the page is not what scripts/ph_11th_sandbox.py emits")

    def test_the_serif_notes_page_is_generated_too(self):
        notes = ROOT / "workbench" / "ph-11th-serif-notes.html"
        self.assertTrue(notes.exists())
        text = notes.read_text()
        for marker in ("appendixOf", "residual", "ph-11th-sandbox.html", "window.polynomialValue"):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_the_degree_is_eleven_not_seven(self):
        text = JS.read_text()
        self.assertIn("let speedDegree = Number.isFinite(asked) && asked >= 1 ? Math.round(asked) : 5;", text)
        self.assertIn("const positionDegree = () => 2 * speedDegree + 1;", text)


if __name__ == "__main__":
    unittest.main()
