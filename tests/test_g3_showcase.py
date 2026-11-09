"""The cubic G3 showcase: four-point spans only, every join G3.

Every panel is one cubic (or one cubic cut into pieces). The quintic G3
representation collapses to a cubic, which is what Inkscape and the glyph
pipeline need. The tests pin the four-point spans and the integer scale.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import g3_showcase as G  # noqa: E402

PAGE = ROOT / "workbench" / "g3-showcase.html"
NOTES = ROOT / "workbench" / "g3-notes.html"


class TestCubicGeometry(unittest.TestCase):
    def test_six_cubics_and_their_spans(self):
        self.assertEqual(len(G.PANELS), 6)
        for panel in G.PANELS:
            with self.subTest(panel=panel["key"]):
                self.assertEqual(len(panel["spans"]),
                                 8 if panel["key"] == "G3.6" else 5)
                self.assertEqual(len(G.gate(panel["spans"])),
                                 len(panel["spans"]) - 1)
                self.assertEqual(len(panel["spans"][0]), 4)

    def test_every_join_passes_and_is_exact(self):
        for panel in G.PANELS:
            for row in G.gate(panel["spans"]):
                with self.subTest(panel=panel["key"], join=row["join"]):
                    self.assertTrue(row["pass"], row)
                    self.assertLess(row["dp"], 1e-9)
                    self.assertLess(row["angle"], 1e-6)
                    self.assertLess(row["dk"], 1e-9)
                    self.assertLess(row["dks"], 1e-9)
            if panel["key"] == "G3.6":
                self.assertLess(panel["error"], 1e-5)
            else:
                self.assertLess(panel["error"], 1e-9)

    def test_the_integer_panels_are_integer_at_625(self):
        for panel in G.PANELS:
            if panel["key"] == "G3.6":
                self.assertFalse(panel["ints"])
                continue
            self.assertTrue(panel["ints"], panel["key"])
            self.assertEqual(panel["scale"], 625)
            for P in panel["spans"]:
                for p in P:
                    for v in p:
                        self.assertAlmostEqual(v * 625, round(v * 625), places=6)

    def test_the_comparison_curves_come_from_the_showcase(self):
        panels = G.showcase_comparison_panels()
        self.assertEqual([p["name"].split(" ·")[0] for p in panels],
                         ["bow", "strophoid", "bernoulli"])
        for p in panels:
            self.assertTrue(p["seam"])
            self.assertGreater(p["g3"], 1.0)
            seam = [r for r in p["rows"] if r["join"] == "seam"][0]
            self.assertFalse(seam["pass"])
            self.assertGreater(seam["dks"], 1.0)

    def test_the_acceleration_graph_fills_its_box(self):
        import re
        panel = next(p for p in G.PANELS if p["key"] == "G3.5")
        svg = G.acceleration_svg(panel)
        d = re.search(r'<path d="([^"]+)"', svg).group(1)
        xs = [float(m[0]) for m in re.findall(r'([\d.]+),([\d.]+)', d)]
        self.assertGreater(max(xs) - min(xs), 250)

    def test_the_spans_are_cubics_not_quintics(self):
        for panel in G.PANELS:
            for P in panel["spans"]:
                self.assertEqual(len(P), 4)


class TestCubicPages(unittest.TestCase):
    def test_showcase_page(self):
        page = PAGE.read_text(encoding="utf-8")
        self.assertIn("Cubic Béziers, every join G3", page)
        self.assertIn("collapses to a cubic", page)
        self.assertIn("quintic-showcase.html", page)
        self.assertIn("g3-catalogue.html", page)
        for key in ("G3.1", "G3.2", "G3.3", "G3.4", "G3.5", "G3.6"):
            self.assertIn(f"Fig. {key}", page)
        self.assertEqual(page.count('<section class="panel">'), 8)
        self.assertEqual(page.count("From the original showcase · still outside G3"), 1)
        self.assertIn("Catalogue progress", page)
        self.assertNotIn("C2 cubic spline", page)
        self.assertNotIn("Catmull–Rom", page)
        self.assertEqual(page.count(">ground<"), 9)
        self.assertEqual(page.count('class="panel-grid"'), 9)
        self.assertEqual(page.count("G3 acceleration · dκ/ds"), 6)
        self.assertEqual(page.count("integer cubics ×625"), 5)
        self.assertEqual(page.count("G3 interpolation"), 6)

    def test_notes_page_still_explains_the_circle(self):
        notes = NOTES.read_text(encoding="utf-8")
        self.assertIn("circle", notes.lower())
        self.assertIn("κ = 1/R", notes)
        self.assertIn("dκ/ds = 0", notes)
        self.assertIn("quintic-showcase.html", notes)


if __name__ == "__main__":
    unittest.main()
