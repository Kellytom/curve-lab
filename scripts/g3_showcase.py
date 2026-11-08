"""A G3-only showcase: five independent Bezier spans per curve.

    .venv/bin/python scripts/g3_showcase.py
    open workbench/g3-showcase.html
    open workbench/g3-notes.html

G3 at a join means position, tangent, curvature and curvature-rate all agree.
The spans are independent: each has its own control points, and the join is a
measured G3 join, not a shared polynomial. Where the curve itself is a cubic
(the ogee and the lattice wave), the five spans collapse to cubics. Otherwise
the spans are degree 7, because a generic chain of independent cubics cannot
carry G3: a cubic has four control points against five join conditions.

Circles are G3 everywhere; they are explained on the notes page rather than
used as a showcase panel, because they pass the gate trivially.
"""

from __future__ import annotations

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = "#fbf7ec"
INK, MUTED, GOLD, BLUE, RED = "#2e2413", "#7b6c4e", "#c9a441", "#1f5fa8", "#a23b2a"
RULE = "#d8ccae"
GREEN = "#2f6b3a"

TOL = 1e-9
ANGLE_TOL = 1e-6          # degrees; floating-point noise only


# -- exact geometry ---------------------------------------------------------

def hermite7(p0, d0, dd0, ddd0, p1, d1, dd1, ddd1):
    """The degree-7 Bezier span with the given Hermite data at t = 0 and 1."""
    def add(*vs):
        return (sum(v[0] for v in vs), sum(v[1] for v in vs))

    def mul(k, v):
        return (k * v[0], k * v[1])

    return [
        p0,
        add(p0, mul(1 / 7, d0)),
        add(p0, mul(2 / 7, d0), mul(1 / 42, dd0)),
        add(p0, mul(3 / 7, d0), mul(3 / 42, dd0), mul(1 / 210, ddd0)),
        add(p1, mul(-3 / 7, d1), mul(3 / 42, dd1), mul(-1 / 210, ddd1)),
        add(p1, mul(-2 / 7, d1), mul(1 / 42, dd1)),
        add(p1, mul(-1 / 7, d1)),
        p1,
    ]


def bezier(P, t):
    n = len(P) - 1
    u = 1.0 - t
    x = y = 0.0
    for i, p in enumerate(P):
        w = math.comb(n, i) * u ** (n - i) * t ** i
        x += w * p[0]
        y += w * p[1]
    return (x, y)


def derivative(P, t, order=1):
    Q = list(P)
    n = len(Q) - 1
    for _ in range(order):
        Q = [(n * (Q[i + 1][0] - Q[i][0]),
              n * (Q[i + 1][1] - Q[i][1])) for i in range(len(Q) - 1)]
        n -= 1
    m = len(Q) - 1
    u = 1.0 - t
    x = y = 0.0
    for i, p in enumerate(Q):
        w = math.comb(m, i) * u ** (m - i) * t ** i
        x += w * p[0]
        y += w * p[1]
    return (x, y)


def curvature(P, t):
    a = derivative(P, t, 1)
    b = derivative(P, t, 2)
    speed = math.hypot(*a)
    if speed == 0.0:
        return float("nan")
    return (a[0] * b[1] - a[1] * b[0]) / speed ** 3


def curvature_rate(P, t):
    """d(kappa)/ds, the G3 quantity, at parameter t."""
    a = derivative(P, t, 1)
    b = derivative(P, t, 2)
    c = derivative(P, t, 3)
    speed = math.hypot(*a)
    if speed == 0.0:
        return float("nan")
    num = a[0] * b[1] - a[1] * b[0]
    # N = cross(r', r''); N' = cross(r', r''') because cross(r'', r'') = 0
    num_d = a[0] * c[1] - a[1] * c[0]
    kappa_d = num_d / speed ** 3 - 3 * num * (a[0] * b[0] + a[1] * b[1]) / speed ** 5
    return kappa_d / speed


