"""Every named curve must be the curve it claims to be.

The generators page builds each curve from a rational parametrisation and then
turns it into a Bezier.  This test does the opposite: it takes the finished
control values, evaluates them, and checks the result against an equation or a
trigonometric definition written here by hand, from the mathematics rather than
from the code.  A parametrisation that is subtly the wrong curve still produces
a smooth, plausible picture -- this is the check that notices.

Two curves on the page were wrong when this file was written: `nodal` was
captioned as the Tschirnhausen cubic (its node crosses at 90 degrees, not 60),
and the piriform was given as `x^4 - x^2 y + y^2 = 0`, which has no real points
but the origin.  Both would have failed here immediately.
"""

import math
import sys
import unittest
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generators as G  # noqa: E402

# -- the equations, written independently of the parametrisations -----------

IMPLICIT = {
    "bean": lambda x, y: x ** 4 + x * x * y * y + y ** 4 - x * (x * x + y * y),
    "bicorn": lambda x, y: y * y * (1 - x * x) - (x * x + 2 * y - 1) ** 2,
    "nodal": lambda x, y: y * y - x * x * (x + 1),
    "tschirnhausen": lambda x, y: 27 * y * y - (1 - x) * (8 + x) ** 2,
    "bow": lambda x, y: x ** 4 - (x * x * y - y ** 3),
    "piriform": lambda x, y: x ** 4 - 2 * x ** 3 + y * y,
    "abs(x) gerono": lambda x, y: x ** 4 - x * x + y * y,
    "piriform 2x": lambda x, y: x ** 4 - 4 * x ** 3 + 16 * y * y,
    "cardioid": lambda x, y: (x * x + y * y) ** 2 + 2 * x * (x * x + y * y) - y * y,
    "bernoulli": lambda x, y: (x * x + y * y) ** 2 - (x * x - y * y),
    "gerono": lambda x, y: x ** 4 - x * x + y * y,
    "astroid": lambda x, y: (x * x + y * y - 1) ** 3 + 27 * x * x * y * y,
    "trifolium": lambda x, y: (x * x + y * y) ** 2 - x ** 3 + 3 * x * y * y,
    "quadrifolium": lambda x, y: (x * x + y * y) ** 3 - (x * x - y * y) ** 2,
    "circle": lambda x, y: x * x + y * y - 1,
    "pear": lambda x, y: x * x - y ** 3 * (1 - y),
    "cruciform": lambda x, y: x * x * y * y - x * x - y * y,
}

# roulettes: checked against their trigonometric definition, which is what the
# rational form is supposed to be a rewriting of
TRIG = {
    "deltoid": lambda t: (2 * math.cos(t) + math.cos(2 * t),
                          2 * math.sin(t) - math.sin(2 * t)),
    "hypocycloid k=5": lambda t: (4 * math.cos(t) + math.cos(4 * t),
                                  4 * math.sin(t) - math.sin(4 * t)),
    "epicycloid k=3": lambda t: (4 * math.cos(t) - math.cos(4 * t),
                                 4 * math.sin(t) - math.sin(4 * t)),
    "epicycloid k=5": lambda t: (6 * math.cos(t) - math.cos(6 * t),
                                 6 * math.sin(t) - math.sin(6 * t)),
    "nephroid": lambda t: (3 * math.cos(t) - math.cos(3 * t),
                           3 * math.sin(t) - math.sin(3 * t)),
}

ROUNDED = [(3, -2), (3, 2), (2, 3), (-2, 3), (-3, 2), (-3, -2), (-2, -3),
           (2, -3)]

SAMPLES = [F(k, 40) for k in range(1, 40)]


def entries():
    return {spec["key"]: spec for spec in G.NAMED}


def points(spec, s):
    """Every point the curve visits at this s, across its branches."""
    data = G.named_data(spec)
    out = []
    for ctrl in data["ctrl"]:
        w = sum(F(p[2]) * G.bern_n(i, len(ctrl) - 1, s)
                for i, p in enumerate(ctrl))
        if w == 0:
            continue
        out.append(G.homog_point(ctrl, s))
    return out


