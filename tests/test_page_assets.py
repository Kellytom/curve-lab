"""Every page was rebuilt after the shared JavaScript last changed.

The sandbox pages inline `scripts/ph_math.js` and `scripts/ph_nth_panels.js`, so
an edit to either does nothing until the page is rebuilt. Measured 2026-11-16:
the rails control was reported dead while the source was correct, because the
page in the browser carried a copy from an earlier build.

The copy cannot be compared byte for byte: some generators substitute inside it
on purpose (the exp page sets its own speed degree). So this test compares the
build in time, which is the thing that actually went wrong, and checks that the
newest guard is present in the pages that hold the panels.
"""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKBENCH = ROOT / "workbench"
SHARED = (ROOT / "scripts" / "ph_math.js", ROOT / "scripts" / "ph_nth_panels.js")

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

# Text that only the current panels carry. A page without it is from an older build.
MARKERS = ("const readSaved = () => {", "window.phNthSaved = {", "n-import-list")


class TestPageAssets(unittest.TestCase):
    def test_every_page_is_newer_than_the_shared_javascript(self):
        """A stale page looks like a broken control; run scripts/build-pages.py."""
        newest = max(path.stat().st_mtime for path in SHARED)
        for name in PAGES:
            page = WORKBENCH / name
            with self.subTest(page=name):
                self.assertGreaterEqual(
                    page.stat().st_mtime, newest,
                    f"{name} is older than {', '.join(p.name for p in SHARED)}: rebuild the pages",
                )

    def test_every_page_carries_the_current_guard(self):
        """A page with the B panel must carry the current storage guard and its controls."""
        for name in PAGES:
            text = (WORKBENCH / name).read_text()
            if 'id="n-saved"' not in text:
                continue
            for marker in MARKERS:
                with self.subTest(page=name, marker=marker):
                    self.assertIn(marker, text)

    def test_the_gallery_heading_is_a_stable_anchor(self):
        """The exp page's gallery is found by id, not by its wording."""
        page = (WORKBENCH / "ph-nth-sandbox-exp.html").read_text()
        self.assertIn('id="n-gallery"', page)


if __name__ == "__main__":
    unittest.main()