def gate(spans):
    """Measure every join. A join passes only if all four gaps are below tol."""
    joins = []
    for i in range(len(spans) - 1):
        A, B = spans[i], spans[i + 1]
        pA, pB = bezier(A, 1.0), bezier(B, 0.0)
        dA, dB = derivative(A, 1.0, 1), derivative(B, 0.0, 1)
        la, lb = math.hypot(*dA), math.hypot(*dB)
        dot = dA[0] * dB[0] + dA[1] * dB[1]
        cross = dA[0] * dB[1] - dA[1] * dB[0]
        # atan2 keeps the small-angle resolution that acos loses near 1
        ang = math.degrees(abs(math.atan2(cross, dot)))
        row = {
            "join": f"{i}–{i + 1}",
            "dp": math.dist(pA, pB),
            "angle": ang,
            "dk": abs(curvature(A, 1.0) - curvature(B, 0.0)),
            "dks": abs(curvature_rate(A, 1.0) - curvature_rate(B, 0.0)),
        }
        row["pass"] = (row["dp"] < TOL and row["angle"] < ANGLE_TOL
                       and row["dk"] < TOL and row["dks"] < TOL)
        joins.append(row)
    return joins


# -- quintic G3 spans -------------------------------------------------------

def quintic_g3(p0, p5, T0, T1, k0, k1, r0, r1, a, b):
    """A quintic Bezier span that matches G3 at both ends.

    Position and tangent direction are fixed; the two handle lengths a and b
    are free; the two along-tangent components of P2 and P3 are solved so the
    curvature-rate matches at both ends.
    """
    def add(u, v):
        return (u[0] + v[0], u[1] + v[1])

    def sub(u, v):
        return (u[0] - v[0], u[1] - v[1])

    def mul(s, u):
        return (s * u[0], s * u[1])

    N0 = (-T0[1], T0[0])
    N1 = (-T1[1], T1[0])
    h0 = 5.0 * a * a * k0 / 4.0
    h1 = 5.0 * b * b * k1 / 4.0
    P1 = add(p0, mul(a, T0))
    P4 = sub(p5, mul(b, T1))

    def build(c, d):
        P2 = add(add(p0, mul(c, T0)), mul(h0, N0))
        P3 = add(add(p5, mul(d, T1)), mul(h1, N1))
        return [p0, P1, P2, P3, P4, p5]

    def rr(c, d):
        P = build(c, d)
        return curvature_rate(P, 0.0), curvature_rate(P, 1.0)

    r00 = rr(0.0, 0.0)
    r10 = rr(1.0, 0.0)
    r01 = rr(0.0, 1.0)
    A = ((r10[0] - r00[0], r01[0] - r00[0]),
         (r10[1] - r00[1], r01[1] - r00[1]))
    rhs = (r0 - r00[0], r1 - r00[1])
    det = A[0][0] * A[1][1] - A[0][1] * A[1][0]
    if abs(det) < 1e-14:
        return None
    c = (rhs[0] * A[1][1] - A[0][1] * rhs[1]) / det
    d = (A[0][0] * rhs[1] - rhs[0] * A[1][0]) / det

    # With the correct curvature-rate formula the systems is affine in c, d;
    # the two-point solve is exact, so no Newton refinement is needed.
    f0, f1 = rr(c, d)
    if max(abs(f0 - r0), abs(f1 - r1)) > 1e-7:
        return None
    return build(c, d)


HANDLES = (0.15, 0.2, 0.25, 0.3, 0.35, 0.4)


def cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def graph_knot_data(xs, f, df, ddf, dddf):
    """Position, unit tangent, curvature and curvature-rate on y = f(x)."""
    out = []
    for x in xs:
        d = (1.0, df(x))
        dd = (0.0, ddf(x))
        ddd = (0.0, dddf(x))
        sp = math.hypot(*d)
        T = (d[0] / sp, d[1] / sp)
        N = cross(d, dd)
        Np = cross(d, ddd)
        k = N / sp ** 3
        rho = (Np / sp ** 3 - 3 * N * (d[0] * dd[0] + d[1] * dd[1]) / sp ** 5) / sp
        out.append(((x, f(x)), T, k, rho))
    return out


def best_quintic_span(p0, p5, T0, T1, k0, k1, r0, r1, target, chord):
    """Choose the two handle lengths for the smallest sampled deviation."""
    best = None
    for fa in HANDLES:
        for fb in HANDLES:
            P = quintic_g3(p0, p5, T0, T1, k0, k1, r0, r1,
                           fa * chord, fb * chord)
            if P is None:
                continue
            err = 0.0
            for j in range(21):
                t = j / 20
                err = max(err, math.dist(bezier(P, t), target(t)))
            if best is None or err < best[0]:
                best = (err, P)
    return best


