"""Guards the three exploration pages: their claims, not just their files."""

import math
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
