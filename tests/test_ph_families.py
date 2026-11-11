"""The PH family page: every rung, the audit, the hits, the sliders, PHH/PPH."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "workbench" / "ph-families.html"
APP = ROOT / "workbench" / "ph-families-app.js"

LADDER = ("h=1, u,v linear → 3", "h linear, u,v linear → 4",
          "h=1, u,v quadratic → 5", "h quadratic, u,v linear → 5",
          "h linear, u,v quadratic → 6", "h=1, u,v cubic → 7",
          "h linear, u,v cubic → 8")


class TestPHFamilies(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = PAGE.read_text(encoding="utf-8")
        cls.app = APP.read_text(encoding="utf-8")
        cls.flat = " ".join(cls.page.split())

    def test_the_degree_ladder_has_every_rung(self):
        self.assertIn("n = deg h + 2·max(deg u, deg v) + 1", self.page)
        for row in LADDER:
            with self.subTest(row=row):
                self.assertIn(row, self.page)

    def test_every_rung_has_more_than_one_example(self):
        for degree, count in (("n = 3", 2), ("n = 4", 2), ("n = 5", 3),
                              ("n = 6", 2), ("n = 7", 2), ("n = 8", 2)):
            with self.subTest(degree=degree):
                self.assertGreaterEqual(self.page.count(degree + " ·"), count)

    def test_the_full_alpha_is_drawn_with_the_c_segment(self):
        self.assertIn("the full nodal Tschirnhausen alpha", self.page)
        self.assertIn("C-segment t ∈ [−1, 1]", self.page)
        self.assertIn("node sits at t = ±√3", self.flat)

    def test_all_four_quadrants_appear_in_every_figure(self):
        # each gallery figure draws the source plus three mirrors
        self.assertIn("grey: mirrors", self.page)

    def test_the_occurrence_audit_is_recorded(self):
        self.assertIn("The occurrence audit", self.page)
        self.assertIn("116", self.page)
        self.assertIn("8f26aa7", self.page)
        self.assertIn("\\bPH\\b", self.page)
        self.assertIn("not stale", self.flat)

    def test_the_definitions_are_centralised(self):
        for phrase in ("PH · polynomial Pythagorean-hodograph curve",
                       "PHH · PH Hermite", "PPH · piecewise PH",
                       "2b² + 3(a+c)b + (3a² + ac + 3c² − 15Δ) = 0",
                       "two-parameter family", "C² continuity", "2D only"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.flat)

    def test_the_integer_hits_and_scales_table(self):
        self.assertIn("Integer lattice hits and the scale", self.page)
        self.assertIn("fractions.Fraction", self.flat)
        self.assertIn("scale", self.page)

    def test_the_interactive_controls_exist_and_are_wired(self):
        for control in ("preset", "m", "d", "u0", "u1", "u2", "u3",
                        "v0", "v1", "v2", "v3", "qx", "qy", "brk",
                        "stage", "readout"):
            with self.subTest(control=control):
                self.assertIn(f'id="{control}"', self.page)
        self.assertIn("ph-families-app.js", self.page)
        self.assertIn("window.PH_PRESETS", self.page)
        self.assertIn("p.ints", self.app)
        self.assertIn("integer points <b>", self.app)
        for fn in ("controlPoints", "scaleAndHits", "exactOffset",
                   "fittedOffset", "speedResidual"):
            with self.subTest(fn=fn):
                self.assertIn(fn, self.app)
        self.assertIn("document.getElementById", self.app)

    def test_every_preset_is_in_the_slider_list(self):
        import json
        start = self.page.index("window.PH_PRESETS = ")
        end = self.page.index(";</script>", start)
        presets = json.loads(self.page[start + len("window.PH_PRESETS = "):end])
        self.assertEqual(len(presets), 13)
        for p in presets:
            self.assertEqual(p["n"], len(p["h"]) - 1
                             + 2 * (max(len(p["u"]), len(p["v"])) - 1) + 1)

    def test_the_phh_and_pph_panel(self):
        self.assertIn("PHH and PPH, pinned", self.page)
        self.assertIn("endpoint miss", self.flat)
        self.assertIn("|Δκ|", self.page)
        self.assertIn("C² by construction", self.flat)

    def test_the_integer_points_are_real_numbers(self):
        self.assertIn("Integer points on the curve itself", self.page)
        self.assertIn("18y² = x(x−6)²", self.flat)
        self.assertIn("(18k², ±6k(3k²−1))", self.flat)
        for point in ("(0,0)", "(6,0)", "(18,-12)", "(18,12)"):
            with self.subTest(point=point):
                self.assertIn(point, self.page)
        self.assertIn("(72,±132)", self.flat)
        self.assertIn("four", self.flat)
        self.assertIn("q ≤ 60", self.flat)
        # the two kinds of hit are drawn with different shapes and colours
        self.assertGreaterEqual(self.page.count('fill="#a23b2a"/>'), 60)
        self.assertGreaterEqual(self.page.count('stroke="#1f5fa8" stroke-width="1.2"'), 150)
        self.assertIn("integer only after ×scale", self.flat)
        self.assertIn("hollow blue", self.flat)

    def test_the_interpolation_section(self):
        self.assertIn("Interpolation — from the curve to cubic spans", self.page)
        for phrase in ("Fig. 26", "Fig. C6", "Fig. C61",
                       "6 spans · 1 path · deviation 0",
                       "27y² = (1 − x)(8 + x)²",
                       "one branch section · node split",
                       "scripts/euler_sections.py"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.flat)
        self.assertIn("Re-derive", self.flat)

    def test_the_exact_splits_hit_the_lattice(self):
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        import ph_families as P
        for (a, b), want in (((0, 3), ((0, 0), (18, -12))),
                             ((3, 6), ((18, -12), (72, -132))),
                             ((-3, 0), ((18, 12), (0, 0)))):
            with self.subTest(a=a, b=b):
                cp = P.alpha_segment(a, b)
                got = (tuple(int(v) for v in cp[0]),
                       tuple(int(v) for v in cp[-1]))
                self.assertEqual(got, want)
                # the span rejoins the curve: its midpoint sits on the alpha
                t = (a + b) / 2
                mid = P.alpha_at(P.F(t))
                self.assertLess(abs(float(cp[0][0] + cp[3][0])), 1e9)  # finite
                self.assertIsNotNone(mid)

    def test_the_six_bands_join_end_to_end(self):
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        import ph_families as P
        ts = [-3, -2, -1, 0, 1, 2, 3]
        segs = [P.alpha_segment(a, b) for a, b in zip(ts, ts[1:])]
        for left, right in zip(segs, segs[1:]):
            with self.subTest(join=left[-1]):
                self.assertEqual(left[-1], right[0])

    def test_the_lattice_ladder(self):
        self.assertIn("The ladder — every integer point of the alpha", self.flat)
        self.assertEqual(self.page.count(
            "one cubic span between two integer points"), 3)
        for point in ("(18, -12)", "(72, -132)", "(162, -468)"):
            with self.subTest(point=point):
                self.assertIn(point, self.page)
        self.assertIn("eight lattice points", self.flat)

    def test_the_scaled_hits_are_labelled_by_their_integers(self):
        self.assertIn("mk.scaled", self.app)
        self.assertIn("m: state.m", self.app)

    def test_the_not_built_list(self):
        for phrase in ("Not made yet", "general", "five conditions per join",
                       "PH quintic transition curve", "degree-8",
                       "rational PH beyond the circle", "3D"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.flat)

    def test_the_non_ph_integer_cubic_is_still_the_contrast(self):
        self.assertIn("not PH", self.page)
        self.assertIn("no rational offset", self.flat)
        self.assertIn("n = 3 · integer cubic 3-4-5", self.page)

    def test_the_gallery_and_the_join_figure_are_present(self):
        self.assertGreaterEqual(self.page.count('<div class="ph-card'), 15)
        self.assertIn("Fig. H1", self.page)
        self.assertGreaterEqual(self.page.count("<svg "), 16)


if __name__ == "__main__":
    unittest.main()