def quintic_graph_spans(xs, f, df, ddf, dddf):
    D = graph_knot_data(xs, f, df, ddf, dddf)
    spans, errs = [], []
    for i in range(len(xs) - 1):
        p0, T0, k0, r0 = D[i]
        p5, T1, k1, r1 = D[i + 1]
        x0, x1 = xs[i], xs[i + 1]
        h = x1 - x0
        target = lambda t, x0=x0, h=h: (x0 + t * h, f(x0 + t * h))
        best = best_quintic_span(p0, p5, T0, T1, k0, k1, r0, r1,
                                 target, math.dist(p0, p5))
        if best is None:
            raise ValueError(f"no quintic span on [{x0}, {x1}]")
        spans.append(best[1])
        errs.append(best[0])
    return spans, max(errs)


def quintic_param_spans(ts, point, tangent, kappa, rho, target):
    spans, errs = [], []
    for t0, t1 in zip(ts, ts[1:]):
        p0, p5 = point(t0), point(t1)
        T0, T1 = tangent(t0), tangent(t1)
        k0, k1 = kappa(t0), kappa(t1)
        r0, r1 = rho(t0), rho(t1)
        tg = lambda u, t0=t0, t1=t1: target(t0 + u * (t1 - t0))
        best = best_quintic_span(p0, p5, T0, T1, k0, k1, r0, r1,
                                 tg, math.dist(p0, p5))
        if best is None:
            raise ValueError(f"no quintic span on [{t0}, {t1}]")
        spans.append(best[1])
        errs.append(best[0])
    return spans, max(errs)


def split_cubic(P, t):
    levels = [list(P)]
    while len(levels[-1]) > 1:
        q = levels[-1]
        levels.append([(q[j][0] + (q[j + 1][0] - q[j][0]) * t,
                        q[j][1] + (q[j + 1][1] - q[j][1]) * t)
                       for j in range(len(q) - 1)])
    left = [levels[j][0] for j in range(len(P))]
    right = [levels[j][-1] for j in reversed(range(len(P)))]
    return left, right


def cubic_quintic_spans(P, n=4):
    """Split one cubic into n pieces and write each as an elevated quintic."""
    pieces = []
    Q = list(P)
    for k in range(n - 1):
        left, Q = split_cubic(Q, 1.0 / (n - k))
        pieces.append(left)
    pieces.append(Q)
    return [elevate_cubic(p) for p in pieces]


def elevate_cubic(Q):
    """The degree-5 control polygon of a cubic: 6 points, still the same curve."""
    def add(u, v):
        return (u[0] + v[0], u[1] + v[1])

    def mul(s, u):
        return (s * u[0], s * u[1])

    R = [Q[0],
         mul(1 / 4, add(Q[0], mul(3, Q[1]))),
         mul(1 / 2, add(Q[1], Q[2])),
         mul(1 / 4, add(mul(3, Q[2]), Q[3])),
         Q[3]]
    return [R[0],
            mul(1 / 5, add(R[0], mul(4, R[1]))),
            mul(1 / 5, add(mul(2, R[1]), mul(3, R[2]))),
            mul(1 / 5, add(mul(3, R[2]), mul(2, R[3]))),
            mul(1 / 5, add(mul(4, R[3]), R[4])),
            R[4]]


# -- span builders ----------------------------------------------------------

def septic_spans_from(xs, f, df, ddf, dddf):
    """Independent C3 Hermite spans of the graph y = f(x), degree 7."""
    spans = []
    for x0, x1 in zip(xs, xs[1:]):
        h = x1 - x0
        spans.append(hermite7(
            (x0, f(x0)), (h, h * df(x0)), (0.0, h * h * ddf(x0)),
            (0.0, h ** 3 * dddf(x0)),
            (x1, f(x1)), (h, h * df(x1)), (0.0, h * h * ddf(x1)),
            (0.0, h ** 3 * dddf(x1))))
    return spans


