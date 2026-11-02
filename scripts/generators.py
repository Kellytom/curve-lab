"""generators: integer planar PH curves of degree 3-6, from numbers you type.

    .venv/bin/python scripts/generators.py
    open workbench/generators.html

    # one curve, your numbers:
    .venv/bin/python scripts/generators.py --n 5 --h 1 --u 2,1,3 --v 1,2,5 --m 5

The input is the generator, not the curve.  A planar PH curve is written

    z'(t) = h(t) · ( u(t)^2 - v(t)^2 , 2 u(t) v(t) ),   sigma = h (u^2 + v^2)

and its degree is fixed by Farouki & Sakkalis's lemma,

    n = deg h + 2 · max(deg u, deg v) + 1

so odd and even degrees are both reachable -- cubics and quintics take h = 1,
quartics and sextics take a linear h.  Everything below is exact: Fraction
coefficients, integer control points, integer milestones at t = k/M.

+y is up.  SVG is y-down, so every figure flips at the last step, in `render`.
"""

from __future__ import annotations

import math
import sys
from fractions import Fraction as F
from math import comb, gcd, lcm
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

INK = "#2e2413"
GOLD = "#c9a441"   # scaffolding: control polygons
DOT = "#b23a2b"    # milestones: needs to read against #fffdf7 and ink
GRID = "#ece4cf"
LINE = "#d8ccae"
MUTED = "#7b6c4e"


# -- the exact engine -------------------------------------------------------

def mul(a, b):
    out = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def integrate(a):
    return [F(0)] + [c / (k + 1) for k, c in enumerate(a)]


def to_bernstein(mono, n):
    """Monomial coefficients of degree <= n -> the n+1 Bernstein control points."""
    m = [F(c) for c in mono] + [F(0)] * (n + 1 - len(mono))
    return [sum((m[k] * F(comb(j, k), comb(n, k)) for k in range(j + 1)), F(0))
            for j in range(n + 1)]


def at(mono, t):
    return sum((c * t ** k for k, c in enumerate(mono)), F(0))


def denom_of(values):
    d = 1
    for c in values:
        d = lcm(d, F(c).denominator)
    return d


class PHCurve:
    """z'(t) = h (u^2 - v^2, 2uv), integrated to degree n."""

    def __init__(self, n: int, u, v, h=(1,)):
        self.n = n
        self.u = [int(c) for c in u]
        self.v = [int(c) for c in v]
        self.h = [int(c) for c in h]
        self.p = max(len(self.u) - 1, len(self.v) - 1)
        self.lam = len(self.h) - 1
        want = self.lam + 2 * self.p + 1
        if want != n:
            raise ValueError(
                f"deg h + 2 max(deg u, deg v) + 1 = {self.lam} + 2*{self.p} + 1 "
                f"= {want}, not {n}.  Pick h, u, v to hit the degree you want.")
        uu, vv = mul(self.u, self.u), mul(self.v, self.v)
        width = max(len(uu), len(vv))
        xd = [a - b for a, b in zip(uu + [0] * (width - len(uu)),
                                    vv + [0] * (width - len(vv)))]
        yd = [2 * a for a in mul(self.u, self.v)]
        self.x = integrate(mul(self.h, xd))
        self.y = integrate(mul(self.h, yd))
        # strip the leading zeros integration leaves if the top coefficient dies
        self.cp = list(zip(to_bernstein(self.x, n), to_bernstein(self.y, n)))

    # -- exact measurements ------------------------------------------------
    def control_scale(self):
        return denom_of([c for p in self.cp for c in p])

    def milestone_scale(self, m: int):
        pts = []
        for k in range(m + 1):
            t = F(k, m)
            pts.append(at(self.x, t))
            pts.append(at(self.y, t))
        return denom_of(pts)

    def scale(self, m: int):
        return lcm(self.control_scale(), self.milestone_scale(m))

    def integer_control(self, scale):
        return [(round(p[0] * scale), round(p[1] * scale)) for p in self.cp]

    def integer_milestones(self, m, scale):
        out = []
        for k in range(m + 1):
            t = F(k, m)
            out.append((round(at(self.x, t) * scale), round(at(self.y, t) * scale)))
        return out

    def check(self, m, scale):
        """Raise unless every control point and milestone really is an integer."""
        for (x, y), p in zip(self.integer_control(scale), self.cp):
            assert F(p[0]) * scale == x and F(p[1]) * scale == y, "control not integral"
        for k in range(m + 1):
            t = F(k, m)
            assert at(self.x, t) * scale == round(at(self.x, t) * scale)
            assert at(self.y, t) * scale == round(at(self.y, t) * scale)
        return True

    def bezier(self, t):
        """de Casteljau on the exact control points -- for drawing."""
        pts = [(F(a), F(b)) for a, b in self.cp]
        while len(pts) > 1:
            pts = [((1 - t) * a[0] + t * b[0], (1 - t) * a[1] + t * b[1])
                   for a, b in zip(pts, pts[1:])]
        return pts[0]

    def arc(self):
        hh, uu, vv = self.h, self.u, self.v
        # sigma = h (u^2 + v^2); integrate exactly over [0, 1]
        sigma = mul(hh, [a + b for a, b in zip(
            mul(uu, uu), mul(vv, vv))])
        return sum((F(c) / (k + 1) for k, c in enumerate(sigma)), F(0))


def plain_bezier_scale(n, m):
    """Milestone scale for an ordinary degree-n Bezier with integer points.

    Nothing PH about it: the Bernstein weights at t = k/m carry m^n, so this is
    the floor every integer-milestone curve pays, PH or not.
    """
    return m ** n


# -- named curves: exact when rational, sampled when not ---------------------
#
# A planar curve is rational exactly when a rational parametrisation exists,
# and then (X(t), Y(t), W(t)) gives an exact rational Bezier with integer data.
# Where no parametrisation exists -- the heart is a smooth sextic -- the curve
# can only be sampled, and the honest output is a polyline, not a polygon.

def _substitute(P, deg):
    """P(t) -> P(s/(1-s)) * (1-s)^deg, back in monomial coefficients of s."""
    out = [F(0)] * (deg + 1)
    for k, c in enumerate(P):
        if not c:
            continue
        for j in range(deg - k + 1):
            out[k + j] += F(c * ((-1) ** j) * comb(deg - k, j))
    return out


def _scale_rows(rows):
    """Rows of exact control values -> integers, plus the least scale.

    The assertion is the point: an earlier version used int() alone, which
    truncates a 1/3 to 0 and draws a different curve without complaint.
    """
    scale = 1
    for r in rows:
        scale = lcm(scale, denom_of(r))
    ctrl = [(int(a * scale), int(b * scale), int(c * scale))
            for a, b, c in zip(*rows)]
    for (px, py, pw), (a, b, c) in zip(ctrl, zip(*rows)):
        assert F(a) * scale == px and F(b) * scale == py and F(c) * scale == pw
    return ctrl, scale


def homog_bezier(X, Y, W, deg):
    """Monomial (X, Y, W) in t -> integer homogeneous control values in s."""
    return _scale_rows([to_bernstein(_substitute(P, deg), deg)
                        for P in (X, Y, W)])


def bern_n(i, deg, s):
    return F(comb(deg, i)) * (1 - s) ** (deg - i) * s ** i


def homog_point(ctrl, s):
    deg = len(ctrl) - 1
    px = sum(F(p[0]) * bern_n(i, deg, s) for i, p in enumerate(ctrl))
    py = sum(F(p[1]) * bern_n(i, deg, s) for i, p in enumerate(ctrl))
    pw = sum(F(p[2]) * bern_n(i, deg, s) for i, p in enumerate(ctrl))
    return px / pw, py / pw


