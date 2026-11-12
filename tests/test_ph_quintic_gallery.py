"""The gallery of 48 PH quintics: S and C, exact pitches and endpoints."""

import sys
import unittest
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ph_quintic_gallery as G  # noqa: E402


class TestGallery(unittest.TestCase):
    def test_the_count_and_the_split(self):
        self.assertEqual(len(G.CASES), 48)
        self.assertEqual(len(G.S_CASES), 24)
        self.assertEqual(len(G.C_CASES), 24)

    def test_every_s_case_has_an_interior_inflection(self):
        for u, v in G.S_CASES:
            infl, pitch, end, swing = G.s_info(u, v)
            with self.subTest(u=u, v=v):
                self.assertIsNotNone(infl)
                self.assertGreater(infl, 0.0)
                self.assertLess(infl, 1.0)

    def test_every_c_case_is_one_sided(self):
        for u, v in G.C_CASES:
            with self.subTest(u=u, v=v):
                self.assertEqual(G.shape(u, v), "C")

    def test_the_endpoints_are_whole_at_the_pitch(self):
        for u, v in G.CASES:
            infl, pitch, end, swing = G.s_info(u, v)
            with self.subTest(u=u, v=v):
                self.assertEqual((end[0] * pitch).denominator, 1)
                self.assertEqual((end[1] * pitch).denominator, 1)

    def test_the_pitch_is_the_lcm_of_the_integrated_denominators(self):
        for u, v in G.CASES[:10]:
            infl, pitch, end, swing = G.s_info(u, v)
            x, y = G.uv_curve(u, v)
            from math import lcm
            want = 1
            for c in x + y:
                want = lcm(want, c.denominator)
            self.assertEqual(pitch, want)

    def test_the_s_set_is_on_the_page_below_g1(self):
        page = (ROOT / "workbench" / "ph-quintic-gallery.html").read_text()
        self.assertIn("Fig. Q2", page)
        self.assertIn("the S curves, enlarged", page)
        self.assertGreater(page.index("Fig. Q2"), page.index("Fig. Q1"))

    def test_q3_is_the_dramatic_set(self):
        self.assertEqual(len(G.Q3_CASES), 12)
        for u, v in G.Q3_CASES:
            infl, pitch, end, swing = G.s_info(u, v)
            th = G.theta_curve(u, v)
            k = min(len(th) - 1, max(0, round(infl * (len(th) - 1))))
            s0 = abs(th[k] - th[0])
            s1 = abs(th[-1] - th[k])
            with self.subTest(u=u, v=v):
                self.assertGreaterEqual(min(s0, s1), 45)

    def test_q4_curls_or_turns(self):
        self.assertEqual(len(G.Q4_CASES), 12)
        for u, v in G.Q4_CASES:
            th = G.theta_curve(u, v)
            with self.subTest(u=u, v=v):
                self.assertGreaterEqual(max(th) - min(th), 120)

    def test_q5_has_the_inflection_in_the_middle(self):
        self.assertEqual(len(G.Q5_CASES), 28)
        for u, v in G.Q5_CASES:
            infl, pitch, end, swing = G.s_info(u, v)
            with self.subTest(u=u, v=v):
                self.assertIsNotNone(infl)
                self.assertGreater(infl, 0.44)
                self.assertLess(infl, 0.56)

    def test_q6_is_balanced(self):
        self.assertEqual(len(G.Q6_CASES), 16)
        for u, v in G.Q6_CASES:
            infl, pitch, end, swing = G.s_info(u, v)
            th = G.theta_curve(u, v)
            k = min(len(th) - 1, max(0, round(infl * (len(th) - 1))))
            s0 = abs(th[k] - th[0])
            s1 = abs(th[-1] - th[k])
            with self.subTest(u=u, v=v):
                self.assertGreater(infl, 0.47)
                self.assertLess(infl, 0.53)
                self.assertGreaterEqual(min(s0, s1), 40)
                self.assertLessEqual(abs(s0 - s1), max(4.0, 0.12 * max(s0, s1)))

    def test_q6b_is_exactly_balanced(self):
        self.assertEqual(len(G.Q6B_CASES), 12)
        for u, v in G.Q6B_CASES:
            infl, pitch, end, swing = G.s_info(u, v)
            th = G.theta_curve(u, v)
            k = len(th) // 2
            s0 = abs(th[k] - th[0])
            s1 = abs(th[-1] - th[k])
            with self.subTest(u=u, v=v):
                self.assertAlmostEqual(infl, 0.5, places=9)
                self.assertAlmostEqual(s0, s1, places=6)

    def test_the_slider_panel_is_wired(self):
        page = (ROOT / "workbench" / "ph-quintic-gallery.html").read_text()
        self.assertIn('id="q7-scale-b"', page)
        self.assertIn('id="q7-shift-a"', page)
        self.assertIn('id="q7-plot"', page)
        self.assertIn('id="q7-morph-lambda"', page)
        self.assertIn("bend", page)
        self.assertIn("Math.atan2", page)

    def test_q8_playground_is_wired_and_its_defaults_are_the_target(self):
        page = (ROOT / "workbench" / "ph-quintic-gallery.html").read_text()
        for id_ in ("q8-speed-x0", "q8-speed-x1", "q8-speed-x2",
                    "q8-speed-y0", "q8-speed-y1", "q8-speed-y2",
                    "q8-plot", "q8-readout", "q8-closed-form"):
            self.assertIn(f'id="{id_}"', page)
        self.assertIn("pitch", page)
        # the default recipe is the simplified curve 15, pitch 1500
        infl, pitch, end, swing = G.s_info((F(1, 5), -2, 2), (F(2, 5), F(-3, 2), F(8, 5)))
        self.assertEqual(pitch, 1500)
        # the Q7 starting recipe, c = 1, is free on the grid
        infl, pitch, end, swing = G.s_info((1, 0, 0), (1, -4, 4))
        self.assertEqual(pitch, 15)

    def test_the_bend_two_proposals_are_wired(self):
        page = (ROOT / "workbench" / "ph-quintic-gallery.html").read_text()
        for tag in ("Fig. Q9", "Fig. Q10", "Fig. Q11"):
            self.assertIn(tag, page)
        for host in ("q9-controls", "q9-plot", "q9-readout",
                     "q10-controls", "q10-plot", "q10-readout",
                     "q11-controls", "q11-plot", "q11-readout"):
            self.assertIn(f'id="{host}"', page)
        self.assertIn("buildRecipePanel(", page)
        self.assertIn("lineSlope", page)
        self.assertIn("lineIntercept", page)
        self.assertIn("closedFormOf", page)

        def bend(u, v):
            pts = G.uv_samples(u, v, 400)
            arc = sum(((b[1] - a[1]) ** 2 + (b[2] - a[2]) ** 2) ** 0.5
                      for a, b in zip(pts, pts[1:]))
            chord = ((pts[-1][1] - pts[0][1]) ** 2 + (pts[-1][2] - pts[0][2]) ** 2) ** 0.5
            return arc / chord

        # Q9: v = 4u - 6
        infl, pitch, end, swing = G.s_info((2, -3, 3), (2, -12, 12))
        self.assertEqual(pitch, 10)
        self.assertAlmostEqual(bend((2, -3, 3), (2, -12, 12)), 2.0, delta=0.02)
        # Q10 landmarks
        infl, pitch, end, swing = G.s_info((F(1, 2), F(-1, 2), F(1, 2)),
                                           (F(39, 50), -4, 4))
        self.assertEqual(pitch, 15000)
        self.assertAlmostEqual(bend((F(1, 2), F(-1, 2), F(1, 2)),
                                    (F(39, 50), -4, 4)), 2.01, delta=0.02)
        # Q11: the 2.04 find, and its x10 form at pitch 2
        infl, pitch, end, swing = G.s_info((5, -5, 5), (7, -40, 40))
        self.assertEqual(pitch, 2)
        self.assertAlmostEqual(bend((5, -5, 5), (7, -40, 40)), 2.69, delta=0.02)

    def test_the_page_and_data_are_keyboard_ascii(self):
        """Every variable is searchable: no Greek, no typographic glyphs."""
        for name in ("workbench/ph-quintic-gallery.html",
                     "workbench/ph-quintic-presets.json",
                     "workbench/ph-quintic-presets.svg"):
            text = (ROOT / name).read_text()
            bad = sorted({ch for ch in text if ord(ch) > 127})
            with self.subTest(file=name):
                self.assertEqual(bad, [], f"{name} has non-ASCII: {bad}")

    def test_the_variable_names_are_on_the_page(self):
        page = (ROOT / "workbench" / "ph-quintic-gallery.html").read_text()
        for name in ("curvatureAngle", "curvatureRatio", "morphLambda",
                     "speedMid", "slopeMid", "curvatureMid",
                     "speedXAtEnds", "lineSlope", "lineIntercept"):
            with self.subTest(name=name):
                self.assertIn(name, page)

    def test_the_page_has_the_figures_and_the_table(self):
        page = (ROOT / "workbench" / "ph-quintic-gallery.html").read_text()
        self.assertIn("Fig. Q1", page)
        self.assertIn("24 S", page)
        for tag in ("Fig. Q3", "Fig. Q4", "Fig. Q5", "Fig. Q6", "Fig. Q6b", "Fig. Q7",
                    "Fig. Q8", "Fig. Q9", "Fig. Q10", "Fig. Q11"):
            self.assertIn(tag, page)
        self.assertIn("Moving the root inside", page)
        self.assertIn("How to find a preset", page)
        self.assertIn("ph-quintic-lattice.html", page)
        self.assertEqual(page.count("<tr>"), 49)   # header + 48 rows


if __name__ == "__main__":
    unittest.main()