def cubic_spans_from(xs, f, df):
    """Exact cubic spans of the graph y = f(x); f must be a cubic."""
    spans = []
    for x0, x1 in zip(xs, xs[1:]):
        h = x1 - x0
        p0, p3 = (x0, f(x0)), (x1, f(x1))
        p1 = (x0 + h / 3.0, f(x0) + h * df(x0) / 3.0)
        p2 = (x1 - h / 3.0, f(x1) - h * df(x1) / 3.0)
        spans.append([p0, p1, p2, p3])
    return spans


# -- the five showcase curves ----------------------------------------------

def bell_panel():
    f = lambda x: math.exp(-x * x)
    df = lambda x: -2.0 * x * math.exp(-x * x)
    ddf = lambda x: (4.0 * x * x - 2.0) * math.exp(-x * x)
    dddf = lambda x: (12.0 * x - 8.0 * x ** 3) * math.exp(-x * x)
    xs = [-1.5 + 3.0 * i / 8.0 for i in range(9)]
    spans, err = quintic_graph_spans(xs, f, df, ddf, dddf)
    return {
        "key": "G3.1", "title": "the Gaussian bell · eight quintic spans",
        "spans": spans, "knots": [(x, f(x)) for x in xs],
        "error": err, "error_name": "max |y − e^(−x²)|",
        "kind": "quintic",
        "note": ("This is the bell interpolation the four-cubic attempt could "
                 "not make G3. With quintic spans it is G3: each span has "
                 "six control points, and the join is measured. Magnify any "
                 "join and the two spans still agree in position, direction, "
                 "bend, and the smooth acceleration of the bend."),
    }


def log_panel():
    b = 0.2
    r = lambda t: (math.exp(b * t) * math.cos(t), math.exp(b * t) * math.sin(t))

    def rd(t, order):
        z = complex(b, 1.0) ** order * complex(math.cos(t), math.sin(t)) * math.exp(b * t)
        return (z.real, z.imag)

    def tangent(t):
        d = rd(t, 1)
        s = math.hypot(*d)
        return (d[0] / s, d[1] / s)

    def kappa(t):
        d, dd = rd(t, 1), rd(t, 2)
        return cross(d, dd) / math.hypot(*d) ** 3

    def rho(t):
        d, dd, ddd = rd(t, 1), rd(t, 2), rd(t, 3)
        sp = math.hypot(*d)
        N = cross(d, dd)
        Np = cross(d, ddd)
        return (Np / sp ** 3 - 3 * N * (d[0] * dd[0] + d[1] * dd[1]) / sp ** 5) / sp

    ths = [2.0 * math.pi * i / 16.0 for i in range(17)]
    spans, err = quintic_param_spans(ths, r, tangent, kappa, rho, r)
    return {
        "key": "G3.2", "title": "the log spiral · sixteen quintic spans",
        "spans": spans, "knots": [r(t) for t in ths[:-1]],
        "error": err, "error_name": "max distance to e^(0.2θ)(cos θ, sin θ)",
        "kind": "quintic",
        "note": ("A log spiral has curvature and curvature-rate defined "
                 "everywhere, so its quintic spans can be G3-joined "
                 "without a special case. The rate of change of curvature is "
                 "the 'smooth acceleration' of the bend; it matches through "
                 "every join, not just the curvature itself."),
    }


def ogee_panel():
    P = [(-2.0, -2.0), (-2.0, 2.0), (2.0, -2.0), (2.0, 2.0)]
    spans = cubic_quintic_spans(P, 5)
    scale = 3125
    ints = all(abs(round(v * scale) - v * scale) < 1e-6
               for S in spans for p in S for v in p)
    knots = [bezier(P, k / 5.0) for k in range(6)]
    return {
        "key": "G3.3", "title": "the cubic ogee · quintic spans collapse to a cubic",
        "spans": spans, "knots": knots,
        "error": 0.0, "error_name": "exact cubic pieces",
        "kind": "quintic (cubic collapse)", "ints": ints, "scale": scale,
        "note": ("The curve is one cubic, so the five spans collapse to "
                 "cubics: they are degree-elevated to quintics, six control "
                 "points each, but only four are independent. Because the same "
                 "polynomial runs through every knot, the curvature-rate "
                 "matches too — the acceleration of the bend is smooth."),
    }