def _pmul(a, b):
    out = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def _cheb(m, second=False):
    if m == 0:
        return [F(1)]
    a, b = [F(1)], ([F(0), F(2)] if second else [F(0), F(1)])
    for _ in range(1, m):
        c = [F(0)] + [2 * v for v in b]
        for i, v in enumerate(a):
            c[i] -= v
        a, b = b, c
    return b


def roulette(m, sign):
    """Hypo- and epicycloids, exactly, in u = tan(t/2).

        x = m cos t + sign*cos(m t)
        y = m sin t - sin(m t)

    sign = +1 is the hypocycloid with k = m+1 cusps, sign = -1 the epicycloid
    with k = m-1.  Returns integer monomial lists (X, Y, W) of degree 2m.
    """
    cn, cd = [F(1), F(0), F(-1)], [F(1), F(0), F(1)]

    def cdpow(k):
        r = [F(1)]
        for _ in range(k):
            r = _pmul(r, cd)
        return r

    X = [F(v) * m for v in _pmul(cn, cdpow(m - 1))]
    for j, tj in enumerate(_cheb(m)):
        if not tj:
            continue
        term = cdpow(m - j)
        for _ in range(j):
            term = _pmul(term, cn)
        for i, v in enumerate([F(v) * tj * sign for v in term]):
            if i < len(X):
                X[i] += v
            else:
                X.append(v)
    inner = [F(v) * m for v in cdpow(m - 1)]
    for j, uj in enumerate(_cheb(m - 1, second=True)):
        if not uj:
            continue
        term = cdpow(m - 1 - j)
        for _ in range(j):
            term = _pmul(term, cn)
        for i, v in enumerate([F(v) * uj for v in term]):
            if i < len(inner):
                inner[i] -= v
            else:
                inner.append(-v)
    deg = 2 * m

    def pad(P):
        P = [F(v) for v in P] + [F(0)] * (deg + 1 - len(P))
        return [int(v) for v in P]

    return pad(X), pad([F(0)] + [2 * v for v in inner]), pad(cdpow(m))


# sanity: the epicycloid entries below were computed before this helper existed
assert roulette(2, -1)[0] == [1, 0, 6, 0, -3]
assert roulette(3, -1)[0] == [2, 0, 18, 0, -18, 0, -2]
assert roulette(4, -1)[0] == [3, 0, 36, 0, -70, 0, 20, 0, -5]


NAMED = [
    dict(key="bean", deg=4, m=4,
         eq="x⁴ + x²y² + y⁴ = x(x² + y²)",
         tail="rational quartic · r = cosθ / (1 − ¼sin²2θ)",
         branches=[([1, 0, 1], [0, 1, 0, 1], [1, 0, 1, 0, 1])]),
    dict(key="bicorn", deg=4, m=4,
         eq="y²(1 − x²) = (x² + 2y − 1)²",
         tail="rational quartic · two branches, joined at (±1, 0)",
         branches=[([0, 2, 0, 6], [1, 0, -2, 0, 1], [1, 0, 4, 0, 3]),
                   ([0, 6, 0, 2], [1, 0, -2, 0, 1], [3, 0, 4, 0, 1])]),
    dict(key="pear", deg=8, m=4,
         eq="x² = y³(1 − y)",
         tail="rational after all · y = sin² t, x = sin³ t cos t",
         branches=[([0, 0, 0, 8, 0, -8], [0, 0, 4, 0, 8, 0, 4],
                    [1, 0, 4, 0, 6, 0, 4, 0, 1])]),
    dict(key="heart", deg=6, m=None,
         eq="(x² + y² − 1)³ = x²y³",
         tail="sextic, three cusps · genus 4 · sampled",
         branches=None, sampler="heart"),
    dict(key="nodal", deg=3, m=2, subst="affine",
         eq="y² = x²(x + 1)",
         tail="nodal cubic · node angle 90° · not the PH one",
         branches=[([0, -4, 4], [0, 4, -12, 8], [1])]),
    dict(key="tschirnhausen", deg=3, m=3, subst="affine",
         eq="27y² = (1 − x)(8 + x)²",
         tail="the cubic PH curve · node angle 60° · r = a sec³(θ/3)",
         branches=[([-11, 48, -48], [2, -36, 96, -64], [1])]),
    dict(key="bow", deg=4, m=4, subst="affine",
         eq="x⁴ = x²y − y³",
         tail="triple point at the origin · genus 0",
         branches=[([0, -4, 12, -8], [0, 4, -20, 32, -16], [1])]),
    dict(key="epicycloid k=3", deg=8, m=2,
         eq="x = 4cos θ − cos 4θ,  y = 4sin θ − sin 4θ",
         tail="epicycloid R = 3r · four cusps · rational, degree 8",
         branches=[([3, 0, 36, 0, -70, 0, 20, 0, -5],
                    [0, 0, 0, 80, 0, -32, 0, 16, 0],
                    [1, 0, 4, 0, 6, 0, 4, 0, 1]),
                   ([3, 0, 36, 0, -70, 0, 20, 0, -5],
                    [0, 0, 0, -80, 0, 32, 0, -16, 0],
                    [1, 0, 4, 0, 6, 0, 4, 0, 1])]),
    dict(key="epicycloid k=5", deg=12, m=2,
         eq="x = 6cos θ − cos 6θ,  y = 6sin θ − sin 6θ",
         tail="epicycloid R = 5r · six cusps · rational, degree 12",
         branches=[([5, 0, 90, 0, -465, 0, 924, 0, -525, 0, 42, 0, -7],
                    [0, 0, 0, 280, 0, -672, 0, 912, 0, -160, 0, 24, 0],
                    [1, 0, 6, 0, 15, 0, 20, 0, 15, 0, 6, 0, 1]),
                   ([5, 0, 90, 0, -465, 0, 924, 0, -525, 0, 42, 0, -7],
                    [0, 0, 0, -280, 0, 672, 0, -912, 0, 160, 0, -24, 0],
                    [1, 0, 6, 0, 15, 0, 20, 0, 15, 0, 6, 0, 1])]),
    dict(key="deltoid", deg=4, m=2,
         eq="x = 2cos θ + cos 2θ,  y = 2sin θ − sin 2θ",
         tail="hypocycloid k = 3 · three cusps · r = 1 + 2cos θ",
         branches=[roulette(2, +1), (roulette(2, +1)[0], [-v for v in roulette(2, +1)[1]], roulette(2, +1)[2])]),
    dict(key="hypocycloid k=5", deg=8, m=2,
         eq="x = 4cos θ + cos 4θ,  y = 4sin θ − sin 4θ",
         tail="hypocycloid k = 5 · five cusps · rational, degree 8",
         branches=[roulette(4, +1), (roulette(4, +1)[0], [-v for v in roulette(4, +1)[1]], roulette(4, +1)[2])]),
    dict(key="nephroid", deg=6, m=2,
         eq="z ↦ z³ + 3z on the unit circle",
         tail="two cusps · rational sextic · x = 6cos φ − 4cos³φ",
         branches=[([2, 0, 18, 0, -18, 0, -2], [0, 0, 0, 32, 0, 0],
                    [1, 0, 3, 0, 3, 0, 1]),
                   ([2, 0, 18, 0, -18, 0, -2], [0, 0, 0, -32, 0, 0],
                    [1, 0, 3, 0, 3, 0, 1])]),
    dict(key="astroid", deg=6, m=2,
         eq="(x² + y² − 1)³ + 27x²y² = 0",
         tail="x^(2/3) + y^(2/3) = 1 · four cusps · rational sextic",
         branches=[([1, 0, -3, 0, 3, 0, -1], [0, 0, 0, 8, 0, 0],
                    [1, 0, 3, 0, 3, 0, 1]),
                   ([1, 0, -3, 0, 3, 0, -1], [0, 0, 0, -8, 0, 0],
                    [1, 0, 3, 0, 3, 0, 1])]),
    dict(key="trifolium", deg=4, m=4,
         eq="(x² + y²)² − x³ + 3xy² = 0",
         tail="three-petaled rose · rational quartic · r = −cos 3θ",
         branches=[([1, 0, -3], [0, 1, 0, -3], [1, 0, 2, 0, 1]),
                   ([1, 0, -3], [0, -1, 0, 3], [1, 0, 2, 0, 1])]),
    dict(key="quadrifolium", deg=6, m=4,
         eq="(x² + y²)³ = (x² − y²)²",
         tail="four-petaled rose · r = cos 2θ · rational sextic",
         branches=[([1, 0, -7, 0, 7, 0, -1], [0, 2, 0, -12, 0, 2],
                    [1, 0, 3, 0, 3, 0, 1]),
                   ([-1, 0, 7, 0, -7, 0, 1], [0, -2, 0, 12, 0, -2],
                    [1, 0, 3, 0, 3, 0, 1])]),
    dict(key="circle", deg=2, m=4,
         eq="x² + y² = 1",
         tail="superellipse n = 2 · exact, integer data",
         branches=[([1, 0, -1], [0, 2], [1, 0, 1]),
                   ([1, 0, -1], [0, -2], [1, 0, 1])]),
    dict(key="rounded square", deg=2, deg_label="4 + 4 pieces", m=4,
         subst="affine",
         eq="four edges and four quarter arcs",
         tail="assembled · every piece exact · corner radius 1, half-side 3",
         branches=[([3], [-2, 4], [1]),
                   ([3, 0, 1], [2, 2, 2], [1, 0, 1]),
                   ([2, -4], [3], [1]),
                   ([-2, -2, -2], [3, 0, 1], [1, 0, 1]),
                   ([-3], [2, -4], [1]),
                   ([-3, 0, -1], [-2, -2, -2], [1, 0, 1]),
                   ([-2, 4], [-3], [1]),
                   ([2, 2, 2], [-3, 0, -1], [1, 0, 1])]),
    dict(key="squircle", deg=4, m=None,
         eq="|x|⁴ + |y|⁴ = 1",
         tail="superellipse n = 4 · Lamé's special quartic · genus 3, sampled",
         branches=None, sampler="squircle"),
    dict(key="cardioid", deg=4, m=4,
         eq="(x² + y²)² + 2x(x² + y²) − y² = 0",
         tail="rational quartic · r = 1 − cos φ · one cusp, one scoop",
         branches=[([0, 0, 2, 0, -2], [0, 0, 0, 4], [1, 0, 2, 0, 1])]),
    dict(key="bernoulli", deg=4, m=4,
         eq="(x² + y²)² = x² − y²",
         tail="lemniscate of Bernoulli · rational quartic · two lobes",
         branches=[([0, 1, 0, 1], [0, 1, 0, -1], [1, 0, 0, 0, 1]),
                   ([0, -1, 0, -1], [0, -1, 0, 1], [1, 0, 0, 0, 1])]),
    dict(key="gerono", deg=4, m=4,
         eq="x⁴ − x² + y² = 0",
         tail="lemniscate of Gerono · rational quartic · one figure eight",
         branches=[([-1, 0, 0, 0, 1], [0, -2, 0, 2], [1, 0, 2, 0, 1])]),
    dict(key="cruciform", deg=4, m=4, subst="affine",
         eq="x²y² − b²x² − a²y² = 0",
         tail="rational quartic · x = a sec t, y = b csc t · one arm, mirrored four times · tails unbounded",
         branches=[]),
    dict(key="piriform", deg=4, m=4,
         eq="x⁴ − 2x³ + y² = 0",
         tail="a water drop · x = 2/(1+u²), y = 4u/(1+u²)² · mirrored on x",
         branches=[([2, 0, 2], [0, 4], [1, 0, 2, 0, 1]),
                   ([2, 0, 2], [0, -4], [1, 0, 2, 0, 1])]),
]