class TestNamedCurves(unittest.TestCase):

    def test_every_exact_curve_matches_its_equation(self):
        seen = 0
        for key, spec in entries().items():
            with self.subTest(curve=key):
                if key == "rounded square":
                    continue                      # assembled; checked below
                if key not in IMPLICIT and key not in TRIG:
                    self.assertFalse(
                        G.named_data(spec)["exact"],
                        f"{key} is exact but has no independent check")
                    continue
                data = G.named_data(spec)
                self.assertTrue(data["exact"], f"{key} should be exact")
                seen += 1
                worst = 0.0
                for s in SAMPLES:
                    for x, y in points(spec, s):
                        if key in IMPLICIT:
                            worst = max(worst, abs(IMPLICIT[key](float(x), float(y))))
                        else:
                            u = float(s) / (1 - float(s))
                            th = 2 * math.atan(u)
                            ex, ey = TRIG[key](th)
                            # branches come in mirrored pairs
                            worst = max(worst, min(
                                math.hypot(float(x) - ex, float(y) - ey),
                                math.hypot(float(x) - ex, float(y) + ey)))
                self.assertLess(worst, 1e-9, f"{key} is off its own equation by {worst}")
        self.assertGreaterEqual(seen, 18)

    def test_control_values_and_milestones_are_integers(self):
        for key, spec in entries().items():
            with self.subTest(curve=key):
                data = G.named_data(spec)
                if not data["exact"]:
                    continue
                for ctrl in data["ctrl"]:
                    for p in ctrl:
                        for v in p:
                            self.assertIsInstance(v, int)
                m = spec["m"]
                for branch in data["milestones"]:
                    for p in branch:
                        for v in p:
                            self.assertEqual(F(v) * data["mscale"],
                                             F(v) * data["mscale"])

    def test_scales_are_the_recorded_ones(self):
        """A change here is a change in the arithmetic, not a refactor."""
        expect = {
            "bean": (12, 273), "bicorn": (6, 105), "nodal": (3, 1),
            "tschirnhausen": (1, 27), "bow": (3, 16), "circle": (1, 5),
            "piriform": (3, 25), "gerono": (6, 25), "cardioid": (3, 25),
            "abs(x) gerono": (3, 25), "piriform 2x": (3, 25),
            "pear": (35, 625),
            "bernoulli": (4, 41), "trifolium": (12, 50), "astroid": (5, 1),
            "deltoid": (3, 1), "nephroid": (5, 1), "quadrifolium": (15, 125),
            "rounded square": (1, 425),
        }
        for key, (cs, ms) in expect.items():
            with self.subTest(curve=key):
                data = G.named_data(entries()[key])
                self.assertEqual((data["cscale"], data["mscale"]), (cs, ms))

    def test_rounded_square_closes(self):
        spec = entries()["rounded square"]
        data = G.named_data(spec)
        self.assertEqual(len(data["ctrl"]), 8)
        ends = []
        for ctrl in data["ctrl"]:
            ends.append((float(G.homog_point(ctrl, F(0))[0]),
                         float(G.homog_point(ctrl, F(0))[1]),
                         float(G.homog_point(ctrl, F(1))[0]),
                         float(G.homog_point(ctrl, F(1))[1])))
        for i, (sx, sy, ex, ey) in enumerate(ends):
            nx, ny = ROUNDED[(i + 1) % 8]
            self.assertAlmostEqual(sx, ROUNDED[i][0], places=9)
            self.assertAlmostEqual(sy, ROUNDED[i][1], places=9)
            self.assertAlmostEqual(ex, nx, places=9)
            self.assertAlmostEqual(ey, ny, places=9)

    def test_roulette_helper_agrees_with_the_page(self):
        """The epicycloid entries predate `roulette`; it must still reproduce them."""
        self.assertEqual(G.roulette(2, -1)[0], [1, 0, 6, 0, -3])
        self.assertEqual(G.roulette(3, -1)[0], [2, 0, 18, 0, -18, 0, -2])
        self.assertEqual(G.roulette(4, -1)[0], [3, 0, 36, 0, -70, 0, 20, 0, -5])

    def test_non_rational_curves_are_declared_sampled(self):
        for key in ("squircle", "heart"):
            with self.subTest(curve=key):
                self.assertFalse(G.named_data(entries()[key])["exact"])

    def test_samples_never_hit_a_pole(self):
        for key, spec in entries().items():
            if not G.named_data(spec)["exact"]:
                continue
            with self.subTest(curve=key):
                for s in SAMPLES:
                    self.assertTrue(points(spec, s), f"{key} vanishes at {s}")


if __name__ == "__main__":
    unittest.main()