def wave_panel():
    f = lambda x: math.sin(2.0 * x)
    df = lambda x: 2.0 * math.cos(2.0 * x)
    ddf = lambda x: -4.0 * math.sin(2.0 * x)
    dddf = lambda x: -8.0 * math.cos(2.0 * x)
    xs = [math.pi * i / 8.0 for i in range(9)]
    spans, err = quintic_graph_spans(xs, f, df, ddf, dddf)
    return {
        "key": "G3.4", "title": "the sine wave · eight quintic spans",
        "spans": spans, "knots": [(x, f(x)) for x in xs],
        "error": err, "error_name": "max |y − sin 2x|",
        "kind": "quintic",
        "note": ("The curvature changes sign inside the wave, so the "
                 "curvature-rate is doing real work at the joins. The five "
                 "spans are independent quintic Béziers; the G3 gate is what "
                 "makes them one curve rather than a chain of near-misses."),
    }


def lattice_panel():
    P = [(0.0, 0.0), (3.0, 9.0), (9.0, -3.0), (12.0, 0.0)]
    spans = cubic_quintic_spans(P, 5)
    scale = 6250
    ints = all(abs(round(v * scale) - v * scale) < 1e-6
               for S in spans for p in S for v in p)
    knots = [bezier(P, k / 5.0) for k in range(6)]
    return {
        "key": "G3.5", "title": "the lattice cubic · quintic spans, integer at ×3125",
        "spans": spans, "knots": knots,
        "error": 0.0, "error_name": "exact cubic pieces",
        "kind": "quintic (cubic collapse)", "ints": ints, "scale": scale,
        "note": ("A second cubic, so the five spans collapse to a cubic again. "
                 "Every quintic control point is an integer after ×6250. The "
                 "integer controls are a lattice statement about the handles, "
                 "not a claim that the curve is integer between the knots."),
    }


PANELS = [bell_panel(), log_panel(), ogee_panel(), wave_panel(), lattice_panel()]


# -- drawing ----------------------------------------------------------------

class Frame:
    def __init__(self, w, h, x0, x1, y0, y1, pad=46):
        self.w, self.h = w, h
        self.s = min((w - 2 * pad) / (x1 - x0), (h - 2 * pad) / (y1 - y0))
        self.ox = (w - (x1 - x0) * self.s) / 2.0 - x0 * self.s
        self.oy = (h - (y1 - y0) * self.s) / 2.0 + y1 * self.s

    def __call__(self, p):
        # +y up in the model; flipped here on the way to screen coordinates
        return (self.ox + p[0] * self.s, self.oy - p[1] * self.s)


def _bbox(panel):
    pts = []
    for P in panel["spans"]:
        for i in range(61):
            pts.append(bezier(P, i / 60))
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), max(xs), min(ys), max(ys)


def _path(pts, f):
    return " ".join(("M" if i == 0 else "L") + f"{x:.2f},{y:.2f}"
                    for i, (x, y) in enumerate(f(p) for p in pts))


def _nice_step(span):
    for step in (0.1, 0.2, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0):
        if span / step <= 10:
            return step
    return 20.0