def pear_branches(n=120):
    """x^2 = y^3 (1-y): a cusp at the origin, so no parametrisation."""
    upper, lower = [], []
    for i in range(n + 1):
        y = i / n
        x = y ** 1.5 * max(0.0, 1.0 - y) ** 0.5
        upper.append((x, y))
        lower.append((-x, y))
    return [upper, lower]


def heart_branches(nx=90):
    """The heart, sampled.  There is no parametrisation to do better with."""
    def f(x, y):
        return (x * x + y * y - 1) ** 3 - x * x * y ** 3

    def roots(x):
        out = []
        ys = [-1.6 + 3.2 * i / 1600 for i in range(1601)]
        for a, b in zip(ys, ys[1:]):
            fa, fb = f(x, a), f(x, b)
            if fa == 0:
                out.append(a)
            elif fa * fb < 0:
                lo, hi = a, b
                for _ in range(50):
                    m = (lo + hi) / 2
                    if f(x, lo) * f(x, m) <= 0:
                        hi = m
                    else:
                        lo = m
                out.append((lo + hi) / 2)
        return out

    upper, lower = [], []
    for i in range(nx + 1):
        x = -1.105 + 2.21 * i / nx
        rs = roots(x)
        if not rs:
            continue
        upper.append((x, max(rs)))
        lower.append((x, min(rs)))
    return [upper, lower]


def squircle_branches(n=240):
    """|x|^4 + |y|^4 = 1: a smooth quartic, genus 3, so there is no
    parametrisation to convert.  This is the power form, sampled."""
    pts = []
    for i in range(n + 1):
        t = 2 * math.pi * i / n
        c, sx = math.cos(t), math.sin(t)
        pts.append((math.copysign(abs(c) ** 0.5, c),
                    math.copysign(abs(sx) ** 0.5, sx)))
    return [pts]


def cruciform_branches(n=70):
    """x^2 y^2 = b^2 x^2 + a^2 y^2 (a = b = 1), from x = a sec t, y = b csc t.

    The curve is unbounded and asymptotic to both axes, so this is a finite
    window on each of the four arms rather than a whole curve.
    """
    lo, hi = 0.35, 1.22
    arms = []
    for sx, sy in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
        arms.append([(sx / math.cos(lo + (hi - lo) * i / n),
                      sy / math.sin(lo + (hi - lo) * i / n))
                     for i in range(n + 1)])
    return arms


def named_data(spec):
    """Control values, exact milestones and the scale that clears them."""
    if spec["branches"] is None:
        if spec.get("sampler") == "pear":
            paths = pear_branches()
        elif spec.get("sampler") == "heart":
            paths = heart_branches()
        elif spec.get("sampler") == "cruciform":
            paths = cruciform_branches()
        elif spec.get("sampler") == "squircle":
            paths = squircle_branches()
        else:
            paths = None
        return dict(spec=spec, exact=False, paths=paths,
                    ctrl=None, cscale=None, milestones=None, mscale=None)
    m = spec["m"]
    ctrls, scales, mils = [], [], []
    for X, Y, W in spec["branches"]:
        if spec.get("subst") == "affine":
            # already polynomial in s (t = 2s - 1 or t = s)
            ctrl, scale = _scale_rows(
                [to_bernstein([F(v) for v in P], spec["deg"]) for P in (X, Y, W)])
        else:
            ctrl, scale = homog_bezier(X, Y, W, spec["deg"])
        ctrls.append(ctrl)
        scales.append(scale)
        mils.append([homog_point(ctrl, F(k, m)) for k in range(m + 1)])
    ms = 1
    for branch in mils:
        for p in branch:
            ms = lcm(ms, lcm(p[0].denominator, p[1].denominator))
    return dict(spec=spec, exact=True, paths=None, ctrl=ctrls,
                cscale=lcm(*scales) if len(scales) > 1 else scales[0],
                milestones=mils, mscale=ms)


