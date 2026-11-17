"""Every page loads the one shared copy of the panels, not a copy of its own.

The fault this ends: each sandbox page inlined 3,846 lines of
`scripts/ph_nth_panels.js` and 244 of `scripts/ph_math.js`. One edit dirtied a
hundred pages, and a page not rebuilt kept running the old code — which is how a
correct rails control looked dead on 2026-11-16.

The pages now carry `<script src="ph_math.js">` and `<script src="ph_nth_panels.js">`,
and `scripts/build-pages.py` writes one copy of each beside them.
"""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKBENCH = ROOT / "workbench"
SCRIPTS = ROOT / "scripts"

PAGES = (
    "ph-nth-sandbox.html",
    "ph-nth-sandbox-2.html",
    "ph-nth-sandbox-exp.html",
    "ph-11th-sandbox.html",
    "ph-11th-sandbox-2.html",
    "ph-nth-serif-notes.html",
    "ph-11th-serif-notes.html",
    "ph-septic-sandbox.html",
)

PANEL_PAGES = (
    "ph-nth-sandbox.html",
    "ph-nth-sandbox-2.html",
    "ph-nth-sandbox-exp.html",
    "ph-11th-sandbox.html",
    "ph-11th-sandbox-2.html",
    "ph-septic-sandbox.html",
)


class TestPageAssets(unittest.TestCase):
    def test_the_shared_scripts_sit_beside_the_pages(self):
        """A page that loads a missing file draws nothing; build-pages.py writes both."""
        for name in ("ph_math.js", "ph_nth_panels.js"):
            with self.subTest(file=name):
                self.assertEqual((SCRIPTS / name).read_text(), (WORKBENCH / name).read_text())

    def test_every_page_loads_the_math_file(self):
        for name in PAGES:
            with self.subTest(page=name):
                self.assertIn('src="ph_math.js"', (WORKBENCH / name).read_text())

    def test_the_panel_pages_load_the_panels_file(self):
        for name in PANEL_PAGES:
            with self.subTest(page=name):
                self.assertIn('src="ph_nth_panels.js"', (WORKBENCH / name).read_text())

    def test_no_page_inlines_the_panels_again(self):
        """The marker below only appears if a generator starts copying the file in."""
        for name in PAGES:
            text = (WORKBENCH / name).read_text()
            with self.subTest(page=name):
                self.assertNotIn("window.phNthSaved = {", text)

    def test_the_gallery_heading_is_a_stable_anchor(self):
        page = (WORKBENCH / "ph-nth-sandbox-exp.html").read_text()
        self.assertIn('id="n-gallery"', page)


if __name__ == "__main__":
    unittest.main()