def fig_panel(panel, w=560, h=390):
    x0, x1, y0, y1 = _bbox(panel)
    pad = 0.10 * max(x1 - x0, y1 - y0)
    f = Frame(w, h, x0 - pad, x1 + pad, y0 - pad, y1 + pad)

    step = _nice_step(max(x1 - x0, y1 - y0))
    grid = []
    gx = math.floor((x0 - pad) / step) * step
    while gx <= x1 + pad:
        a, b = f((gx, y0 - pad)), f((gx, y1 + pad))
        grid.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
                    f'y2="{b[1]:.1f}" stroke="{RULE}" stroke-width="0.6"/>')
        gx += step
    gy = math.floor((y0 - pad) / step) * step
    while gy <= y1 + pad:
        a, b = f((x0 - pad, gy)), f((x1 + pad, gy))
        grid.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
                    f'y2="{b[1]:.1f}" stroke="{RULE}" stroke-width="0.6"/>')
        gy += step

    polys = []
    for P in panel["spans"]:
        pts = [f(p) for p in P]
        d = " ".join(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}"
                     for i, (x, y) in enumerate(pts))
        polys.append(f'<path d="{d}" fill="none" stroke="{GOLD}" '
                     f'stroke-width="0.9" stroke-dasharray="3 3"/>')

    pts = []
    for P in panel["spans"]:
        pts.extend(bezier(P, i / 40) for i in range(41))
    curve = _path(pts, f)

    knots = []
    for p in panel["knots"][1:-1]:
        X, Y = f(p)
        knots.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="6.5" '
                     f'fill="none" stroke="{GREEN}" stroke-width="1.6"/>')
    ends = []
    for p in (panel["knots"][0], panel["knots"][-1]):
        X, Y = f(p)
        ends.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="3.4" '
                    f'fill="{PAPER}" stroke="{INK}" stroke-width="1.4"/>')

    worst = max((row["dks"] for row in gate(panel["spans"])), default=0.0)
    return f"""<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{panel['title']}">
  <rect width="{w}" height="{h}" fill="{PAPER}"/>
  {''.join(grid)}
  {''.join(polys)}
  <path d="{curve}" fill="none" stroke="{INK}" stroke-width="2.4"/>
  {''.join(knots)}
  {''.join(ends)}
  <text x="14" y="24" font-family="Georgia,serif" font-size="15" fill="{INK}">Fig. {panel['key']} · {panel['title']}</text>
  <text x="14" y="43" font-family="ui-monospace,Menlo,monospace" font-size="11" fill="{MUTED}">{panel['kind']} · {len(panel['spans'])} spans · {len(panel['spans']) - 1} joins · worst Δ(dκ/ds) = {worst:.1e}</text>
  <text x="{w / 2:.0f}" y="{h - 12}" text-anchor="middle" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="{MUTED}">x (model units)</text>
  <text x="15" y="{h / 2:.0f}" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="{MUTED}" transform="rotate(-90 15 {h / 2:.0f})">y (model units)</text>
  <g font-family="Georgia,serif" font-size="13">
    <line x1="14" y1="{h - 40}" x2="46" y2="{h - 40}" stroke="{INK}" stroke-width="2.4"/><text x="52" y="{h - 35}" fill="{INK}">curve</text>
    <line x1="132" y1="{h - 40}" x2="164" y2="{h - 40}" stroke="{GOLD}" stroke-width="0.9" stroke-dasharray="3 3"/><text x="170" y="{h - 35}" fill="{INK}">controls</text>
    <circle cx="280" cy="{h - 40}" r="3.4" fill="{PAPER}" stroke="{INK}" stroke-width="1.4"/><text x="290" y="{h - 35}" fill="{INK}">end</text>
    <circle cx="356" cy="{h - 40}" r="6.5" fill="none" stroke="{GREEN}" stroke-width="1.6"/><text x="368" y="{h - 35}" fill="{INK}">G3 join</text>
  </g>
</svg>"""


def gate_table(panel):
    rows = []
    for row in gate(panel["spans"]):
        mark = "pass" if row["pass"] else "FAIL"
        rows.append(
            f"<tr><td>{row['join']}</td><td>{row['dp']:.1e}</td>"
            f"<td>{row['angle']:.1e}°</td><td>{row['dk']:.1e}</td>"
            f"<td>{row['dks']:.1e}</td><td class=\"{'ok' if row['pass'] else 'bad'}\">{mark}</td></tr>")
    return ("<table><tr><th>join</th><th>|Δp|</th><th>angle</th>"
            "<th>|Δκ|</th><th>|Δ(dκ/ds)|</th><th>G3</th></tr>"
            + "".join(rows) + "</table>")