# -- integer hits ------------------------------------------------------------
#
# A "hit" is a point of the curve that lands exactly on a lattice node.  The
# count is taken over t = p/q with q <= QMAX, which is a stated sample, not a
# theoretical maximum -- the curve is bounded, so the true number is finite but
# there is no closed form for it.  What matters for design is the trend, and
# the trend is blunt: multiplying the grid finds nothing new, because the
# denominators that occur do not change.  The grid that collects hits is the
# one built from the denominators that *do* occur.

QMAX = 14
_POINTS = {}


def curve_points(spec):
    """Every distinct point at t = p/q, q <= QMAX, plus the point at infinity."""
    if spec["key"] in _POINTS:
        return _POINTS[spec["key"]]
    data = named_data(spec)
    seen = set()
    for ctrl in data["ctrl"]:
        deg = len(ctrl) - 1

        def at(s):
            w = sum(F(p_[2]) * bern_n(j, deg, s) for j, p_ in enumerate(ctrl))
            return None if w == 0 else homog_point(ctrl, s)

        for q in range(1, QMAX + 1):
            for p_ in range(-q, q + 1):
                r = at(F(p_, q))
                if r:
                    seen.add(r)
        r = at(F(1))
        if r:
            seen.add(r)
    _POINTS[spec["key"]] = seen
    return seen


def hit_points(spec, scale):
    """The lattice nodes this curve passes through at this grid, as integers."""
    out = set()
    for x, y in curve_points(spec):
        X, Y = F(x) * scale, F(y) * scale
        if X.denominator == 1 and Y.denominator == 1:
            out.add((int(X), int(Y)))
    return sorted(out)


def hits_figure(spec, scale, caption, w=430.0, h=300.0):
    data = named_data(spec)
    curves = []
    for ctrl in data["ctrl"]:
        curves.append([(float(a) * scale, float(b) * scale)
                       for a, b in (homog_point(ctrl, F(i, 200))
                                    for i in range(201))])
    marks = [(float(x), float(y)) for x, y in hit_points(spec, scale)]
    pts = [p for c in curves for p in c] + marks
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    pad = 0.10
    x0, x1 = x0 - pad * (x1 - x0), x1 + pad * (x1 - x0)
    y0, y1 = y0 - pad * (y1 - y0), y1 + pad * (y1 - y0)
    k = min((w - 18) / (x1 - x0), (h - 18) / (y1 - y0))
    ox, oy = (w - (x1 - x0) * k) / 2, (h - (y1 - y0) * k) / 2

    def put(p):
        return ox + (p[0] - x0) * k, h - (oy + (p[1] - y0) * k)

    # the lattice, at a step that divides the grid
    step = max(1, scale // 16)
    lines = []
    gx = x0 - x0 % step
    while gx <= x1 + step:
        a, b = put((gx, y0)), put((gx, y1))
        lines.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
                     f'y2="{b[1]:.1f}" stroke="{GRID}"/>')
        gx += step
    gy = y0 - y0 % step
    while gy <= y1 + step:
        a, b = put((x0, gy)), put((x1, gy))
        lines.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
                     f'y2="{b[1]:.1f}" stroke="{GRID}"/>')
        gy += step

    paths = "".join(
        '<path d="' + "M " + " L ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}"
                                        for p in c) +
        f'" fill="none" stroke="{INK}" stroke-width="2.3"/>' for c in curves)
    dots = "".join(
        f'<circle cx="{put(p)[0]:.1f}" cy="{put(p)[1]:.1f}" r="3.9" '
        f'fill="{DOT}" stroke="#fffdf7" stroke-width="1.2"/>' for p in marks)
    return (f'<svg viewBox="0 0 {w:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg">'
            f'<rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="#fffdf7"'
            f' stroke="{LINE}"/>{"".join(lines)}{paths}{dots}</svg>',
            len(marks), step)


# -- the best grid under a budget -------------------------------------------
#
# Hits depend only on which denominators divide the grid, so the grid is a
# factorisation problem, not a size one.  Hill-climb on prime factors, allowing
# a swap as well as a multiply: multiplying alone gets stuck, e.g. growing
# 5^6 and never discovering that 3 or 7 buys more.

PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31)
_GRID = {}


def _score(dens, S):
    return sum(1 for v in dens if S % v == 0)


def best_grid(spec, budget=3125):
    """The grid <= budget catching the most lattice points on this curve.

    Scored on exactly the sample `hit_points` reports, so the two numbers in
    the table are the same measurement.
    """
    key = (spec["key"], budget)
    if key in _GRID:
        return _GRID[key]
    pts = curve_points(spec)
    dens = [lcm(x.denominator, y.denominator) for x, y in pts]
    ps = sorted({p for v in dens if v <= budget for p in PRIMES if v % p == 0})

    def score(S):
        return sum(1 for v in dens if S % v == 0)

    best = (score(1), 1)
    seeds = [1] + sorted({d for d in dens if d <= budget})[:8]
    for seed in seeds:
        S = seed
        for _ in range(80):
            cur = score(S)
            nxt = None
            for p in ps:                       # multiply
                q = p
                while q * S <= budget:
                    sc = score(S * q)
                    if sc > cur and (nxt is None or sc > nxt[0]):
                        nxt = (sc, S * q)
                    q *= p
            if nxt:
                S = nxt[1]
                continue
            moved = False
            for p in ps:                       # swap one prime for another
                if S % p:
                    continue
                for q in ps:
                    if q == p:
                        continue
                    nS = S // p * q
                    if nS <= budget and nS != S and score(nS) > cur:
                        S, nxt, moved = nS, (0, nS), True
                        break
                if moved:
                    break
            if not nxt:
                break
        if score(S) > best[0]:
            best = (score(S), S)
    _GRID[key] = (best[1], best[0])
    return _GRID[key]


def _compose(P, alpha, beta, deg):
    """P(u) with u = alpha*s + beta, expanded in s to degree deg."""
    out = [F(0)] * (deg + 1)
    for c in reversed(P):
        nxt = [F(0)] * (deg + 1)
        for j, v in enumerate(out):
            if v == 0:
                continue
            nxt[j] = nxt[j] + v * beta
            if j + 1 <= deg:
                nxt[j + 1] = nxt[j + 1] + v * alpha
        nxt[0] += F(c)
        out = nxt
    return out


def cruciform_arm(lo=F(1, 4), hi=F(3, 4)):
    """One arm of x^2 y^2 = x^2 + y^2, exact, over u = tan(t/2) in [lo, hi].

    x = (1+u^2)/(1-u^2), y = (1+u^2)/(2u); the common denominator 2u(1-u^2)
    makes X, Y and W polynomials, so an affine change of parameter keeps the
    arm on whole numbers.
    """
    X = [F(0), F(2), F(0), F(2)]
    Y = [F(1), F(0), F(0), F(0), F(-1)]
    W = [F(0), F(2), F(0), F(-2)]
    a = (hi - lo)
    return ([_compose(X, a, lo, 4), _compose(Y, a, lo, 4),
             _compose(W, a, lo, 4)])


