"""Extend-and-cut: the cut is interior, so the terminal inherits G3.

The tests check the measurements the page claims: the cut lands within 1% of
the curve size, the tangent/curvature/curvature-rate errors are inside their
tolerances, and the split across the cut is G3.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import g3_cut as C  # noqa: E402

PAGE = ROOT / "workbench" / "g3-cut.html"


class TestExtendAndCut(unittest.TestCase):
    def test_two_cuts(self):
        self.assertEqual(len(C.PANELS), 2)

    def test_each_cut_passes(self):
        for p in C.PANELS:
            with self.subTest(curve=p["name"]):
                self.assertTrue(p["ok"], p)
                self.assertLess(p["g3"], 1e-9)
                self.assertLess(p["distance"], 0.01 * p["size"])
                self.assertLess(p["tangent_err"], 1.0)
                self.assertLess(p["kappa_err"], 0.05)
                self.assertLess(p["rate_err"], 0.1)

    def test_the_tail_is_discarded_but_still_measured(self):
        for p in C.PANELS:
            self.assertGreaterEqual(len(p["tail"]), 1)
            self.assertLess(len(p["kept"]), len(p["spans"]))

    def test_the_page(self):
        page = PAGE.read_text(encoding="utf-8")
        self.assertIn("extend, then cut", page.lower())
        self.assertIn("cut deviation", page)
        self.assertIn("G3 across cut", page)
        self.assertIn("discarded tail", page)
        for p in C.PANELS:
            self.assertIn(p["name"], page)

    def test_the_manifest_names_the_page(self):
        manifest = (ROOT / "workbench" / "manifest.json").read_text(
            encoding="utf-8")
        self.assertIn('"g3-cut"', manifest)


if __name__ == "__main__":
    unittest.main()