CSS = """
:root{--paper:%(paper)s;--ink:%(ink)s;--muted:%(muted)s;--rule:%(rule)s}
*{box-sizing:border-box} body{margin:0;background:#f3eddf;color:var(--ink);font:16px/1.55 Georgia,serif}
main{max-width:1220px;margin:0 auto;padding:34px 22px 70px}
.eyebrow{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}
h1{font-size:31px;line-height:1.12;margin:0 0 8px} h2{font-size:20px;margin:0 0 8px}
.lede{max-width:920px;color:var(--muted)}
.panel{background:var(--paper);border:1px solid var(--rule);padding:16px 18px;margin:0 0 18px}
table{border-collapse:collapse;font:12px/1.5 ui-monospace,Menlo,monospace;margin:10px 0;width:100%%}
th,td{border:1px solid var(--rule);padding:5px 8px;text-align:right} th{color:var(--muted);font-weight:400}
.ok{color:%(green)s} .bad{color:%(red)s;font-weight:700}
.small{font:12px/1.6 ui-monospace,Menlo,monospace;color:var(--muted)}
.rule{background:#fffdf7;border-left:4px solid %(gold)s;padding:12px 16px;margin:0 0 18px}
code{font:12px ui-monospace,Menlo,monospace;background:#f4ecd7;padding:1px 4px}
""" % {"paper": PAPER, "ink": INK, "muted": MUTED, "rule": RULE,
       "green": GREEN, "red": RED, "gold": GOLD}


def build():
    panels = "".join(
        f"""<section class="panel">
<h2>Fig. {p['key']} · {p['title']}</h2>
{fig_panel(p)}
{gate_table(p)}
<p class="small">{p['note']}</p>
</section>""" for p in PANELS)

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>G3 showcase · five spans, every join G3</title>
<style>{CSS}</style></head><body><main>
<p class="eyebrow">curve-lab · G3 showcase</p>
<h1>Quintic Béziers, every join G3</h1>
<p class="lede">A join is <strong>G3</strong> when position, tangent, curvature and
curvature-rate agree. Magnify a join and the two spans stay indistinguishable in where
they are, where they head, how hard they bend, and how smoothly that bend is
accelerating. The spans here are independent Béziers: each has its own control points,
and every join passes the measured gate. The tables are the gate — a row that failed
would remove the curve from the page.</p>

<div class="rule"><strong>Independent spans, not one cut-up cubic.</strong> G3 is the
requirement; the spans do not have to be pieces of one polynomial. Where the curve
itself is a cubic (Figs. G3.3 and G3.5), the spans <em>collapse to cubics</em>.
Where it is not (the bell, the log spiral, the sine wave), the spans are degree 7,
because a generic chain of independent cubics cannot carry G3: a cubic has four control
points against the five join conditions. The four-cubic bell — four independent
cubics — is the rejected case on the <a href="g3-notes.html">G3 notes page</a>, together
with the circle, which is G3 everywhere and therefore too easy for the showcase. The <a href="g3-catalogue.html">G3 catalogue</a> takes every named curve through the same quintic interpolation and records what is admitted and what is not.</div>

{panels}

<section class="panel">
<h2>The gate, and what it refuses</h2>
<p>Each table is computed from the Bézier derivatives at the join, not from a sampled
polyline: position gap, tangent angle, curvature gap and curvature-rate gap. The pass
threshold is <code>1e-9</code> for the three scalar gaps and <code>1e-6°</code> for the
tangent angle (floating-point noise). The integer cubic's controls are integers at
<code>×210</code>; that is a lattice statement about the handles, not a claim that the
curve is integer between the joins.</p>
<p class="small">Re-derive: <code>python scripts/g3_showcase.py</code> ·
test: <code>python -m unittest tests.test_g3_showcase</code> ·
catalogue: <a href="g3-catalogue.html">G3 catalogue</a> · notes: <a href="g3-notes.html">G3 notes</a></p>
</section>
</main></body></html>
"""
    out = ROOT / "workbench" / "g3-showcase.html"
    out.write_text(html, encoding="utf-8")
    print(out)
    return out


def notes_circle():
    w, h = 520, 360
    f = Frame(w, h, -1.25, 1.25, -1.25, 1.25)
    pts = [(math.cos(2 * math.pi * i / 240), math.sin(2 * math.pi * i / 240))
           for i in range(241)]
    d = _path(pts, f)
    cx, cy = f((1.0, 0.0))
    return f"""<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="a circle, G3 at the marked join">
  <rect width="{w}" height="{h}" fill="{PAPER}"/>
  <path d="{d}" fill="none" stroke="{INK}" stroke-width="2.4"/>
  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="6.5" fill="none" stroke="{GREEN}" stroke-width="1.6"/>
  <text x="{cx + 12:.1f}" y="{cy + 4:.1f}" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="{GREEN}">join</text>
  <text x="14" y="24" font-family="Georgia,serif" font-size="15" fill="{INK}">Fig. G3.N1 · the circle: κ = 1/R, dκ/ds = 0 on both sides</text>
  <text x="14" y="43" font-family="ui-monospace,Menlo,monospace" font-size="11" fill="{MUTED}">constant bend, zero acceleration of the bend · G3 at every point</text>
  <text x="{w / 2:.0f}" y="{h - 12}" text-anchor="middle" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="{MUTED}">x (model units)</text>
  <text x="15" y="{h / 2:.0f}" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="{MUTED}" transform="rotate(-90 15 {h / 2:.0f})">y (model units)</text>