def named_figure(item, w=430.0, h=300.0):
    spec = item["spec"]
    if item["exact"]:
        curves = [[(float(a), float(b)) for a, b in
                   (homog_point(c, F(i, 200)) for i in range(201))]
                  for c in item["ctrl"]]
        marks = [(float(p[0]), float(p[1]))
                 for branch in item["milestones"] for p in branch]
    elif item["paths"]:
        curves = [[(float(a), float(b)) for a, b in br] for br in item["paths"]]
        marks = []
    else:
        return ('<svg viewBox="0 0 430 300" xmlns="http://www.w3.org/2000/svg">'
                '<rect x="0" y="0" width="430" height="300" fill="#fffdf7" '
                'stroke="#d8ccae"/><text x="215" y="150" text-anchor="middle" '
                'font-size="12" fill="#7b6c4e">no real points</text></svg>')
    pts = [p for c in curves for p in c] + marks
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    pad = 0.10
    x0, x1 = x0 - pad * (x1 - x0), x1 + pad * (x1 - x0)
    y0, y1 = y0 - pad * (y1 - y0), y1 + pad * (y1 - y0)
    k = min((w - 18) / (x1 - x0), (h - 18) / (y1 - y0))
    ox, oy = (w - (x1 - x0) * k) / 2, (h - (y1 - y0) * k) / 2

    def put(p):
        # +y up in the model, y-down in SVG: the one flip
        return ox + (p[0] - x0) * k, h - (oy + (p[1] - y0) * k)

    lines = []
    for g in range(1, 4):
        gx = x0 + (x1 - x0) * g / 4
        a, b = put((gx, y0)), put((gx, y1))
        lines.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" '
                     f'x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{GRID}"/>')
        gy = y0 + (y1 - y0) * g / 4
        a, b = put((x0, gy)), put((x1, gy))
        lines.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" '
                     f'x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{GRID}"/>')

    paths = "".join(
        '<path d="' + "M " + " L ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}"
                                        for p in c) +
        f'" fill="none" stroke="{INK}" stroke-width="2.3" '
        f'stroke-linejoin="round"/>' for c in curves)
    dots = "".join(
        f'<circle cx="{put(p)[0]:.1f}" cy="{put(p)[1]:.1f}" r="3.7" '
        f'fill="{DOT}" stroke="#fffdf7" stroke-width="1.2"/>' for p in marks)
    return f"""<svg viewBox="0 0 {w:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="#fffdf7"
          stroke="{LINE}"/>
    {''.join(lines)}
    {paths}
    {dots}
  </svg>"""

# -- the presets: numbers you could say out loud -----------------------------

PRESETS = [
    dict(key="cubic", n=3, h=(1,), u=(2, -2), v=(1, -2), m=4,
         note="h = 1 and linear generators: a Tschirnhausen loop"),
    dict(key="quartic", n=4, h=(1, 2), u=(1, -1), v=(1, -2), m=4,
         note="one linear h, so the degree comes out even"),
    dict(key="quintic", n=5, h=(1,), u=(-2, -1, 1), v=(-1, -1, 2), m=2,
         note="h = 1 and quadratic generators: the C/S workhorse"),
    dict(key="sextic", n=6, h=(1, 2), u=(-1, 1, 0), v=(2, -1, 0), m=2,
         note="linear h times quadratic generators"),
]

_X, _Y, _W = cruciform_arm()
for _spec in NAMED:
    if _spec["key"] == "cruciform":
        _spec["branches"] = [
            (_X, _Y, _W),
            ([(-v) for v in _X], _Y, _W),
            ([(-v) for v in _X], [(-v) for v in _Y], _W),
            (_X, [(-v) for v in _Y], _W),
        ]

STEPS = (2, 4, 5, 8, 10, 16)


def build_preset(spec):
    c = PHCurve(spec["n"], spec["u"], spec["v"], spec["h"])
    m = spec["m"]
    s = c.scale(m)
    c.check(m, s)
    cps = c.integer_control(s)
    ms = c.integer_milestones(m, s)
    xs = [p[0] for p in cps] + [p[0] for p in ms]
    ys = [p[1] for p in cps] + [p[1] for p in ms]
    return dict(spec=spec, curve=c, scale=s, cps=cps, milestones=ms,
                box=(min(xs), min(ys), max(xs), max(ys)),
                step_table=[(mm, c.control_scale(), c.milestone_scale(mm),
                             c.scale(mm)) for mm in STEPS])


# -- drawing ----------------------------------------------------------------

def render(item, w=420.0, h=300.0):
    """One curve: lattice, control polygon, curve, milestones.  y flips here."""
    curve = item["curve"]
    s = item["scale"]
    samples = [curve.bezier(F(i, 240)) for i in range(241)]
    pts = [(float(a) * s, float(b) * s) for a, b in samples] + \
          [(float(a), float(b)) for a, b in item["milestones"]]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    padx = max((x1 - x0) * 0.10, 1.0)
    pady = max((y1 - y0) * 0.10, 1.0)
    x0, x1, y0, y1 = x0 - padx, x1 + padx, y0 - pady, y1 + pady

    k = min((w - 20) / (x1 - x0), (h - 20) / (y1 - y0))
    ox = (w - (x1 - x0) * k) / 2
    oy = (h - (y1 - y0) * k) / 2

    def put(p):
        # +y up in the model, y-down in SVG: this is the one flip
        return ox + (p[0] - x0) * k, h - (oy + (p[1] - y0) * k)

    # a coarse lattice in model units, chosen so there are ~6 lines across
    raw = (x1 - x0) / 6
    step = 1
    for cand in (1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000, 2500,
                 5000, 10000, 25000, 50000, 100000):
        step = cand
        if raw <= cand:
            break

    grid = []
    gx = x0 - x0 % step
    while gx <= x1 + step:
        a, b = put((gx, y0)), put((gx, y1))
        grid.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" '
                    f'x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{GRID}"/>')
        gx += step
    gy = y0 - y0 % step
    while gy <= y1 + step:
        a, b = put((x0, gy)), put((x1, gy))
        grid.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" '
                    f'x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{GRID}"/>')
        gy += step

    dense = [put((float(p[0]) * s, float(p[1]) * s)) for p in samples]
    d = "M " + " L ".join(f"{p[0]:.1f} {p[1]:.1f}" for p in dense)

    poly = [put(p) for p in item["cps"]]
    poly_d = "M " + " L ".join(f"{p[0]:.1f} {p[1]:.1f}" for p in poly)
    dots = "".join(
        f'<circle cx="{put(p)[0]:.1f}" cy="{put(p)[1]:.1f}" r="3.7" '
        f'fill="{DOT}" stroke="#fffdf7" stroke-width="1.2"/>'
        for p in item["milestones"])

    return f"""<svg viewBox="0 0 {w:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg">
    <defs><clipPath id="c{item['spec']['key']}">
      <rect x="0" y="0" width="{w:.0f}" height="{h:.0f}"/>
    </clipPath></defs>
    <rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="#fffdf7"
          stroke="{LINE}"/>
    <g clip-path="url(#c{item['spec']['key']})">
    {''.join(grid)}
    <path d="{poly_d}" fill="none" stroke="{GOLD}" stroke-width="1.1"
          stroke-dasharray="4 3"/>
    {''.join(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="2.4" fill="none" stroke="{MUTED}" stroke-width="1"/>' for p in poly)}
    <path d="{d}" fill="none" stroke="{INK}" stroke-width="2.4"
          stroke-linejoin="round"/>
    {dots}
    </g>
  </svg>"""


# -- the page ---------------------------------------------------------------

