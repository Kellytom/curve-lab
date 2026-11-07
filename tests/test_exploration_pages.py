"""Guards the three exploration pages: their claims, not just their files."""

import math
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "workbench"


class TestLogSpiral(unittest.TestCase):
    def test_parallel_is_not_a_log_spiral(self):
        b = 0.2

        def pt(th):
            r = 10 * math.exp(b * th)
            return r * math.cos(th), r * math.sin(th)

        def nrm(th):
            r = 10 * math.exp(b * th)
            dr = b * r
            t = (dr * math.cos(th) - r * math.sin(th), dr * math.sin(th) + r * math.cos(th))
            L = math.hypot(*t)
            return -t[1] / L, t[0] / L

        spread = []
        for i in range(400):
            th = 6 * math.pi * i / 399
            p, n = pt(th), nrm(th)
            spread.append((p[0] + n[0], p[1] + n[1]))
        seq = []
        for i in range(1, len(spread) - 1):
            dx = spread[i + 1][0] - spread[i - 1][0]
            dy = spread[i + 1][1] - spread[i - 1][1]
            v = (math.atan2(dy, dx) - math.atan2(spread[i][1], spread[i][0])) % math.pi
            if seq:
                while v - seq[-1] > math.pi / 2: v -= math.pi
                while v - seq[-1] < -math.pi / 2: v += math.pi
            seq.append(v)
        self.assertGreater(math.degrees(max(seq) - min(seq)), 0.5)

    def test_page_exists(self):
        page = (PAGES / "log-spiral.html").read_text()
        self.assertIn("Fig. L1", page)
        self.assertIn("evolute", page)


class TestParabolaFamily(unittest.TestCase):
    def test_evolute_involute_returns_the_parabola(self):
        def p(t): return (t, t * t / 2)
        def n(t):
            L = math.sqrt(1 + t * t)
            return (-t / L, 1 / L)
        def evo(t):
            nn = n(t); rho = (1 + t * t) ** 1.5
            return (t + rho * nn[0], t * t / 2 + rho * nn[1])
        def inv(t, c=-1.0):
            nn = n(t); E = evo(t); s = (1 + t * t) ** 1.5 - 1
            return (E[0] - (s - c) * nn[0], E[1] - (s - c) * nn[1])

        worst = max(math.dist(inv(t), p(t)) for t in [0.05 + 0.05 * i for i in range(1, 60)])
        self.assertLess(worst, 1e-9)

    def test_evolute_at_integer_t(self):
        # the evolute of y = x² is (−4t³, 3t² + ½), i.e. 27x² = 16(y − ½)³;
        # the widely copied 27x² = 4(y − 2)³ is a different semicubical
        for t in (1, 2, 3):
            x, y = -4 * t ** 3, 3 * t * t + 0.5
            self.assertAlmostEqual(27 * x * x, 16 * (y - 0.5) ** 3, places=6)
        # the pasted form satisfies its own identity but not the evolute's
        x, y = 2 * 1 ** 3, 3 * 1 ** 2 + 2
        self.assertAlmostEqual(27 * x * x, 4 * (y - 2) ** 3)
        self.assertNotAlmostEqual(y, 3 * 1 * 1 + 0.5)

    def test_offset_is_not_a_parabola(self):
        # the fit residual of the offset must be a non-trivial share of d
        d, tmax, N = 0.1, 3.0, 500
        pts = []
        for i in range(N):
            t = -tmax + 2 * tmax * i / (N - 1)
            L = math.sqrt(1 + t * t)
            pts.append((t - d * t / L, t * t / 2 + d / L))
        S2 = S4 = Sy = Su2y = 0.0
        for x, y in pts:
            u = x / tmax; u2 = u * u
            S2 += u2; S4 += u2 * u2; Sy += y; Su2y += u2 * y
        det = N * S4 - S2 * S2
        A = (N * Su2y - S2 * Sy) / det
        C = (S4 * Sy - S2 * Su2y) / det
        worst = max(abs(A * (x / tmax) ** 2 + C - y) for x, y in pts)
        self.assertGreater(worst / d, 0.05)


class TestTaperedStemPage(unittest.TestCase):
    def test_page_states_the_asymmetry(self):
        page = (PAGES / "tapered-stem.html").read_text()
        self.assertIn("Fig. T1", page)
        self.assertIn("asymmetric", page)
        self.assertIn("5.25%", page)


class TestComposedStem(unittest.TestCase):
    def test_page_states_the_kink(self):
        page = (PAGES / "composed-stem.html").read_text()
        self.assertIn("Fig. C1", page)
        self.assertIn("25.06", page)
        self.assertIn("1/5", page)


