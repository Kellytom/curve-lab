"""The preserved quintic page: Quintic Béziers every join G3.

This is the copy of the original G3 showcase. It keeps the bell, log spiral,
sine and the two cubic-collapse panels, but every non-cubic curve is carried
as six-point quintic spans.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import quintic_showcase as Q  # noqa: E402

PAGE = ROOT / "workbench" / "quintic-showcase.html"


class TestQuinticGeometry(unittest.TestCase):
    def test_five_curves_and_their_span_counts(self):
        self.assertEqual(len(Q.PANELS), 5)
        by_key = {p["key"]: p for p in Q.PANELS}
        self.assertEqual(len(by_key["G3.1"]["spans"]), 8)
        self.assertEqual(len(by_key["G3.2"]["spans"]), 16)
        self.assertEqual(len(by_key["G3.3"]["spans"]), 5)
        self.assertEqual(len(by_key["G3.4"]["spans"]), 8)
        self.assertEqual(len(by_key["G3.5"]["spans"]), 5)

    def test_every_span_is_quintic(self):
        for panel in Q.PANELS:
            for P in panel["spans"]:
                with self.subTest(panel=panel["key"]):
                    self.assertEqual(len(P), 6)

    def test_every_join_passes(self):
        for panel in Q.PANELS:
            for row in Q.gate(panel["spans"]):
                with self.subTest(panel=panel["key"], join=row["join"]):
                    self.assertTrue(row["pass"], row)
                    self.assertLess(row["dks"], 1e-9)

    def test_the_errors_and_integer_scales(self):
        by_key = {p["key"]: p for p in Q.PANELS}
        self.assertLess(by_key["G3.1"]["error"], 1.5e-2)
        self.assertLess(by_key["G3.2"]["error"], 2.0e-2)
        self.assertLess(by_key["G3.4"]["error"], 1.5e-2)
        self.assertLess(by_key["G3.3"]["error"], 1e-9)
        self.assertLess(by_key["G3.5"]["error"], 1e-9)
        self.assertEqual(by_key["G3.3"]["scale"], 3125)
        self.assertEqual(by_key["G3.5"]["scale"], 6250)
        self.assertTrue(by_key["G3.3"]["ints"])
        self.assertTrue(by_key["G3.5"]["ints"])


class TestQuinticPage(unittest.TestCase):
    def test_page(self):
        page = PAGE.read_text(encoding="utf-8")
        self.assertIn("Quintic Béziers every join G3", page)
        self.assertIn("quintic", page.lower())
        self.assertIn("Magnify", page)
        self.assertIn("smooth acceleration", page)
        self.assertIn("g3-showcase.html", page)
        for key in ("G3.1", "G3.2", "G3.3", "G3.4", "G3.5"):
            self.assertIn(f"Fig. {key}", page)

    def test_the_manifest_names_the_page(self):
        manifest = (ROOT / "workbench" / "manifest.json").read_text(
            encoding="utf-8")
        self.assertIn('"quintic-showcase"', manifest)


if __name__ == "__main__":
    unittest.main()
