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

    def test_every_span_keeps_the_interior_speed_floor(self):
        import g3_catalogue as C
        for panel in G.PANELS:
            prob = C.problem_of_spans(panel["spans"])
            with self.subTest(panel=panel["key"]):
                self.assertGreaterEqual(prob["ratio"], 0.10)

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
        for n in range(1, 7):
            self.assertIn(f"Fig. {n} ·", page)
        self.assertEqual(page.count('<section class="panel"'), 182)
        self.assertIn("The finished curve · what can be handed over", page)
        self.assertIn("G3-complete", page)
        self.assertIn("smooth handover", page)
        self.assertIn('class="badge"', page)
        self.assertIn("g3-handover.html", page)
        self.assertIn("Quintic-required · 5", page)
        self.assertGreaterEqual(page.count("quintic-required"), 5)
        self.assertIn("Every complete curve · 166", page)
        self.assertIn("Tightest-span diagnostics", page)
        self.assertIn("slope P0P1", page)
        self.assertIn("Control points and handle vectors are integers", page)
        self.assertNotIn("|Δp|", page)
        self.assertEqual(page.count("Fig. H · "), 0)
        self.assertIn("Fig. 18 ·", page)
        self.assertIn("Fig. 183 ·", page)
        self.assertNotIn("From the original showcase", page)
        self.assertNotIn("C2 cubic spline", page)
        self.assertNotIn("Catmull–Rom", page)
        self.assertEqual(page.count(">ground<"), 183)
        self.assertEqual(page.count('class="panel-grid"'), 183)
        self.assertEqual(page.count("1 · G3 acceleration"), 183)
        self.assertEqual(page.count("G3 acceleration · dκ/ds"), 13)
        self.assertEqual(page.count("dκ/ds · cusp / failing join"), 4)
        self.assertEqual(page.count("integer cubics ×625"), 5)
        self.assertGreaterEqual(page.count("G3 interpolation"), 12)
        self.assertIn("Cusp curves · allowed with a declared cusp", page)
        self.assertIn("Still failing · deviation", page)
        for key in ("astroid", "deltoid", "heart · Beutel lower", "squircle"):
            self.assertIn(key, page)

    def test_notes_page_still_explains_the_circle(self):
        notes = NOTES.read_text(encoding="utf-8")
        self.assertIn("circle", notes.lower())
        self.assertIn("κ = 1/R", notes)
        self.assertIn("dκ/ds = 0", notes)
        self.assertIn("quintic-showcase.html", notes)

    def test_notes_page_carries_the_six_curves_and_error_tables(self):
        notes = NOTES.read_text(encoding="utf-8")
        self.assertIn("The six panels, with their error tables", notes)
        self.assertGreaterEqual(notes.count("|Δp|"), 6)
        for n in range(1, 7):
            self.assertIn(f"Fig. {n} ·", notes)


if __name__ == "__main__":
    unittest.main()