class TestShowcase(unittest.TestCase):
    def test_every_single_curve_panel_carries_companions(self):
        """Main curve plus a left and right companion, and the rule is named.

        Fig. 1a (the log spiral) is the reference. A curve is one curve even
        when it is drawn in pieces — hyperbola branches, lemniscate loops,
        cusp splits, an ideal plus its quantised twin — so each piece gets its
        own pair. Charts are not curves, and the Rays panel is its own
        monstrance, so neither may claim companions.
        """
        page = (PAGES / "showcase.html").read_text()
        charts = {"19b", "20c"}
        anchors = re.findall(
            r'<a class="fig" id="fig-([0-9a-zA-Z]+)"([^>]*)>(.*?)</a>', page, re.S)
        self.assertEqual(len(anchors), 463)          # 392 figures plus the rays
        with_companions = 0
        for key, attrs, body in anchors:
            paths = re.findall(r'<path [^>]*>', body)
            comp = [p for p in paths if 'class="comp"' in p]
            solid = [p for p in paths if 'class="comp"' not in p
                     and 'stroke="#d8ccae"' not in p
                     and 'stroke-dasharray' not in p]
            ink = [p for p in solid if 'stroke="#2e2413"' in p]
            mains = ink or solid
            rule = re.search(r'data-companion="([^"]+)"', attrs)
            if 'data-single="1"' in attrs:
                with_companions += 1
                self.assertEqual(len(comp), 2 * len(mains), key)
                self.assertIsNotNone(rule, key)
                self.assertIn(rule.group(1), ("exact", "fitted", "not an offset"), key)
                self.assertIn(rule.group(1), body, key)   # named in the panel
            elif key in charts:
                self.assertEqual(len(comp), 0, key)
                self.assertIsNone(rule, key)
        self.assertGreaterEqual(with_companions, 300)
        # the pieces that made the first cut wrong: one curve, several paths
        for key in ("16a", "16b", "16c", "9d", "8f", "c004", "c008", "c010",
                    "c012", "c020", "c022", "c023", "c025", "c048"):
            self.assertIn(f'id="fig-{key}"', page)
            self.assertRegex(
                page, rf'id="fig-{key}"[^>]*data-companion="(exact|fitted|not an offset)"')

    def test_three_across_and_rays_last(self):
        page = (PAGES / "showcase.html").read_text()
        self.assertEqual(page.count('class="row"'), 164)
        self.assertEqual(page.count('class="row four"'), 0)
        self.assertIn("Fig. 1a", page)
        self.assertIn("Rays", page)
        self.assertLess(page.index("Fig. 3a"), page.index("Fig. 6"))
        self.assertIn("monstrance", page)

    def test_the_345_spiral_panel(self):
        # moved to the notes page: it is an explanation with an illustration
        page = (PAGES / "showcase.html").read_text()
        notes = (PAGES / "showcase-notes.html").read_text()
        self.assertNotIn('id="fig-19a"', page)
        self.assertIn('id="fig-19a"', notes)
        self.assertIn("int nodes x5^15", notes)

    def test_the_closed_gap_panels(self):
        page = (PAGES / "showcase.html").read_text()
        self.assertIn('id="fig-4d"', page)
        self.assertIn("rails not equidistant", page)
        self.assertIn('id="fig-8d"', page)
        self.assertIn("seagrass", page)
        self.assertIn('id="fig-9d"', page)
        self.assertIn("hyperbola", page)

    def test_every_named_curve_is_on_the_page(self):
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        import generators as G
        page = (PAGES / "showcase.html").read_text()
        for spec in G.NAMED:
            self.assertIn(f'data-curve="{spec["key"]}"', page, spec["key"])

    def test_the_squircle_of_eight_eulers(self):
        page = (PAGES / "showcase.html").read_text()
        self.assertIn('id="fig-8e"', page)
        self.assertIn("eight 45° Euler spans", page)
        self.assertIn('id="fig-8f"', page)
        self.assertIn("bicorn · one quartic", page)
        self.assertIn('id="fig-8g"', page)
        self.assertIn("four bicorns, moved to the origin", page)

    def test_clouds_and_drapery(self):
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        import showcase_catalogue as C
        page = (PAGES / "showcase.html").read_text()
        self.assertEqual(len(C.cloud_panels()), 7)
        self.assertEqual(len(C.drapery_panels()), 6)
        self.assertEqual(len(C.combined_panels()), 6)
        self.assertIn("Combined curves · 6", page)
        self.assertEqual(len(C.primal_panels()), 4)
        self.assertIn("Primal · 4", page)
        self.assertEqual(len(C.cubic_c_panels()), 10)
        self.assertIn("The integer C cubics · 10", page)
        self.assertNotIn("Clouds · 7", page)
        effects = (PAGES / "showcase-effects.html").read_text()
        self.assertIn("Cloud effects", effects)
        self.assertEqual(len(C.cloud_panels()), 7)
        self.assertIn("Drapery · 6", page)

    def test_french_curves_and_leaves(self):
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        import curve_morphs as M
        page = (PAGES / "showcase.html").read_text()
        self.assertEqual(len(M.french_panels()), 8)
        self.assertEqual(len(M.leaf_panels()), 8)
        self.assertIn("French curves · 8", page)
        self.assertIn("Leaves · 8", page)

    def test_the_terminal_fit_and_named_panels(self):
        page = (PAGES / "showcase.html").read_text()
        self.assertIn('id="fig-20a"', page)
        self.assertIn("butt, point, arc, round", page)
        self.assertIn('id="fig-21a"', page)
        self.assertIn("fitted, never exact", page)
        self.assertIn('data-curve="tschirnhausen"', page)
        self.assertIn("Tschirnhausen", page)


class TestShowcaseNotes(unittest.TestCase):
    def test_every_figure_links_to_its_note(self):
        page = (PAGES / "showcase.html").read_text()
        notes = (PAGES / "showcase-notes.html").read_text()
        ids = re.findall(r'id="fig-([0-9a-zA-Z]+)"', page)
        self.assertEqual(len(ids), 463)
        for key in ids:
            self.assertIn(f'href="showcase-notes.html#fig-{key}"', page)
            self.assertIn(f'id="fig-{key}"', notes)
        self.assertEqual(len(set(ids)), 463)
        self.assertIn("fig-rays", page)
        self.assertIn('id="fig-rays"', notes)


class TestMultiGrid(unittest.TestCase):
    def test_composite_is_the_lcm(self):
        comp = 1
        for d in (1, 5, 25):
            comp = comp * d // math.gcd(comp, d)
        self.assertEqual(comp, 25)

    def test_page_exists(self):
        page = (PAGES / "multi-grid.html").read_text()
        self.assertIn("Fig. G1", page)
        self.assertIn("15,625", page)


if __name__ == "__main__":
    unittest.main()
