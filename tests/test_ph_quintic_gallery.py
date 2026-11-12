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

    def test_the_page_has_the_figures_and_the_table(self):
        page = (ROOT / "workbench" / "ph-quintic-gallery.html").read_text()
        self.assertIn("Fig. Q1", page)
        self.assertIn("24 S", page)
        for tag in ("Fig. Q3", "Fig. Q4", "Fig. Q5"):
            self.assertIn(tag, page)
        self.assertIn("Moving the root inside", page)
        self.assertIn("ph-quintic-lattice.html", page)
        self.assertEqual(page.count("<tr>"), 49)   # header + 48 rows


if __name__ == "__main__":
    unittest.main()