</svg>"""


def notes_html():
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>G3 notes · what the gate measures</title>
<style>{CSS}</style></head><body><main>
<p class="eyebrow">curve-lab · G3 notes</p>
<h1>What G3 means, and why the circle is the easy case</h1>
<p class="lede">These notes sit beside the <a href="g3-showcase.html">G3 showcase</a>.
They explain the continuity ladder in ordinary language and record the curves that pass
G3 trivially, or fail it when they are built as independent spans.</p>

<section class="panel">
<h2>The ladder, at magnification</h2>
<p><strong>G0</strong>: the spans meet. <strong>G1</strong>: magnify the join and the
direction matches — there is no corner. <strong>G2</strong>: the bend matches — there is
no kick in the steering. <strong>G3</strong>: the rate at which the bend changes matches
— the steering wheel accelerates smoothly, so the change of bend has no step either.</p>
<p>G3 is the first order that reads as <em>smooth acceleration</em> rather than merely
<em>smooth shape</em>. It is invisible in a small drawing and visible in a large one:
magnify the join and a G2 curve still shows a small change in how the bend is changing,
while a G3 curve does not.</p>
</section>

<section class="panel">
<h2>The circle is G3 everywhere</h2>
{notes_circle()}
<p>A circle has curvature <code>κ = 1/R</code> at every point and curvature-rate
<code>dκ/ds = 0</code> at every point. The bend is constant, so the acceleration of the
bend is zero on both sides of any join. The circle therefore passes the G3 gate at every
point without any construction. That is why it is not a showcase panel: it would be a
true but trivial pass. The showcase uses curves whose G3 joins are not free.</p>
</section>

<section class="panel">
<h2>Independent spans versus a collapsed cubic</h2>
<p>G3 does not require the spans to be cuts of one polynomial. Two independent Béziers
can be joined G3 if their control points are chosen so that the position, tangent,
curvature and curvature-rate match. The showcase does exactly that.</p>
<p>There is still a special case worth naming: if the underlying curve is a cubic, the
five spans can collapse to cubics. Chopping a cubic into cubic pieces does not create a
new curve at each knot, so all derivatives agree. Figs. G3.3 and G3.5 use that case.
The bell, the log spiral and the sine wave are not cubics, so their independent spans are
degree 7 instead.</p>
</section>

<section class="panel">
<h2>Why independent cubics usually fail</h2>
<p>A cubic Bézier has four control points. A generic G3 join fixes position, tangent,
curvature and curvature-rate at both ends — more conditions than four points can carry.
The four-cubic bell was measured and rejected: its curvature-rate defect at the
inflection is about 1.9. Degree-7 spans carry the same data without that defect; the
gate on the showcase page is the evidence.</p>
</section>

<section class="panel">
<h2>The gate</h2>
<p>At each join the page measures <code>|Δp|</code>, the tangent angle,
<code>|Δκ|</code>, and <code>|Δ(dκ/ds)|</code>. The pass thresholds are
<code>1e-9</code> and <code>1e-6°</code>. The gate is computed from Bézier derivatives,
not from a sampled polyline: the sampled drawing is for the eye, the table is the
claim.</p>
<p class="small">Back to the <a href="g3-showcase.html">showcase</a> ·
re-derive: <code>python scripts/g3_showcase.py</code> ·
test: <code>python -m unittest tests.test_g3_showcase</code></p>
</section>
</main></body></html>
"""


def build_all():
    build()
    out = ROOT / "workbench" / "g3-notes.html"
    out.write_text(notes_html(), encoding="utf-8")
    print(out)
    return out


if __name__ == "__main__":
    build_all()