def page(items):
    figures, tables, notes = [], [], []
    by = {it["spec"]["key"]: it for it in items}

    def step_row(key, m):
        it = by.get(key)
        if not it:
            return None
        for mm, cs, ms, sc in it["step_table"]:
            if mm == m:
                return cs, ms, sc
        return None

    q5, q10, c8 = step_row("quintic", 5), step_row("quintic", 10), step_row("cubic", 8)
    measured = []
    if q5:
        measured.append(f"this quintic stepped by fifths: <strong>{q5[2]}</strong>")
    if q10:
        measured.append(f"by tenths: <strong>{q10[2]}</strong>")
    if c8:
        measured.append(f"this cubic by eighths: <strong>{c8[2]}</strong>")
    measured_html = " · ".join(measured)

    bean = [x for x in NAMED if x["key"] == "bean"][0]
    hit_a, hits_a, _ = hits_figure(bean, 12, "a")
    hit_b, hits_b, _ = hits_figure(bean, 273, "b")

    named = [named_data(s) for s in NAMED]
    named_cards = "".join(
        f"""<section><h2>Fig. {6 + ni} · {it['spec']['key']}</h2>
  <p class="input">{it['spec']['eq']}</p>
  <div class="art">{named_figure(it)}</div>
  <p class="cap">{it['spec']['tail']}</p></section>"""
        for ni, it in enumerate(named))
    named_rows = "".join(
        f"<tr><td>{it['spec']['key']}</td>"
        f"<td>{it['spec'].get('deg_label', it['spec']['deg'])}</td>"
        f"<td>{'yes' if it['exact'] else it['spec'].get('tier', 'no')}</td>"
        f"<td>{it['cscale'] if it['exact'] else '—'}</td>"
        f"<td>{it['mscale'] if it['exact'] else '—'}</td>"
        f"<td>{len(hit_points(it['spec'], it['cscale'])) if it['exact'] else '—'}</td>"
        f"<td>{bg[1] if it['exact'] else '—'}</td>"
        f"<td>{bg[0] if it['exact'] else '—'}</td>"
        f"</tr>"
        for it in named
        for bg in ([best_grid(it["spec"])] if it["exact"] else [(0, 0)]))

    for fi, it in enumerate(items):
        sp = it["spec"]
        c = it["curve"]
        x0, y0, x1, y1 = it["box"]
        figures.append(f"""<section>
  <h2>Fig. {fi + 2} · {sp['key']} · n = {sp['n']}</h2>
  <p class="input">h = ({','.join(map(str, sp['h']))}) ·
  u = ({','.join(map(str, sp['u']))}) · v = ({','.join(map(str, sp['v']))}) ·
  t by 1/{sp['m']}</p>
  <div class="art">{render(it)}</div>
  <p class="cap">scale <strong>{it['scale']}</strong> · grid
  <strong>{x1 - x0} × {y1 - y0}</strong> · {sp['note']}</p>
</section>""")

        rows = "".join(
            f"<tr><td>{mm}</td><td>{cs}</td><td>{ms}</td><td><strong>{sc}</strong></td>"
            f"<td>{plain_bezier_scale(sp['n'], mm)}</td></tr>"
            for mm, cs, ms, sc in it["step_table"])
        tables.append(f"""<tr><th colspan="5">{sp['key']} · n = {sp['n']}</th></tr>
<tr><th>1/m</th><th>control points</th><th>milestones</th><th>both</th>
<th>plain Bézier</th></tr>{rows}""")

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Generators: integer PH curves from four numbers</title>
<style>
body{{margin:0;background:#f6f1e4;color:{INK};font:16px/1.55 Georgia,serif}}
main{{max-width:1080px;margin:0 auto;padding:34px 22px 70px}}
h1{{font-size:28px;margin:0 0 4px}}
.lead{{color:#8c6a21;margin:0 0 24px}}
h2{{font:600 11px/1.2 ui-monospace,Menlo,monospace;letter-spacing:.12em;
text-transform:uppercase;color:{MUTED};margin:0 0 4px}}
p{{font-size:14px;margin:0 0 8px}}
.input{{font:12px/1.4 ui-monospace,Menlo,monospace;color:{MUTED}}}
.cap{{font-size:12px;color:{MUTED}}}
.panel{{background:#fffdf7;border:1px solid {LINE};padding:16px 18px;margin:0 0 22px}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}
.grid3{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px}}
section{{background:#fffdf7;border:1px solid {LINE};padding:12px}}
.art{{background:#fffdf7;margin:6px 0}}
svg{{display:block;width:100%;height:auto}}
table{{border-collapse:collapse;width:100%;font:12px/1.4 ui-monospace,Menlo,monospace}}
th,td{{border-bottom:1px solid {LINE};padding:5px 8px;text-align:right}}
th:first-child,td:first-child{{text-align:left}}
th{{color:{MUTED};font-weight:600}}
th[colspan]{{color:{INK};text-align:left;border-bottom:2px solid {LINE}}}
code{{font:12px/1.4 ui-monospace,Menlo,monospace;background:#f1ead8;padding:1px 4px}}
@media(max-width:760px){{.grid2{{grid-template-columns:1fr}}}}
</style></head><body><main>

<h1>Generators</h1>
<p class="lead">Integer planar PH curves of degree 3 to 6, from four numbers
you can say out loud.</p>

<div class="panel">
<p><strong>What this page is for, in plain words.</strong> A curve drawn on a
screen is usually a chain of decimals. A curve drawn here is a chain of whole
numbers, chosen before anything is drawn, so the same shape can be cut, measured
or typed into another program without rounding. That is the whole point: pick
four whole numbers, get a curve whose control points are whole numbers too.</p>
<p>The rest of the page is the arithmetic behind that, then a gallery of twenty
named curves — the ones people actually draw — each with the grid it needs and
the points where it lands exactly on the grid.</p>
</div>

<div class="panel">
<p><strong>The input is the generator, not the curve.</strong> Every planar
polynomial PH curve is written</p>
<p style="margin-left:14px"><code>z′(t) = h(t) · ( u(t)² − v(t)² , 2u(t)v(t) )</code>,
&nbsp;<code>σ = h · (u² + v²)</code></p>
<p>and Farouki and Sakkalis's lemma fixes its degree:</p>
<p style="margin-left:14px"><code>n = deg h + 2 · max(deg u, deg v) + 1</code></p>
<p>So the degree is <em>chosen by the split</em>, not by a multiplier. Cubics
and quintics take <code>h = 1</code>; quartics take one linear factor;
sextics take one linear factor and quadratic generators. Type integers into
<code>h</code>, <code>u</code>, <code>v</code>, and a step <code>1/m</code>,
and the rest is arithmetic:</p>
<ul>
<li><strong>control points</strong> come from integrating a cubic (÷3), a
quartic (÷4), a quintic (÷5) or a sextic (÷6), then converting to Bernstein;</li>
<li><strong>milestones</strong> are the points at <code>t = k/m</code>;</li>
<li>the <strong>scale</strong> is the least integer that clears both, and it is
read off the numbers you typed — not off the degree.</li>
</ul>
<p>command: <code>.venv/bin/python scripts/generators.py --n 5 --h 1 --u 2,1,3 --v 1,2,5 --m 5</code></p>
</div>

<div class="panel">
<p><strong>Fig. 1 · where integer hits come from.</strong> A <em>hit</em> is a
point of the curve sitting exactly on a lattice node. The natural first guess is
that a finer grid finds more of them; it does not. Below is one curve — the bean
— at two grids. At scale 12 it passes through 3 lattice nodes. At 48, and at
156, it still passes through 3: multiplying the grid finds nothing new, because
the set of <em>denominators</em> that occur never changed. At 273 it finds 12,
because 273 is built from the denominators that actually occur.</p>
<p>So the rule is the same one the scale table already gives, seen from the
other side: the grid that collects hits is the one assembled out of the
arithmetic, not rounded up to something round. And because a hit only needs its
denominator to <em>divide</em> the grid, the grid is a factorisation problem.
Searching the grids under 3125 for the best one per curve gives
<strong>859 hits across the twenty-one exact curves, against 113 at their
control scales</strong> — seven times as many, with the same curves and no new
mathematics. The table's last two columns carry that per curve: the count at
the control scale, and the best count and grid under 3125.</p>
<div class="grid2">
<section><div class="art">{hit_a}</div>
<p class="cap"><strong>Fig. 1a</strong> · bean at grid 12 · <strong>{hits_a} hits</strong></p></section>
<section><div class="art">{hit_b}</div>
<p class="cap"><strong>Fig. 1b</strong> · same bean at grid 273 · <strong>{hits_b} hits</strong> — four times as many, same curve</p></section>
</div>
<p style="font-size:12px;color:{MUTED}">A hit is counted over <code>t = p/q</code>
with <code>q ≤ {QMAX}</code>: a stated sample, not a theoretical maximum. Every
exact curve hits something — the floor is the crossings, which are integer by
construction. What varies is how far the grid has to reach: the epicycloids at
high <code>k</code> carry denominators in the hundreds, so under 3125 no grid
beats 4, while the rounded square — built from integer pieces — reaches 456.
The four sampled curves have no parameter at all, so they have no hits to
count.</p>
</div>

<div class="grid2">{''.join(figures)}</div>

<div class="panel">
<p><strong>The scale, printed.</strong> Control points, milestones and the
least scale that clears both, for each curve and each step. The last column is
the same curve <em>without</em> the PH condition — an ordinary Bézier whose
control points are integers already.</p>
<table>{''.join(tables)}</table>
<p style="margin-top:10px">Two things fall out of that table, and neither is in
the folklore. First, the milestone scale is <code>mⁿ</code> for a plain Bézier
and never better for a PH curve: the PH property does not buy integer
milestones, the step does. Second, PH <em>costs</em> you a factor of 3
(cubic), 15 (quintic) on the control points, because the integration
denominator has to be cleared. What PH buys is elsewhere: exact arc length,
rational offsets, a rational frame — not a smaller lattice.</p>
</div>

<div class="panel">
<p><strong>Named curves: exact when rational, sampled when not.</strong> One
cubic, four quartics and a sextic, and they split into two kinds. A curve is
<em>rational</em> exactly when a rational parametrisation exists; then
<code>(X(t), Y(t), W(t))</code> turns into an exact Bézier with whole numbers
throughout, by substituting <code>t = s/(1−s)</code>. Where no parametrisation
exists there is nothing to turn, and the curve can only be sampled.</p>
<div class="grid3">{named_cards}</div>
<table style="margin-top:12px">
<tr><th>curve</th><th>degree</th><th>exact Bézier</th><th>control scale</th>
<th>milestones clear at</th><th>hits at control</th><th>best hits ≤ 3125</th>
<th>on that grid</th></tr>
{named_rows}
</table>
<p style="margin-top:10px"><strong>Why the bean has no polygon.</strong> Its
homogeneous control values include two with <code>W = 0</code> — points at
infinity. The integral data lives in three dimensions and the picture is its
shadow, so there is no closed polygon to lay on the lattice.</p>
<p><strong>But integer milestones do exist.</strong> The bean's quarter-points
are (1, 0), (90/91, 30/91), (2/3, 2/3), (10/91, 30/91), (0, 0): denominators
1, 91, 3, 91, 1, so a scale of <strong>273</strong> puts every one on integers.
Any finite set of rational parameters clears, because you take the lowest
common multiple — the scale is a fact about the arithmetic, not a wall.</p>
<p><strong>What is a wall.</strong> No bounded curve holds infinitely many
lattice points, so the chat log's "infinitely many points on the curve can be
integers" cannot be true of any curve, PH or not. You get finitely many, at
parameters you choose, and the denominators set the price.</p>
<p><strong>The two lemniscates are both rational.</strong> Gerono's
<code>x⁴ − x² + y² = 0</code> is a figure eight from one Bézier. Bernoulli's
<code>(x²+y²)² = x² − y²</code> looks like it should not be — its <em>arc
length</em> needs elliptic integrals, which usually means genus one — but its
shape is genus zero, because the double point at the origin and the two
circular points at infinity account for all of the degree. The parametrisation
<code>x = (t+t³)/(1+t⁴)</code>, <code>y = (t−t³)/(1+t⁴)</code> is exact, and one
lobe is one Bézier. Rationality is about the shape, not about how hard the
perimeter is to measure.</p>
<p><strong>Hypocycloids are the same family with one sign flipped.</strong>
Inside a fixed circle of radius <code>R = kr</code> the rolling circle traces
<code>x = m cos θ + cos(mθ)</code>, <code>y = m sin θ − sin(mθ)</code> with
<code>m = k − 1</code>, and <code>k</code> counts the cusps directly.
<code>k = 2</code> is the Tusi couple — a straight line, which is why the
degenerate case is worth naming rather than skipping; <code>k = 3</code> is the
deltoid; <code>k = 4</code> is the astroid, already above. Two more are shown at
<code>k = 3</code> and <code>k = 5</code>. The astroid above and the hypocycloid
at <code>k = 4</code> are the same shape in different normalisations — one is
<code>cos³t</code>, the other <code>4cos³t</code> — which is the kind of thing
that looks like an error and is not.</p>
<p><strong>Epicycloids are a family, and two members are already here.</strong>
A circle of radius <code>r</code> rolling outside one of radius <code>R = kr</code>
traces <code>x = r(k+1)cos θ − r cos((k+1)θ)</code>, <code>y = r(k+1)sin θ −
r sin((k+1)θ)</code>. At <code>k = 1</code> that is the cardioid and at
<code>k = 2</code> the nephroid — both on this page already, in their own
normalisations. The degree climbs with <code>k</code>: <code>2(k+1)</code>. Two
more are shown, <code>k = 3</code> at degree 8 and <code>k = 5</code> at degree
12, and they stay rational throughout, because <code>cos(mθ)</code> is a
polynomial in <code>cos θ</code> — Chebyshev again — so <code>tan(θ/2)</code>
still rationalises the whole thing.</p>
<p><strong>The nephroid is the sextic that is a cubic in disguise.</strong>
<code>z ↦ z³ + 3z</code> sends the unit circle to it, which is why the
parametrisation is so short: <code>x = 6cos φ − 4cos³φ</code>,
<code>y = 4sin³φ</code>, both polynomial in <code>cos</code> and
<code>sin</code>, hence rational in <code>tan(φ/2)</code>. Two cusps, genus
zero, exact.</p>
<p><strong>The astroid is a sextic with four cusps.</strong>
<code>x^(2/3) + y^(2/3) = 1</code> looks like it needs fractional powers
everywhere; in the form <code>(x²+y²−1)³ + 27x²y² = 0</code> it is a plain
sextic, and <code>x = cos³t</code>, <code>y = sin³t</code> becomes
<code>X = (1−u²)³</code>, <code>Y = 8u³</code>, <code>W = (1+u²)³</code> under
<code>u = tan(t/2)</code>. Four cusps, genus zero, exact.</p>
<p><strong>Roses are the same trick at higher degree.</strong> The trifolium
<code>(x²+y²)² − x³ + 3xy² = 0</code> is a quartic with three petals, and
<code>y = tx</code> through the triple point gives
<code>x = (1−3t²)/(1+t²)²</code>. The quadrifolium
<code>(x²+y²)³ = (x²−y²)²</code> is a <em>sextic</em> — four petals need the
extra degree — but still genus zero, so it too has an exact Bézier, of degree
six.</p>
<p><strong>The squircle's integer-compatible cousins.</strong> Within the
superellipse family <code>|x|ⁿ + |y|ⁿ = 1</code> the rational members are exactly
<code>n = 1</code> (a diamond), <code>n = 2</code> (a circle) and
<code>n = 4/3</code> — which, written as <code>x^(2/3) + y^(2/3) = 1</code>, is the
astroid. <code>n = 4</code> is genus 3 and cannot be rational. So a convex
square-cornered shape has to be <em>assembled</em>: the rounded square below is
four straight edges and four quarter circles, and each quarter circle is exact
under the tangent-half-angle substitution, with no <code>√2</code> weights —
<code>x = c + (1−s²)/(1+s²)</code>, <code>y = c + 2s/(1+s²)</code>. Eight
pieces, all integer data, one shape.</p>
<p><strong>The squircle is the honest failure here.</strong>
<code>|x|⁴ + |y|⁴ = 1</code> is smooth: no node, no cusp, nothing for a line
through the origin to exploit. Its genus is 3, so it has no rational
parametrisation at all, and it is sampled. That is the line the whole table is
drawing — singularities make curves cheap, and the squircle has none.</p>
<p><strong>The cardioid is the same machinery again.</strong>
<code>r = 1 − cos φ</code> is a circle rolling round a fixed one; in Cartesian it
is <code>(x²+y²)² + 2x(x²+y²) − y² = 0</code>, a quartic with a cusp at the
origin. With <code>u = tan(φ/2)</code> it is
<code>X = 2u²(1−u²)</code>, <code>Y = 4u³</code>, <code>W = (1+u²)²</code>: four
integers, four powers, one Bézier.</p>
<p><strong>Two genus-zero quartics that differ only by a bound.</strong> The
Gerono lemniscate <code>x⁴ − x² + y² = 0</code> and the cruciform
<code>x²y² − b²x² − a²y² = 0</code> are both rational quartics, so both have
exact rational Béziers. The lemniscate is bounded — it closes into a figure
eight — so one Bézier over <code>t = s/(1−s)</code> covers all of it. The
cruciform runs off to infinity along both axes, so no single Bézier covers it:
each of the four arms is a separate window, and the page draws a finite piece
of each. Same genus, same degree, different answer — the bound is what decides.</p>
<p><strong>The bow is the triple-point case.</strong> <code>x⁴ = x²y − y³</code>
crosses itself <em>three</em> times at the origin, which is what makes it genus
zero and rational: every line through the origin meets the curve once more, so
<code>x = t − t³</code>, <code>y = t² − t⁴</code> is the whole curve. It is
polynomial, so its Bézier is exact with no weights at all — the cheapest named
curve on this page.</p>
<p><strong>Two nodal cubics, and only one is the PH one.</strong> Every cubic PH
curve is a scaled, rotated Tschirnhausen cubic, <code>27ay² = (a−x)(8a+x)²</code>,
whose node crosses at <strong>60°</strong>. The curve above it,
<code>y² = x²(x+1)</code>, has a <strong>90°</strong> node — so it is a nodal
cubic but not that one, and it is not a PH curve at all. The node angle is the
tell, and it is easy to measure: both curves are the same genus and the same
degree, and an affine map can turn one into the other, but no <em>similarity</em>
can, because an angle is not affine.</p>
<p><strong>The control cases fail, and that is the point.</strong> The pear
<code>x² = y³(1−y)</code> is a quartic with a cusp at the origin — genus 2. The
heart <code>(x²+y²−1)³ = x²y³</code> is a sextic with three cusps, at
<code>(±1, 0)</code> and <code>(0, −1)</code> — genus 4. Both are real, both are
drawable, and neither has a rational parametrisation: <code>|∇F|</code>
vanishes at those cusps, which is exactly what rules it out. They are drawn by
solving for <code>y</code> at sampled <code>x</code>. A table where every named
curve came out rational would prove nothing.</p>
<p><strong>The piriform is the fourth exact one.</strong>
<code>a⁴y² = b²x³(2a − x)</code>, which at <code>a = b = 1</code> is
<code>y² = x³(2 − x)</code>: a rational quartic with a cusp at the origin, a
vertex at <code>(2, 0)</code>, and the bounds <code>0 ≤ x ≤ 2</code>,
<code>|y| ≤ 3√3/4</code>. Through <code>x = 1 + sin t</code>,
<code>y = cos t (1 + sin t)</code>, then <code>u = tan(t/2)</code>, it becomes
<code>X = (u+1)²(1+u²)</code>, <code>Y = (u+1)²(1−u²)</code>,
<code>W = (1+u²)²</code> — whole numbers, no clearing needed.</p>
<p style="font-size:12px;color:{MUTED}">A caution recorded here because it cost
an hour: <code>x⁴ − x²y + y² = 0</code> is a quadratic in <code>y</code> with
discriminant <code>−3x⁴</code>, so its only real point is the origin, and
<code>x⁴ + x²y − y² = 0</code> factorises as
<code>(y − k₁x²)(y − k₂x²)</code> — two parabolas, not a pear. Only the
<code>x³</code> form is the curve.</p>
</div>

<div class="panel">
<p><strong>Where the 3,125 grid comes from.</strong> It is not a property of
quintics. It is <code>5⁵</code>: the step <code>1/5</code> raised to the degree
5, the same rule as <code>mⁿ</code> above. For the curves on this page the
table gives it exactly — {measured_html}.</p>
<p>So the mesh number is fixed by the degree and the step, and by nothing else;
the generators only decide whether the control points clear cheaply. And a
scale is only a minimum: any multiple works, so the power-of-two grids (128,
256, 2048) are reached by rounding the computed scale up, with the margins
free.<br>
Where the paste is right: <em>you can move factors into the generators</em>.
Type <code>u = (2,8)</code>, <code>v = (4,16)</code> and the scale falls,
because common factors cancel inside the curve before the mesh ever sees them.
Where it is wrong: nothing moves <code>mⁿ</code>, because that term comes from
the Bernstein weights at a rational <code>t</code>, not from the curve.</p>
</div>

<div class="panel">
<p><strong>What this does not cover, and why.</strong></p>
<ul>
<li><strong>n = 2.</strong> There are no quadratic PH curves: the lemma gives
<code>n = 1</code> or <code>n ≥ 3</code>.</li>
<li><strong>The bean, the piriform and the heart.</strong> They are quartic
<em>algebraic</em> curves, not PH: their speed is not a polynomial, so their
offsets are not rational. They still take integer control points — every
Bézier does — but their milestones cost <code>m⁴</code> and nothing about them
is exact. Draw them as plain quartics on the same lattice; do not expect the
PH machinery.</li>
<li><strong>The catenary.</strong> A true one needs <code>cosh</code>, so it is
transcendental and no scale factor can put it on an integer grid — the AHPH
family keeps the <em>PH property</em> in the hyperbolic basis, but not
integers. The catenary page already does the integer-friendly thing: four
Tschirnhausen cubics over the curve, worst error 0.41% of <code>a</code>.</li>
<li><strong>The 2^n grids.</strong> 128, 256, 2048 are mesh sizes, not
mathematics: any scale that is a multiple of the computed one works. Pick the
power of two above the required grid and the margins are free.</li>
</ul>
</div>

<p style="font-size:12px;color:{MUTED}">Every coordinate on this page is an
integer, computed in <code>fractions.Fraction</code> and asserted integral
before the page is written. The figures are y-down SVG; the model is +y up and
<code>render()</code> does the one flip.</p>

</main></body></html>
"""


def parse_args(argv):
    spec = dict(n=5, h=(1,), u=(2, 1, 3), v=(1, 2, 5), m=5,
                key="custom", note="your numbers")
    if not argv:
        return None
    it = iter(argv)
    for a in it:
        if a == "--n":
            spec["n"] = int(next(it))
        elif a == "--h":
            spec["h"] = tuple(int(x) for x in next(it).split(","))
        elif a == "--u":
            spec["u"] = tuple(int(x) for x in next(it).split(","))
        elif a == "--v":
            spec["v"] = tuple(int(x) for x in next(it).split(","))
        elif a == "--m":
            spec["m"] = int(next(it))
    return spec


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    custom = parse_args(argv)
    items = [build_preset(p) for p in PRESETS]
    if custom:
        items.append(build_preset(custom))
    path = ROOT / "workbench" / "generators.html"
    path.write_text(page(items), encoding="utf-8")
    print(path)
    for it in items:
        sp, c = it["spec"], it["curve"]
        x0, y0, x1, y1 = it["box"]
        print(f"  {sp['key']:8s} n={sp['n']} "
              f"scale={it['scale']:>7d} grid={x1-x0}x{y1-y0} "
              f"arc={float(c.arc()):.4f} verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
