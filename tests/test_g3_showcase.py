"""The G3 showcase: quintic Bezier spans, every join G3.

The page's claim is measured: position, tangent, curvature and curvature-rate
all match at every join. The tests re-derive that from the control points, not
from the page text. The cubic curves collapse to cubics (carried as elevated
quintics); the rest are independent quintic spans.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import g3_showcase as G  # noqa: E402

PAGE = ROOT / "workbench" / "g3-showcase.html"
NOTES = ROOT / "workbench" / "g3-notes.html"


class TestG3Geometry(unittest.TestCase):
    def test_five_curves_and_their_spans(self):
        self.assertEqual(len(G.PANELS), 5)
        by_key = {p["key"]: p for p in G.PANELS}
        self.assertEqual(len(by_key["G3.1"]["spans"]), 8)
        self.assertEqual(len(by_key["G3.2"]["spans"]), 16)
        self.assertEqual(len(by_key["G3.3"]["spans"]), 5)
        self.assertEqual(len(by_key["G3.4"]["spans"]), 8)
        self.assertEqual(len(by_key["G3.5"]["spans"]), 5)

    def test_every_span_is_quintic(self):
        for panel in G.PANELS:
            for P in panel["spans"]:
                with self.subTest(panel=panel["key"]):
                    self.assertEqual(len(P), 6)

    def test_every_join_passes_the_gate(self):
        for panel in G.PANELS:
            for row in G.gate(panel["spans"]):
                with self.subTest(panel=panel["key"], join=row["join"]):
                    self.assertTrue(row["pass"], row)
                    self.assertLess(row["dp"], 1e-9)
                    self.assertLess(row["angle"], 1e-6)
                    self.assertLess(row["dk"], 1e-9)
                    self.assertLess(row["dks"], 1e-9)

    def test_the_worst_join_is_below_the_gate(self):
        worst = max(row["dks"] for p in G.PANELS for row in G.gate(p["spans"]))
        self.assertLess(worst, 1e-9)

    def test_the_bell_is_the_interpolation_that_passes(self):
        bell = next(p for p in G.PANELS if p["key"] == "G3.1")
        self.assertLess(bell["error"], 1.5e-2)
        self.assertTrue(all(row["pass"] for row in G.gate(bell["spans"])))

    def test_the_fit_errors(self):
        by_key = {p["key"]: p for p in G.PANELS}
        self.assertLess(by_key["G3.1"]["error"], 1.5e-2)
        self.assertLess(by_key["G3.2"]["error"], 2.0e-2)
        self.assertLess(by_key["G3.4"]["error"], 1.5e-2)
        self.assertLess(by_key["G3.3"]["error"], 1e-9)
        self.assertLess(by_key["G3.5"]["error"], 1e-9)

    def test_the_lattice_cubic_is_integer_at_6250(self):
        lattice = next(p for p in G.PANELS if p["key"] == "G3.5")
        self.assertTrue(lattice["ints"])
        self.assertEqual(lattice["scale"], 6250)
        for P in lattice["spans"]:
            for p in P:
                for v in p:
                    self.assertAlmostEqual(v * 6250, round(v * 6250), places=6)

    def test_the_ogee_is_integer_at_3125(self):
        ogee = next(p for p in G.PANELS if p["key"] == "G3.3")
        self.assertTrue(ogee["ints"])
        self.assertEqual(ogee["scale"], 3125)


class TestG3Pages(unittest.TestCase):
    def test_showcase_page(self):
        page = PAGE.read_text(encoding="utf-8")
        self.assertIn("quintic", page.lower())
        self.assertIn("Magnify", page)
        self.assertIn("smooth acceleration", page)
        self.assertIn("g3-catalogue.html", page)
        self.assertIn("g3-notes.html", page)
        for key in ("G3.1", "G3.2", "G3.3", "G3.4", "G3.5"):
            self.assertIn(f"Fig. {key}", page)
        self.assertEqual(page.count('<section class="panel">'), 6)

    def test_notes_page_explains_the_circle(self):
        notes = NOTES.read_text(encoding="utf-8")
        self.assertIn("circle", notes.lower())
        self.assertIn("G3", notes)
        self.assertIn("κ = 1/R", notes)
        self.assertIn("dκ/ds = 0", notes)
        self.assertIn("constant", notes.lower())
        self.assertIn("g3-showcase.html", notes)

    def test_the_circle_is_not_a_showcase_panel(self):
        page = PAGE.read_text(encoding="utf-8")
        self.assertNotIn("Fig. G3.N1", page)
        self.assertNotIn("the circle ·", page)


if __name__ == "__main__":
    unittest.main()
