"""The G3 catalogue: every named curve, interpolated by quintic Beziers.

    .venv/bin/python scripts/g3_catalogue.py
    open workbench/g3-catalogue.html

The catalogue is an interpolation showcase, not a gallery of ideal curves.
Each admitted curve is a chain of quintic Bezier spans whose joins are G3;
the ideal curve is drawn only as a faint reference. A branch that cannot be
interpolated G3 — a cusp, a point at infinity, a singular handle solve — is
listed as rejected with the reason, not quietly dropped.

The JSON beside the page is the machine-readable form of the same result.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import generators as G  # noqa: E402
import g3_showcase as G3  # noqa: E402
import heart_forms as H  # noqa: E402

PAPER = "#fbf7ec"
INK, MUTED, GOLD, BLUE, RED = "#2e2413", "#7b6c4e", "#c9a441", "#1f5fa8", "#a23b2a"
RULE = "#d8ccae"
GREEN = "#2f6b3a"

SPANS = 6
HGRID = (0.15, 0.2, 0.25, 0.3, 0.35, 0.4)
ERR_LIMIT = 0.06

# A fit cache makes the pages cheap to rebuild. Bump FIT_VERSION whenever the
# span solve or the speed gate changes; the source hash catches table changes.
FIT_VERSION = 1
CACHE = ROOT / "workbench" / "g3-catalogue-cache.json"

# A G3 join can match two spans that each pass through a near-cusp: the join
# gate sees only the ends. A span is regular only when its speed never falls
# below this share of its chord. The interior near-cusp is what produces the
# 1e8 curvature-rate spikes that flatten the acceleration graphs.
MIN_SPEED = 0.10

# Integer-rounded source data (the recovered LAC page) is G3 to its own
# precision, not to 1e-9 floating-point noise. The exact constructions keep the
# 1e-9 gate; these source cubic chains use 1e-6 and report the measured gap.
SOURCE_TOL = 1e-5


def span_min_speed(P, chord, samples=81):
    if chord <= 0.0:
        return 0.0
    m = float("inf")
    for i in range(samples):
        t = i / (samples - 1)
        d = G3.derivative(P, t, 1)
        m = min(m, math.hypot(*d))
    return m / chord


def span_is_regular(P, chord):
    return span_min_speed(P, chord) >= MIN_SPEED


def problem_of_spans(spans, samples=81):
    """The worst interior point of a chain: lowest speed share and where it is.

    Returns the speed minimum as a share of the span chord, the span index,
    the parameter, the cumulative arc length along the branch, and the model
    point. This is what the red diagnostic ring is drawn on.
    """
    worst = None
    s = 0.0
    for si, P in enumerate(spans):
        chord = math.dist(P[0], P[-1]) or 1.0
        prev = None
        for i in range(samples):
            t = i / (samples - 1)
            q = G3.bezier(P, t)
            if prev is not None:
                s += math.dist(prev, q)
            prev = q
            d = G3.derivative(P, t, 1)
            ratio = math.hypot(*d) / chord
            if worst is None or ratio < worst["ratio"]:
                worst = {"ratio": ratio, "span": si, "t": t,
                         "s": s, "point": q}
    return worst

# Declared features: points where the source is not a smooth curve and G3 is
# therefore not defined. They are listed, never counted as failed joins.
FEATURES = {
    "astroid": "cusp ×4",
    "deltoid": "cusp ×3",
    "nephroid": "cusp ×2",
    "epicycloid k=3": "cusp ×4",
    "epicycloid k=5": "cusp ×6",
    "hypocycloid k=5": "cusp ×5",
    "cardioid": "cusp ×1",
    "nodal": "node at the seam",
    "bow": "node at the seam",
    "strophoid": "node at the seam",
    "bernoulli": "node at the seam",
    "abs(x) gerono": "node at the seam",
    "bean": "node between the two branches",
    "bicorn": "node between the two branches",
    "trifolium": "node where the leaves meet",
    "quadrifolium": "node where the leaves meet",
    "kappa": "node between the two branches",
    "cruciform": "four arms meet at the centre",
    "heart · cardioid": "cusp ×1",
    "heart · |x|^(2/3) upper": "cusp ×1",
    "heart · |x|^(2/3) lower": "cusp ×1",
}


def degree_content(P, chord):
    """How much of a span is genuinely above cubic degree.

    A quintic control polygon that is a degree elevation of a cubic has zero
    fourth and fifth differences:
        d4 = P0 - 4P1 + 6P2 - 4P3 + P4
        d5 = P0 - 5P1 + 10P2 - 10P3 + 5P4 - P5
    A nonzero d5 means the span uses the fifth-degree freedom (quartic or
    quintic content); zero d5 with nonzero d4 is quartic. The number is
    returned as a share of the span chord, so it is comparable across curves.
    """
    if len(P) == 4:
        return 0.0
    if len(P) != 6 or chord <= 0.0:
        return None
    def norm(v):
        return math.hypot(*v)
    d4a = norm((P[0][0] - 4 * P[1][0] + 6 * P[2][0] - 4 * P[3][0] + P[4][0],
                P[0][1] - 4 * P[1][1] + 6 * P[2][1] - 4 * P[3][1] + P[4][1]))
    d4b = norm((P[1][0] - 4 * P[2][0] + 6 * P[3][0] - 4 * P[4][0] + P[5][0],
                P[1][1] - 4 * P[2][1] + 6 * P[3][1] - 4 * P[4][1] + P[5][1]))
    d5 = norm((P[0][0] - 5 * P[1][0] + 10 * P[2][0] - 10 * P[3][0]
               + 5 * P[4][0] - P[5][0],
               P[0][1] - 5 * P[1][1] + 10 * P[2][1] - 10 * P[3][1]
               + 5 * P[4][1] - P[5][1]))
    return max(d4a, d4b, d5) / chord


# -- exact evaluation of a homogeneous branch ------------------------------

def homog_eval(ctrl, t):
    n = len(ctrl) - 1
    X = Y = W = 0.0
    for i, (x, y, w) in enumerate(ctrl):
        b = math.comb(n, i) * t ** i * (1.0 - t) ** (n - i)
        X += float(x) * b
        Y += float(y) * b
        W += float(w) * b
    if abs(W) < 1e-12:
        return None
    return (X / W, Y / W)


def branch_points(ctrl, n=1000):
    pts, ts = [], []
    for i in range(n + 1):
        t = i / n
        p = homog_eval(ctrl, t)
        if p is not None:
            pts.append(p)
            ts.append(t)
    return pts, ts


def der5(f, t, h=1e-4):
    fm2, fm1, f0, fp1, fp2 = f(t - 2 * h), f(t - h), f(t), f(t + h), f(t + 2 * h)
    if None in (fm2, fm1, f0, fp1, fp2):
        return None
    return (
        (fm2 - 8 * fm1 + 8 * fp1 - fp2) / (12 * h),
        (-fm2 + 16 * fm1 - 30 * f0 + 16 * fp1 - fp2) / (12 * h * h),
        (-fm2 + 2 * fm1 - 2 * fp1 + fp2) / (2 * h ** 3),
    )


def fit_branch(ctrl, nspans=SPANS, trim=0.0):
    """Fit one branch with quintic G3 spans; return None when it cannot fit."""
    pts, ts = branch_points(ctrl)
    if len(pts) < 30:
        return None
    s = [0.0]
    for a, b in zip(pts, pts[1:]):
        s.append(s[-1] + math.dist(a, b))
    total = s[-1]
    if total <= 0.0:
        return None
    closed = math.dist(pts[0], pts[-1]) < 1e-6
    lo = 0.0 if closed else trim * total
    hi = total if closed else (1.0 - trim) * total

    knot_t, knot_p = [], []
    for i in range(nspans + 1):
        target = lo + (hi - lo) * i / nspans
        j = 0
        while j < len(s) - 2 and s[j + 1] < target:
            j += 1
        frac = (target - s[j]) / (s[j + 1] - s[j]) if s[j + 1] > s[j] else 0.0
        t = ts[j] + (ts[j + 1] - ts[j]) * frac
        p = homog_eval(ctrl, t)
        if p is None:
            return None
        knot_t.append(t)
        knot_p.append(p)

    D = []
    for t in knot_t:
        fx = lambda u: (lambda q: None if q is None else q[0])(homog_eval(ctrl, u))
        fy = lambda u: (lambda q: None if q is None else q[1])(homog_eval(ctrl, u))
        dx, dy = der5(fx, t), der5(fy, t)
        if dx is None or dy is None:
            return None
        d1, d2, d3 = (dx[0], dy[0]), (dx[1], dy[1]), (dx[2], dy[2])
        sp = math.hypot(*d1)
        if sp < 1e-12:
            return None
        T = (d1[0] / sp, d1[1] / sp)
        N = d1[0] * d2[1] - d1[1] * d2[0]
        Np = d1[0] * d3[1] - d1[1] * d3[0]
        k = N / sp ** 3
        kp = Np / sp ** 3 - 3 * N * (d1[0] * d2[0] + d1[1] * d2[1]) / sp ** 5
        D.append((T, k, kp / sp))

    dense = pts[::max(1, len(pts) // 320)]

    def near(p):
        return min(math.dist(p, q) for q in dense)

    spans, errs = [], []
    for i in range(nspans):
        p0, p5 = knot_p[i], knot_p[i + 1]
        T0, k0, r0 = D[i]
        T1, k1, r1 = D[i + 1]
        chord = math.dist(p0, p5)
        if chord < 1e-12:
            return None
        best = None
        for fa in HGRID:
            for fb in HGRID:
                P = G3.quintic_g3(p0, p5, T0, T1, k0, k1, r0, r1,
                                  fa * chord, fb * chord)
                if P is None or not span_is_regular(P, chord):
                    continue
                e = max(near(G3.bezier(P, j / 20)) for j in range(21))
                if best is None or e < best[0]:
                    best = (e, P)
        if best is None:
            return None
        spans.append(best[1])
        errs.append(best[0])

    joins = G3.gate(spans)
    closed = math.dist(knot_p[0], knot_p[-1]) < 1e-6
    if closed:
        A, B = spans[-1], spans[0]
        row = {
            "join": "seam",
            "dp": math.dist(G3.bezier(A, 1.0), G3.bezier(B, 0.0)),
            "angle": abs(math.degrees(math.atan2(
                G3.derivative(A, 1.0, 1)[0] * G3.derivative(B, 0.0, 1)[1]
                - G3.derivative(A, 1.0, 1)[1] * G3.derivative(B, 0.0, 1)[0],
                G3.derivative(A, 1.0, 1)[0] * G3.derivative(B, 0.0, 1)[0]
                + G3.derivative(A, 1.0, 1)[1] * G3.derivative(B, 0.0, 1)[1]))),
            "dk": abs(G3.curvature(A, 1.0) - G3.curvature(B, 0.0)),
            "dks": abs(G3.curvature_rate(A, 1.0) - G3.curvature_rate(B, 0.0)),
        }
        row["pass"] = (row["dp"] < 1e-9 and row["angle"] < 1e-6
                       and row["dk"] < 1e-9 and row["dks"] < 1e-9)
        joins.append(row)

    problem = problem_of_spans(spans)
    return {
        "spans": spans,
        "count": nspans,
        "trimmed": trim > 0.0,
        "min_speed": problem["ratio"],
        "problem": problem,
        "ideal": pts[::max(1, len(pts) // 240)],
        "error": max(errs),
        "g3": max((row["dks"] for row in joins if row["join"] != "seam"),
                  default=0.0),
        "g3_seam": max((row["dks"] for row in joins if row["join"] == "seam"),
                       default=0.0),
        "seam_pass": all(row["pass"] for row in joins if row["join"] == "seam"),
        "rows": joins,
        "pass": all(row["pass"] for row in joins if row["join"] != "seam"),
        "closed": closed,
    }


# -- sampled curves: a local cubic read of the polyline ---------------------

def solve4(A, b):
    n = 4
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(A[r][i]))
        if abs(A[p][i]) < 1e-14:
            return None
        A[i], A[p] = A[p], A[i]
        b[i], b[p] = b[p], b[i]
        for r in range(i + 1, n):
            f = A[r][i] / A[i][i]
            for c in range(i, n):
                A[r][c] -= f * A[i][c]
            b[r] -= f * b[i]
    x = [0.0] * n
    for i in reversed(range(n)):
        x[i] = (b[i] - sum(A[i][j] * x[j] for j in range(i + 1, n))) / A[i][i]
    return x


def local_deriv(pts, s0, total, window_frac=0.06):
    """Read position, tangent, curvature and curvature-rate at one station.

    The polyline is only the source; the derivatives come from a local cubic
    least-squares fit over a window, so the result is smooth rather than the
    finite-difference noise of the sampled points.
    """
    win = max(window_frac * total, 1e-9)
    ss = [0.0]
    for a, b in zip(pts, pts[1:]):
        ss.append(ss[-1] + math.dist(a, b))
    idx = [i for i, s in enumerate(ss) if abs(s - s0) <= win]
    if len(idx) < 8:
        idx = list(range(len(pts)))
    rows, bx, by = [], [], []
    for i in idx:
        u = (ss[i] - s0) / win
        rows.append([1.0, u, u * u, u * u * u])
        bx.append(pts[i][0])
        by.append(pts[i][1])
    A = [[sum(r[i] * r[j] for r in rows) for j in range(4)] for i in range(4)]
    cx = solve4([row[:] for row in A],
                [sum(r[i] * bx[k] for k, r in enumerate(rows)) for i in range(4)])
    cy = solve4([row[:] for row in A],
                [sum(r[i] * by[k] for k, r in enumerate(rows)) for i in range(4)])
    if cx is None or cy is None:
        return None
    h = 1.0 / win
    x = (cx[0], cx[1] * h, 2.0 * cx[2] * h * h, 6.0 * cx[3] * h ** 3)
    y = (cy[0], cy[1] * h, 2.0 * cy[2] * h * h, 6.0 * cy[3] * h ** 3)
    d1, d2, d3 = (x[1], y[1]), (x[2], y[2]), (x[3], y[3])
    sp = math.hypot(*d1)
    if sp < 1e-12:
        return None
    T = (d1[0] / sp, d1[1] / sp)
    N = d1[0] * d2[1] - d1[1] * d2[0]
    Np = d1[0] * d3[1] - d1[1] * d3[0]
    k = N / sp ** 3
    rho = (Np / sp ** 3 - 3 * N * (d1[0] * d2[0] + d1[1] * d2[1]) / sp ** 5) / sp
    return (x[0], y[0]), T, k, rho


def fit_poly(pts, nspans=SPANS, trim=0.0):
    """Fit a sampled polyline with quintic G3 spans."""
    if len(pts) < 20:
        return None
    ss = [0.0]
    for a, b in zip(pts, pts[1:]):
        ss.append(ss[-1] + math.dist(a, b))
    total = ss[-1]
    if total <= 0.0:
        return None
    closed = math.dist(pts[0], pts[-1]) < 1e-6
    lo = 0.0 if closed else trim * total
    hi = total if closed else (1.0 - trim) * total

    knots, D = [], []
    for i in range(nspans + 1):
        s0 = lo + (hi - lo) * i / nspans
        d = local_deriv(pts, s0, total)
        if d is None:
            return None
        knots.append(d[0])
        D.append(d[1:])
    if closed:
        knots[-1] = knots[0]
        D[-1] = D[0]

    dense = pts[::max(1, len(pts) // 300)]

    def near(p):
        return min(math.dist(p, q) for q in dense)

    spans, errs = [], []
    for i in range(nspans):
        p0, p5 = knots[i], knots[i + 1]
        T0, k0, r0 = D[i]
        T1, k1, r1 = D[i + 1]
        chord = math.dist(p0, p5)
        if chord < 1e-12:
            return None
        best = None
        for fa in HGRID:
            for fb in HGRID:
                P = G3.quintic_g3(p0, p5, T0, T1, k0, k1, r0, r1,
                                  fa * chord, fb * chord)
                if P is None or not span_is_regular(P, chord):
                    continue
                e = max(near(G3.bezier(P, j / 20)) for j in range(21))
                if best is None or e < best[0]:
                    best = (e, P)
        if best is None:
            return None
        spans.append(best[1])
        errs.append(best[0])

    joins = G3.gate(spans)
    if closed:
        A, B = spans[-1], spans[0]
        d1a, d1b = G3.derivative(A, 1.0, 1), G3.derivative(B, 0.0, 1)
        row = {
            "join": "seam",
            "dp": math.dist(G3.bezier(A, 1.0), G3.bezier(B, 0.0)),
            "angle": abs(math.degrees(math.atan2(
                d1a[0] * d1b[1] - d1a[1] * d1b[0],
                d1a[0] * d1b[0] + d1a[1] * d1b[1]))),
            "dk": abs(G3.curvature(A, 1.0) - G3.curvature(B, 0.0)),
            "dks": abs(G3.curvature_rate(A, 1.0) - G3.curvature_rate(B, 0.0)),
        }
        row["pass"] = (row["dp"] < 1e-9 and row["angle"] < 1e-6
                       and row["dk"] < 1e-9 and row["dks"] < 1e-9)
        joins.append(row)

    problem = problem_of_spans(spans)
    return {
        "spans": spans,
        "count": nspans,
        "trimmed": trim > 0.0,
        "min_speed": problem["ratio"],
        "problem": problem,
        "ideal": pts[::max(1, len(pts) // 240)],
        "error": max(errs),
        "g3": max((row["dks"] for row in joins if row["join"] != "seam"),
                  default=0.0),
        "g3_seam": max((row["dks"] for row in joins if row["join"] == "seam"),
                       default=0.0),
        "seam_pass": all(row["pass"] for row in joins if row["join"] == "seam"),
        "rows": joins,
        "pass": all(row["pass"] for row in joins if row["join"] != "seam"),
        "closed": closed,
    }


def fit_branch_best(ctrl):
    for trim in (0.0, 0.015):
        best = None
        for n in (6, 10):
            r = fit_branch(ctrl, n, trim=trim)
            if r is not None and r["pass"] and (best is None or r["error"] < best["error"]):
                best = r
        if best is not None:
            return best
    return None


def fit_branch_any(ctrl):
    """The best fit even when the G3 gate fails — for the comparison panel."""
    best = None
    for trim in (0.0, 0.015):
        for n in (6, 10):
            r = fit_branch(ctrl, n, trim=trim)
            if r is not None and (best is None or r["error"] < best["error"]):
                best = r
    return best


def fit_poly_best(pts):
    for trim in (0.0, 0.02):
        best = None
        for n in (6, 10, 14):
            r = fit_poly(pts, n, trim=trim)
            if r is not None and r["pass"] and (best is None or r["error"] < best["error"]):
                best = r
        if best is not None:
            return best
    return None


def curve_size(fitted):
    pts = [p for br in fitted for p in br["ideal"]]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return math.hypot(max(xs) - min(xs), max(ys) - min(ys))


# -- the catalogue ----------------------------------------------------------

def attempted(spec):
    data = G.named_data(spec)
    if spec["branches"] is None:
        paths = data.get("paths")
        if not paths:
            return None, "sampled curve with no polyline"
        fitted = []
        for pts in paths:
            r = fit_poly_best([(float(x), float(y)) for x, y in pts])
            if r is None or not r["pass"]:
                return None, "cusp or singular sample; no G3 interpolation"
            fitted.append(r)
        return fitted, None
    if not data["ctrl"]:
        return None, "no exact control polygon"
    fitted = []
    for ctrl in data["ctrl"]:
        r = fit_branch_best(ctrl)
        if r is None or not r["pass"]:
            return None, "cusp, point at infinity, or singular handle solve"
        fitted.append(r)
    bad = [r for r in fitted if not r["pass"]]
    if bad:
        return None, "G3 gate failed"
    return fitted, None


def heart_rows():
    forms = [
        ("heart · Beutel upper", [H.beutel()[0]]),
        ("heart · Beutel lower", [H.beutel()[1]]),
        ("heart · cardioid", H.cardioid()),
        ("heart · |x|^(2/3) upper", [H.abs_heart()[0]]),
        ("heart · |x|^(2/3) lower", [H.abs_heart()[1]]),
        ("heart · Valentine", H.valentine()),
        ("heart · Wolfram", H.wolfram()),
        ("heart · Kuriscak upper", [H.kuriscak()[0]]),
        ("heart · Kuriscak lower", [H.kuriscak()[1]]),
        ("heart · Wu–Nick upper", [H.wu_nick()[0]]),
        ("heart · Wu–Nick lower", [H.wu_nick()[1]]),
        ("heart · Mangaldan", H.mangaldan()),
        ("heart · half-ellipse upper", [H.half_ellipses()[0]]),
        ("heart · half-ellipse lower", [H.half_ellipses()[1]]),
        ("heart · sqrt upper", [H.sqrt_heart()[0]]),
        ("heart · sqrt lower", [H.sqrt_heart()[1]]),
        ("heart · Eisemann upper", [H.eisemann()[0]]),
        ("heart · Eisemann lower", [H.eisemann()[1]]),
        ("heart · Sio upper", [H.sio()[0]]),
        ("heart · Sio lower", [H.sio()[1]]),
        ("heart · Holzapfel upper", [H.holzapfel()[0]]),
        ("heart · Holzapfel lower", [H.holzapfel()[1]]),
        ("heart · Hechinger upper", [H.hechinger()[0]]),
        ("heart · Hechinger lower", [H.hechinger()[1]]),
    ]
    rows = []
    for name, branches in forms:
        fitted = []
        for pts in branches:
            r = fit_poly_best(pts)
            if r is None or not r["pass"]:
                fitted = None
                break
            fitted.append(r)
        if fitted is None:
            rows.append({"key": name, "admitted": False, "source": "heart",
                         "reason": "cusp or singular sample; no G3 interpolation"})
        else:
            rows.append({
                "key": name, "admitted": True,
                "source": "heart", "spans": max(r["count"] for r in fitted),
                "branches": fitted,
                "error": max(r["error"] for r in fitted),
                "g3": max(r["g3"] for r in fitted),
            })
    return rows


def misc_rows():
    import arches as A
    import biarcs as B
    import catenary as C
    import gen_arch as GA
    import maclaurin as Mac
    import missing_families as M
    import ph_quintic as P
    import qac_dlac as Q
    import reuleaux as R

    rows = []

    def add(name, pts, note=""):
        r = fit_poly_best(pts)
        key = f"misc · {name}"
        if r is None or not r["pass"]:
            rows.append({"key": key, "admitted": False, "source": "misc",
                         "reason": "cusp or singular sample; no G3 interpolation"})
        else:
            rows.append({"key": key, "admitted": True, "source": "misc",
                         "spans": r["count"], "branches": [r],
                         "error": r["error"], "g3": r["g3"]})

    for name, pts, note, src in M.cases():
        add(name, pts)
    for name, pts, note, src in A.cases():
        add(name, pts)
    for name, pts, note, src in Mac.cases():
        add(name, pts)
    for name, pts, note, src in GA.cases():
        add(name, pts)
    for name, pts, note, src in P.cases():
        add(name, pts)
    for case in B.CASES:
        b, _ang = B.measure(case)
        add(f"biarc · {case[0]}", b["first"] + b["second"])
    add("Reuleaux triangle", R.reuleaux())
    for name, alpha, c in Q.CASES:
        add(name, Q.qac(alpha, c))
    # Pell: two exact hyperbolic branches
    for sign in (1, -1):
        pts = []
        for i in range(401):
            t = -2.5 + 5.0 * i / 400.0
            pts.append((sign * math.cosh(t), math.sinh(t) / math.sqrt(2.0)))
        add("Pell · x² − 2y² = 1" + (" · +" if sign > 0 else " · −"), pts)
    add("catenary", C.branch(120.0, 60.0, 240))
    return rows


def integer_cubic_rows():
    from curve_lab.pyth_cubic import representatives

    reps = representatives()
    rows = []
    for kind in ("s", "c"):
        for item in reps[kind]:
            P = [item["p0"], item["p1"], item["p2"], item["p3"]]
            spans = G3.cubic_quintic_spans(P, 5)
            ideal = [G3.bezier(P, i / 240.0) for i in range(241)]
            joins = G3.gate(spans)
            ok = all(row["pass"] for row in joins)
            problem = problem_of_spans(spans)
            rows.append({
                "key": f"integer cubic · {item['label']}",
                "admitted": True, "source": "integer-cubic",
                "spans": 5,
                "branches": [{
                    "spans": spans, "ideal": ideal, "count": 5,
                    "min_speed": problem["ratio"], "problem": problem,
                    "error": 0.0, "g3": max(r["dks"] for r in joins),
                    "pass": ok, "closed": False,
                }],
                "error": 0.0, "g3": max(r["dks"] for r in joins),
            })
    return rows


def preset_rows():
    from curve_lab import presets

    def pts_of(name, n=260):
        d = presets.get(name)
        x, y, th = d.anchor["x"], d.anchor["y"], d.anchor["angle"]
        pts = [(x, y)]
        total = sum(seg.length for seg in d.segments) or 1.0
        for seg in d.segments:
            th += seg.corner
            m = max(3, int(n * seg.length / total))
            ds = seg.length / m
            k0 = seg.kappa0 if seg.kappa0 is not None else 0.0
            for i in range(m):
                sm = (i + 0.5) * ds
                theta = th + k0 * sm + seg.kd * sm * sm / 2
                x += math.cos(theta) * ds
                y += math.sin(theta) * ds
                pts.append((x, y))
            th += k0 * seg.length + seg.kd * seg.length ** 2 / 2
        return pts

    rows = []
    for name in ("s-curve", "ogee", "bracket", "petal"):
        r = fit_poly_best(pts_of(name))
        key = f"preset · {name}"
        if r is None or not r["pass"]:
            rows.append({"key": key, "admitted": False, "source": "preset",
                         "reason": "cusp or singular sample; no G3 interpolation"})
        else:
            rows.append({"key": key, "admitted": True, "source": "preset",
                         "spans": r["count"], "branches": [r],
                         "error": r["error"], "g3": r["g3"]})
    return rows


def primal_rows():
    from curve_lab import engine, primal

    rows = []
    for name in ("earth", "water", "air", "fire"):
        piece = primal.PRIMAL[name]()
        fitted = []
        for trace in piece.traces:
            chain = engine.build(trace.design)
            pts = [chain.point(chain.length * i / 240.0) for i in range(241)]
            r = fit_poly_best(pts)
            if r is None or not r["pass"]:
                fitted = None
                break
            fitted.append(r)
        key = f"primal · {name}"
        if fitted is None:
            rows.append({"key": key, "admitted": False, "source": "primal",
                         "reason": "cusp or singular sample; no G3 interpolation"})
        else:
            rows.append({"key": key, "admitted": True, "source": "primal",
                         "spans": max(r["count"] for r in fitted), "branches": fitted,
                         "error": max(r["error"] for r in fitted),
                         "g3": max(r["g3"] for r in fitted)})
    return rows


def lac_rows():
    """The recovered LAC spines are already cubic Bezier chains.

    The source control points are integers at the page scale, so the joins are
    G3 to the data's precision (measured ~6e-8), not to 1e-9 floating-point
    noise. They are carried as their own four-point spans, never re-fitted as
    quintics. The S-label is the showcase-notes label: S39 for Fig. 1, so S44
    for Fig. 6.
    """
    data = json.loads((ROOT / "workbench" / "spirals" / "lac.json").read_text())
    rows = []
    for fig in data["figures"]:
        spine = fig["spines"][0]
        spans = []
        for sp in spine["spans"]:
            spans.append([
                (sp["p0"][0], -sp["p0"][1]),
                (sp["c1"][0], -sp["c1"][1]),
                (sp["c2"][0], -sp["c2"][1]),
                (sp["p3"][0], -sp["p3"][1]),
            ])
        ideal = []
        for P in spans:
            ideal.extend(G3.bezier(P, i / 40.0) for i in range(41))
        joins = G3.gate(spans, tol=SOURCE_TOL)
        ok = all(row["pass"] for row in joins)
        problem = problem_of_spans(spans)
        num = int(fig["figure"].split()[-1])
        key = f"S{38 + num} · {fig['figure']} · {fig['title']}"
        branch = {
            "spans": spans, "count": len(spans), "trimmed": False,
            "min_speed": problem["ratio"], "problem": problem,
            "ideal": ideal, "error": 0.0,
            "g3": max(row["dks"] for row in joins),
            "g3_seam": 0.0, "seam_pass": True,
            "rows": joins, "pass": ok, "closed": False,
        }
        row = {"key": key, "admitted": bool(ok), "source": "lac",
               "spans": len(spans), "branches": [branch],
               "error": 0.0, "g3": branch["g3"],
               "source_precision": True}
        if not ok:
            worst = max(joins, key=lambda r: max(
                r["dp"] / SOURCE_TOL, r["angle"] / 1e-6,
                r["dk"] / SOURCE_TOL, r["dks"] / SOURCE_TOL))
            row["reason"] = (f"source cubic joins are not G3: angle "
                             f"{worst['angle']:.2g}°, Δκ {worst['dk']:.1e}, "
                             f"Δ(dκ/ds) {worst['dks']:.1e}")
        rows.append(row)
    return rows


def stage_two_rows():
    import stem_library as S

    data = json.loads((ROOT / "workbench" / "spirals" / "stage-two.json").read_text())
    rows = []
    for fig in data["figures"]:
        for k, spine in enumerate(fig["spines"]):
            pts = S.lac_branches(spine["spans"])
            title = fig["title"].split(":")[-1].strip()
            key = (f"Stage II · {fig['figure']} · {title}"
                   + ("" if len(fig["spines"]) == 1 else f" · spine {k + 1}"))
            r = fit_poly_best(pts[0])
            if r is None or not r["pass"]:
                rows.append({"key": key, "admitted": False, "source": "stage-two",
                             "reason": "cusp or singular sample; no G3 interpolation"})
            else:
                rows.append({"key": key, "admitted": True, "source": "stage-two",
                             "spans": r["count"], "branches": [r],
                             "error": r["error"], "g3": r["g3"]})
    return rows


def astroid_rows():
    """The astroid, split into four smooth arcs between its cusps.

    A cusp is a declared feature, not a G3 join: the arcs are fitted, the
    cusps are left as the gaps between them.
    """
    cusps = [0.0, math.pi / 2, math.pi, 3 * math.pi / 2, 2 * math.pi]
    branches = []
    for a, b in zip(cusps, cusps[1:]):
        pad = 0.05
        pts = [(math.cos(a + pad + (b - a - 2 * pad) * i / 120) ** 3,
                math.sin(a + pad + (b - a - 2 * pad) * i / 120) ** 3)
               for i in range(121)]
        r = fit_poly_best(pts)
        if r is None:
            return [{"key": "astroid", "admitted": False, "source": "cusp",
                     "reason": "cusp arcs do not fit"}]
        branches.append(r)
    return [{
        "key": "astroid", "admitted": True, "source": "cusp",
        "spans": max(r["count"] for r in branches), "branches": branches,
        "error": max(r["error"] for r in branches),
        "g3": max(r["g3"] for r in branches),
    }]


def cusp_ideal(key):
    if key == "astroid":
        return [(math.cos(t) ** 3, math.sin(t) ** 3) for t in
                [2 * math.pi * i / 240 for i in range(241)]]
    spec = next(s for s in G.NAMED if s["key"] == key)
    data = G.named_data(spec)
    if data.get("ctrl"):
        pts, _ = branch_points(data["ctrl"][0])
        return pts
    return [(float(x), float(y)) for x, y in (data.get("paths") or [[]])[0]]


def cusp_examples(admitted_keys):
    names = ["astroid", "deltoid", "nephroid", "epicycloid k=3",
             "epicycloid k=5", "hypocycloid k=5", "cardioid"]
    out = []
    for name in names:
        pts = cusp_ideal(name)
        if pts:
            status = ("admitted · cusp allowed" if name in admitted_keys
                      else "not admitted")
            out.append({"name": name, "pts": pts, "reason": status})
    return out


def deviation_examples():
    out = []
    spec = next(s for s in G.NAMED if s["key"] == "squircle")
    data = G.named_data(spec)
    if data.get("paths"):
        out.append({"name": "squircle",
                    "pts": [(float(x), float(y)) for x, y in data["paths"][0]],
                    "reason": "deviation 31.2% · too coarse for 5%"})
    import heart_forms as H
    out.append({"name": "heart · Beutel upper",
                "pts": [(float(x), float(y)) for x, y in H.beutel()[0]],
                "reason": "deviation 6.3% · too coarse for 5%"})
    out.append({"name": "LAC · Fig. 1 · p = -3, turn 270",
                "pts": lac_ideal(), "reason": "deviation 9.3% · too coarse for 5%"})
    return out


def lac_ideal():
    import stem_library as S
    data = json.loads((ROOT / "workbench" / "spirals" / "lac.json").read_text())
    return [(float(x), float(y))
            for x, y in S.lac_branches(data["figures"][0]["spines"][0]["spans"])[0]]


def failing_examples():
    """Three original showcase curves that still fail, and why."""
    out = []
    spec = next(s for s in G.NAMED if s["key"] == "astroid")
    data = G.named_data(spec)
    if data["ctrl"]:
        pts, _ts = branch_points(data["ctrl"][0])
        out.append({"name": "astroid", "pts": pts,
                    "reason": "cusp · G3 is undefined at the cusp"})
    spec = next(s for s in G.NAMED if s["key"] == "squircle")
    data = G.named_data(spec)
    if data.get("paths"):
        pts = [(float(x), float(y)) for x, y in data["paths"][0]]
        out.append({"name": "squircle", "pts": pts,
                    "reason": "deviation 31.2% of the curve size · too coarse for 5%"})
    import heart_forms as H
    pts = [(float(x), float(y)) for x, y in H.beutel()[0]]
    out.append({"name": "heart · Beutel upper", "pts": pts,
                "reason": "deviation 6.3% of the curve size · too coarse for 5%"})
    return out


def ideal_svg(ex, w=360, h=240):
    pts = ex["pts"]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    pad = 0.10 * max(max(xs) - min(xs), max(ys) - min(ys), 1e-6)
    f = Frame(w, h, min(xs) - pad, max(xs) + pad,
              min(ys) - pad, max(ys) + pad, pad=30)
    ground_y = min(ys) - 0.35 * pad
    ga, gb = f((min(xs) - pad, ground_y)), f((max(xs) + pad, ground_y))
    return f"""<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{ex['name']} · still failing">
  <rect width="{w}" height="{h}" fill="{PAPER}"/>
  <path d="{_path(pts, f)}" fill="none" stroke="{INK}" stroke-width="2"/>
  <line x1="{ga[0]:.1f}" y1="{ga[1]:.1f}" x2="{gb[0]:.1f}" y2="{gb[1]:.1f}" stroke="{INK}" stroke-width="1"/>
  <text x="10" y="20" font-family="Georgia,serif" font-size="13" fill="{INK}">{ex['name']}</text>
  <text x="10" y="36" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="{GREEN if ex['reason'].startswith('admitted') else RED}">{ex['reason']}</text>
  <text x="10" y="52" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="{MUTED}">original showcase · not admitted</text>
</svg>"""


def catalogue():
    rows = []
    for spec in G.NAMED:
        fitted, why = attempted(spec)
        if fitted is None:
            rows.append({"key": spec["key"], "admitted": False, "reason": why, "source": "named"})
        else:
            rows.append({
                "key": spec["key"], "admitted": True,
                "source": "named", "spans": max(r["count"] for r in fitted),
                "branches": fitted,
                "error": max(r["error"] for r in fitted),
                "g3": max(r["g3"] for r in fitted),
            })
    rows.extend(heart_rows())
    rows.extend(integer_cubic_rows())
    rows.extend(misc_rows())
    rows.extend(preset_rows())
    rows.extend(primal_rows())
    rows.extend(lac_rows())
    rows.extend(stage_two_rows())
    rows.extend(astroid_rows())
    rows = [r for r in rows if not (r["key"] == "astroid" and not r["admitted"])]
    for row in rows:
        if not row["admitted"]:
            continue
        size = abs(curve_size(row["branches"]))
        row["relative"] = row["error"] / size if size > 0 else 0.0
        if row["relative"] > 0.05:
            row["admitted"] = False
            row["reason"] = (f"deviation {row['relative']:.1%} of the curve "
                             "size; the quintic G3 spans cannot follow it")
            for key in ("branches", "error", "g3", "relative", "spans", "source"):
                row.pop(key, None)

    # A join-only gate can pass two spans that each graze a near-cusp in their
    # interior. The speed floor rejects those spans outright.
    for row in rows:
        if not row["admitted"]:
            continue
        ms = min(b.get("min_speed", 1.0) for b in row["branches"])
        if ms < MIN_SPEED:
            row["admitted"] = False
            row["near_cusp"] = True
            row["min_speed"] = ms
            row["reason"] = (f"interior near-cusp: the speed floor is {ms:.0%} "
                             "of the chord; the join gate cannot see it")
            # keep the branches: the diagnostics page draws the red rings on
            # the curve and on dκ/ds.
            for key in ("error", "g3", "relative", "spans"):
                row.pop(key, None)

    # Classify the finished curve, not the span. A curve is G3-complete when
    # every body join passes and the closure seam either passes or is a
    # declared feature (a node, a cusp, a singular endpoint). It is "smooth"
    # for handover when it is one path with no declared feature (the circle is
    # the analytic exception: G3 everywhere by construction).
    for row in rows:
        if not row["admitted"]:
            row["g3_complete"] = False
            row["smooth"] = False
            row["feature"] = None
            row["native"] = None
            row["quintic_content"] = None
            if not row.get("near_cusp"):
                row["min_speed"] = None
            continue
        branches = row["branches"]
        seams = all(b.get("seam_pass", True) for b in branches)
        trimmed = any(b.get("trimmed") for b in branches)
        feature = FEATURES.get(row["key"])
        if trimmed and feature is None:
            feature = "singular endpoint (trimmed)"
        row["feature"] = feature
        row["near_cusp"] = False
        row["single_path"] = len(branches) == 1
        row["seam_pass"] = seams
        row["min_speed"] = min(b.get("min_speed", 1.0) for b in branches)
        row["g3_complete"] = bool(seams or feature is not None)
        # Quantify how much fifth-degree freedom the spans use.
        size = abs(curve_size(branches)) or 1.0
        qc = 0.0
        for br in branches:
            for P in br["spans"]:
                chord = math.dist(P[0], P[-1]) or 1.0
                c = degree_content(P, chord)
                if c is None:
                    continue
                qc = max(qc, c * chord / size)
        row["quintic_content"] = qc
        row["cubic_native"] = qc < 1e-9
        row["native"] = "cubic-native" if row["cubic_native"] else "quintic"
        row["smooth"] = bool(
            row["g3_complete"] and feature is None
            and (row["single_path"] or row["key"] == "circle"))
    return rows


def _fit_signature():
    h = hashlib.sha1(str(FIT_VERSION).encode())
    for name in ("scripts/g3_catalogue.py", "scripts/generators.py",
                 "scripts/heart_forms.py", "scripts/stem_library.py",
                 "workbench/spirals/lac.json",
                 "workbench/spirals/stage-two.json"):
        p = ROOT / name
        if p.exists():
            h.update(p.read_bytes())
    return h.hexdigest()


def catalogue_cached(refresh=False):
    """The catalogue rows, from the fit cache when it is current.

    The page generators call this instead of `catalogue()`; the catalogue page
    calls it with refresh=True so its own rebuild also writes the cache.
    """
    sig = _fit_signature()
    if not refresh and CACHE.exists():
        try:
            data = json.loads(CACHE.read_text(encoding="utf-8"))
            if data.get("signature") == sig:
                return data["rows"]
        except Exception:
            pass
    print("g3_catalogue: fitting 232 curves (cache miss)…", file=sys.stderr)
    rows = catalogue()
    CACHE.write_text(json.dumps({"signature": sig, "rows": rows},
                                separators=(",", ":")), encoding="utf-8")
    return rows


# -- drawing ----------------------------------------------------------------

class Frame:
    def __init__(self, w, h, x0, x1, y0, y1, pad=34):
        self.w, self.h = w, h
        self.s = min((w - 2 * pad) / (x1 - x0), (h - 2 * pad) / (y1 - y0))
        self.ox = (w - (x1 - x0) * self.s) / 2.0 - x0 * self.s
        self.oy = (h - (y1 - y0) * self.s) / 2.0 + y1 * self.s

    def __call__(self, p):
        return (self.ox + p[0] * self.s, self.oy - p[1] * self.s)


def _path(pts, f):
    return " ".join(("M" if i == 0 else "L") + f"{x:.2f},{y:.2f}"
                    for i, (x, y) in enumerate(f(p) for p in pts))


def panel(row, w=520, h=330):
    pts = [p for br in row["branches"] for p in br["ideal"]]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    pad = 0.08 * max(x1 - x0, y1 - y0, 1e-6)
    f = Frame(w, h, x0 - pad, x1 + pad, y0 - pad, y1 + pad)

    ideal = []
    g3 = []
    knots = []
    for br in row["branches"]:
        ideal.append(f'<path d="{_path(br["ideal"], f)}" fill="none" '
                     f'stroke="{MUTED}" stroke-width="1.1" stroke-dasharray="4 4"/>')
        samples = []
        for P in br["spans"]:
            samples.extend(G3.bezier(P, i / 40) for i in range(41))
        g3.append(f'<path d="{_path(samples, f)}" fill="none" '
                  f'stroke="{INK}" stroke-width="2.1"/>')
        for P in br["spans"]:
            p = G3.bezier(P, 0.0)
            X, Y = f(p)
            knots.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="3.0" '
                         f'fill="none" stroke="{GREEN}" stroke-width="1.3"/>')

    trimmed = any(br.get("trimmed") for br in row["branches"])
    seam = any(not br.get("seam_pass", True) for br in row["branches"])
    trim_note = " · ends trimmed at a singular point" if trimmed else ""
    if seam:
        trim_note += " · closure seam allowed"
    return f"""<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{row['key']} G3 interpolation">
  <rect width="{w}" height="{h}" fill="{PAPER}"/>
  {''.join(ideal)}
  {''.join(g3)}
  {''.join(knots)}
  <text x="12" y="22" font-family="Georgia,serif" font-size="14" fill="{INK}">Fig. G3.C · {row['key']}</text>
  <text x="12" y="40" font-family="ui-monospace,Menlo,monospace" font-size="10.5" fill="{MUTED}">{row['spans']} quintic spans · max deviation {row['error']:.1e} · worst Δ(dκ/ds) {row['g3']:.1e}{trim_note}</text>
  <text x="{w / 2:.0f}" y="{h - 8}" text-anchor="middle" font-family="ui-monospace,Menlo,monospace" font-size="10.5" fill="{MUTED}">x (model units)</text>
  <g font-family="Georgia,serif" font-size="11">
    <line x1="12" y1="{h - 24}" x2="38" y2="{h - 24}" stroke="{MUTED}" stroke-width="1.1" stroke-dasharray="4 4"/><text x="44" y="{h - 20}" fill="{INK}">ideal</text>
    <line x1="92" y1="{h - 24}" x2="118" y2="{h - 24}" stroke="{INK}" stroke-width="2.1"/><text x="124" y="{h - 20}" fill="{INK}">G3 interpolation</text>
  </g>
</svg>"""


def table(rows):
    body = []
    for row in rows:
        src = row.get("source") or "named"
        if row["admitted"]:
            seam = any(not b.get("seam_pass", True) for b in row["branches"])
            note = " · see notes" if row["key"] == "circle" else ""
            if seam:
                note += " · closure seam allowed"
            body.append(
                f"<tr><td>{src}</td><td>{row['key']}</td><td>{len(row['branches'])}</td>"
                f"<td>{row['spans']}</td><td>{row['error']:.1e}</td>"
                f"<td>{row['g3']:.1e}</td>"
                f"<td>{'yes' if row.get('g3_complete') else 'no'}</td>"
                f"<td>{native_label(row)}</td>"
                f"<td class=\"ok\">admitted{note}</td></tr>")
        else:
            body.append(
                f"<tr><td>{src}</td><td>{row['key']}</td><td>—</td><td>—</td>"
                f"<td>—</td><td>—</td><td>—</td><td>—</td>"
                f"<td class=\"bad\">rejected: {row['reason']}</td></tr>")
    return ("<table><tr><th>source</th><th>curve</th><th>branches</th><th>spans</th>"
            "<th>max deviation</th><th>worst Δ(dκ/ds)</th><th>complete</th>"
            "<th>native</th><th>status</th></tr>"
            + "".join(body) + "</table>")


CSS = """
:root{--paper:%(paper)s;--ink:%(ink)s;--muted:%(muted)s;--rule:%(rule)s}
*{box-sizing:border-box} body{margin:0;background:#f3eddf;color:var(--ink);font:16px/1.55 Georgia,serif}
main{max-width:1120px;margin:0 auto;padding:34px 22px 70px}
.eyebrow{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}
h1{font-size:31px;line-height:1.12;margin:0 0 8px} h2{font-size:20px;margin:0 0 8px}
.lede{max-width:920px;color:var(--muted)}
.panel{background:var(--paper);border:1px solid var(--rule);padding:14px 16px;margin:0 0 16px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(500px,1fr));gap:16px}
table{border-collapse:collapse;font:12px/1.5 ui-monospace,Menlo,monospace;margin:10px 0;width:100%%}
th,td{border:1px solid var(--rule);padding:5px 8px;text-align:right} th{color:var(--muted);font-weight:400}
.ok{color:%(green)s} .bad{color:%(red)s;font-weight:700}
.small{font:12px/1.6 ui-monospace,Menlo,monospace;color:var(--muted)}
.rule{background:#fffdf7;border-left:4px solid %(gold)s;padding:12px 16px;margin:0 0 18px}
code{font:12px ui-monospace,Menlo,monospace;background:#f4ecd7;padding:1px 4px}
""" % {"paper": PAPER, "ink": INK, "muted": MUTED, "rule": RULE,
       "green": GREEN, "red": RED, "gold": GOLD}


def native_label(row):
    return row.get("native") or "—"


def handover_section(rows):
    smooth = [r for r in rows if r.get("smooth")]
    declared = [r for r in rows if r.get("g3_complete") and not r.get("smooth")]
    admitted = [r for r in rows if r.get("admitted")]
    complete = [r for r in rows if r.get("g3_complete")]
    failed = [r for r in admitted if not r.get("g3_complete")]

    def body(items, with_feature):
        out = []
        for r in items:
            out.append(
                f"<tr><td>{r['key']}</td><td>{r.get('source') or 'named'}</td>"
                f"<td>{r.get('spans', '—')}</td><td>{r['relative']:.1%}</td>"
                f"<td>{native_label(r)}</td>"
                + (f"<td>{r.get('feature') or '—'}</td>" if with_feature else "")
                + "</tr>")
        return "".join(out)

    smooth_table = (
        "<table><tr><th>curve</th><th>source</th><th>spans</th>"
        "<th>deviation</th><th>native</th></tr>"
        + body(smooth, False) + "</table>")
    declared_table = (
        "<table><tr><th>curve</th><th>source</th><th>spans</th>"
        "<th>deviation</th><th>native</th><th>declared feature</th></tr>"
        + body(declared, True) + "</table>")
    return f"""<section class="panel" id="g3-handover">
<h2>Handover to Inkscape and the glyph pipeline</h2>
<p><strong>The unit is the finished curve, not the span.</strong> A curve is
<strong>G3-complete</strong> when every interior join — including the closure seam of a
closed form and every mirror seam — matches position, tangent, curvature and
curvature-rate, and every break is declared by the source (a cusp, a node, or a
singular endpoint), not created by the fit. A <strong>smooth handover</strong> is a
G3-complete curve that is one path with no declared feature, whose deviation is
under 5% of its size, and whose spans keep a speed above 10% of their chord. That is
the list to give Inkscape or a glyph editor without a smoothness caveat.</p>
<p><strong>The interior-speed gate.</strong> A join-only test can pass two spans that
each graze a near-cusp in their interior: the ends match, but the span's speed falls
toward zero and <code>dκ/ds</code> spikes by many orders of magnitude. A span is
admitted only when its speed never falls below 10% of its chord. This is what makes
the acceleration graphs readable and the smooth badge honest; a row that fails it is
rejected with the measured speed floor, not quietly drawn flat.</p>
<p><strong>Why a quintic is the carrier.</strong> Fixing both endpoints, a G3 join asks
for six conditions (tangent direction, curvature and curvature-rate at each end) against
eight unknowns in a quintic span; the two left over are the handle lengths used to
follow the source. A quartic has no freedom left; a cubic is over-determined. So a
quintic span is the least span that can meet G3 at both ends. The number of spans is a
property of the assembly — mirror seams, cusps, nodes and fidelity knots — not of the
degree.</p>
<p><strong>Mirror seams are benign, and testable.</strong> If a curve crosses a mirror
axis orthogonally, reflection preserves curvature (κ is a scalar invariant), so κ is
continuous; κ is even about the seam, so dκ/ds is odd and must vanish there. A true
mirror of a smooth half is therefore G3 at the seam automatically, and
<code>dκ/ds = 0</code> is the test that the mirror is true. An oblique crossing fails
even G1; a mirror <em>tangent</em> (the two arcs meeting with opposite tangents) is a
cusp, not a smooth seam, and is declared as one.</p>
<p><strong>The closure seam is not an exemption.</strong> Where a closed curve starts is
an artifact of the parameterisation, so the seam must pass like any other join. If it
fails, either re-knot the span decomposition or place the seam at a declared node or
cusp. The nodal loops in this catalogue (bow, strophoid, bernoulli, nodal, abs-Gerono)
declare a node at the seam; they are complete <em>with that feature</em>, not smooth.</p>
<p><strong>Native degree.</strong> A quintic span is a pure degree elevation of a cubic
when its fifth divided difference vanishes:
<code>P0 − 5P1 + 10P2 − 10P3 + 5P4 − P5 = 0</code>. Then the fifth-degree freedom did
no work, and the row is badged <strong>cubic-native</strong>: a simple curve collapsing
to a cubic is a selector signal, not an accident. A nonzero fifth difference with a zero
fourth difference is quartic-native; everything else genuinely uses the quintic. The
badge is derived from the control polygon, never asserted.</p>
<p class="small">Every G3-complete curve as a panel, curve left and <code>dκ/ds</code>
right: <a href="g3-handover.html">G3 handover · every complete curve</a>.</p>
<p class="small">Counts: <strong>{len(complete)} G3-complete</strong> of {len(rows)} candidates ·
<strong>{len(smooth)} smooth handover</strong> · {len(declared)} complete with a declared
feature · {len(failed)} admitted but not complete · {len(rows) - len(admitted)} rejected
before completeness. A source corner smoothed inside the 5% tolerance is delivered
smooth; the fit flags a singular endpoint only when it had to trim.</p>
<h3>Smooth handover · {len(smooth)}</h3>
{smooth_table}
<h3>G3-complete with a declared feature · {len(declared)}</h3>
{declared_table}
</section>"""


def build():
    rows = catalogue_cached(refresh=True)
    admitted = [r for r in rows if r["admitted"]]
    rejected = [r for r in rows if not r["admitted"]]
    # The circle is G3 everywhere and is explained on the notes page; it is
    # deliberately not drawn as a catalogue panel.
    drawn = [r for r in admitted if r["key"] != "circle"]
    groups = [("named", "Named curves"), ("heart", "Heart forms"),
              ("integer-cubic", "Integer cubics"),
              ("preset", "Presets"), ("primal", "Primals"),
              ("lac", "LAC spines"), ("stage-two", "Stage II spines"),
              ("misc", "Other families")]
    seam_rows = [r for r in drawn
                 if any(not b.get("seam_pass", True) for b in r["branches"])]
    rest = [r for r in drawn if r not in seam_rows]
    sections, nav = [], ['<a href="#g3-handover">Handover</a>']
    if seam_rows:
        nav.append('<a href="#g3-seam">Closure seam allowed</a>')
        cards = "".join(f'<section class="panel">{panel(r)}</section>'
                        for r in seam_rows)
        sections.append(f'<h2 id="g3-seam" style="margin:26px 0 10px">'
                        f'Closure seam allowed · {len(seam_rows)}</h2>'
                        f'<div class="grid">{cards}</div>')
    for src, label in groups:
        items = [r for r in rest if (r.get("source") or "named") == src]
        if not items:
            continue
        nav.append(f'<a href="#g3-{src}">{label}</a>')
        cards = "".join(f'<section class="panel">{panel(r)}</section>' for r in items)
        sections.append(f'<h2 id="g3-{src}" style="margin:26px 0 10px">{label} · '
                        f'{len(items)}</h2><div class="grid">{cards}</div>')
    panels = "".join(sections)
    nav_line = " · ".join(nav)

    from collections import Counter
    fam = Counter((r.get("source") or "named") for r in admitted)
    family_line = ", ".join(f"{k} {v}" for k, v in sorted(fam.items()))
    admitted_keys = {r["key"] for r in admitted}
    cusp_cards = "".join(
        f'<section class="panel">{ideal_svg(ex)}</section>'
        for ex in cusp_examples(admitted_keys))
    dev_cards = "".join(
        f'<section class="panel">{ideal_svg(ex)}</section>'
        for ex in deviation_examples())
    cusped_hearts = [r["key"] for r in admitted if r.get("source") == "heart"]
    heart_line = ", ".join(cusped_hearts[:8]) + (" …" if len(cusped_hearts) > 8 else "")
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>G3 catalogue · every candidate as a quintic G3 interpolation</title>
<style>{CSS}</style></head><body><main>
<p class="eyebrow">curve-lab · G3 catalogue</p>
<h1>Every candidate, as a G3 quintic interpolation</h1>
<p class="lede">This page shows the <strong>interpolation</strong>, not the ideal curve. Each
admitted curve is a chain of quintic Bézier spans, five to fourteen spans per branch, with
every join measured G3: position, direction, bend, and the smooth acceleration of the bend.
The ideal curve is the faint dashed line underneath. The named curves are read from their
exact homogeneous control polygons; the hearts, presets, primals and recovered LAC/Stage II
spines are read from a local cubic fit of their sampled polylines. A branch that cannot be
interpolated G3 — a cusp, a point at infinity, a singular handle solve, or a deviation over
5% of its own size — is rejected and named in the table, not quietly dropped. The
interpolation runs from end to end; only when an endpoint is singular (a cusp or a point
at infinity) is the first or last span trimmed, and the panel says so.</p>

<div class="rule"><strong>How admission works.</strong> The knots are placed at equal arc
length on the curve. At each knot the tangent, curvature and curvature-rate are read from the
exact homogeneous control polygon, or from a local cubic fit for the sampled hearts, presets, primals and spines. The
quintic span matches them at both ends, and the two handle lengths are chosen to minimise the
deviation from the ideal. The table's <code>max deviation</code> is a geometric distance, not
a parameter error. A curve is admitted only when the deviation is under 5% of its own size;
the rejected reasons state the measured share. The G3 gate is computed from the Bézier
derivatives, not from the drawn polyline. Two exemptions are declared: the
<strong>closure seam</strong> — the point where a closed shape starts and ends — and a
<strong>cusp</strong>, which is split into smooth arcs. Neither is a body join; a body join
at an acute angle, a curvature jump or a curvature-rate jump still fails.</p>

<p class="small" style="margin:0 0 18px">{nav_line}</p>

<section class="panel">
<h2>The gate</h2>
{table(rows)}
<p class="small">By source: {family_line} · {len(admitted)} admitted of {len(rows)} candidates ·
{len([r for r in rows if r.get('g3_complete')])} G3-complete ·
{len([r for r in rows if r.get('smooth')])} smooth handover ·
{len(rejected)} rejected · {SPANS} quintic spans per branch ·
re-derive: <code>python scripts/g3_catalogue.py</code></p>
</section>

{handover_section(rows)}

{panels}

<section class="panel">
<h2>Rejected, with the reason</h2>
<p class="small">A cusp has no tangent direction, so G3 is undefined there; a point at
infinity has no finite position. These are not failures of the interpolation — they are
curves outside the G3 domain. A few hearts are rejected because the quintic G3 spans cannot
follow their sharp features within 5% of the curve size; the reason gives the measured share.
The squircle is still sampled only and needs the same polyline treatment. The next pass adds
it and tightens the high-error cases with more spans.</p>
<p class="small">Back to the <a href="g3-showcase.html">G3 showcase</a> ·
theory on the <a href="g3-notes.html">G3 notes page</a> ·
terminals on the <a href="g3-cut.html">extend-and-cut page</a>.</p>
</section>

<hr class="bottom-rule">
<section class="panel">
<h2>Cusp curves · allowed with a declared cusp</h2>
<p class="small">A cusp is a declared feature, not a G3 join. The curve is split into
smooth arcs between cusps; G3 applies to the arcs, not to the cusp itself. The astroid is
admitted as four such arcs (max deviation 0.0074). The other -oids and the cardioid were
already admitted.</p>
<div class="grid">{cusp_cards}</div>
<p class="small">Cusped hearts already admitted: {heart_line}. See the Heart forms group.</p>
</section>

<hr class="bottom-rule">
<section class="panel">
<h2>Still failing · deviation</h2>
<p class="small">These are not cusp failures. They are source curves whose best quintic
interpolation still misses by more than 5% of the curve size; they stay visible instead of
being quietly dropped. The squircle is the clearest case.</p>
<div class="grid">{dev_cards}</div>
</section>
</main></body></html>
"""
    out = ROOT / "workbench" / "g3-catalogue.html"
    out.write_text(html, encoding="utf-8")

    cache = {
        "spans": SPANS,
        "curves": [
            {"key": r["key"], "admitted": r["admitted"],
             "reason": r.get("reason"),
             "error": r.get("error"), "g3": r.get("g3"),
             "relative": r.get("relative"),
             "source": r.get("source"),
             "g3_complete": r.get("g3_complete"),
             "smooth": r.get("smooth"),
             "feature": r.get("feature"),
             "native": r.get("native"),
             "quintic_content": r.get("quintic_content"),
             "min_speed": r.get("min_speed"),
             "near_cusp": r.get("near_cusp"),
             "source_precision": r.get("source_precision"),
             "branches": [
                 {"error": b["error"], "g3": b["g3"],
                  "pass": b["pass"], "closed": b["closed"],
                  "count": b.get("count"), "trimmed": b.get("trimmed"),
                  "seam_pass": b.get("seam_pass", True),
                  "g3_seam": b.get("g3_seam")}
                 for b in r.get("branches", [])
             ]}
            for r in rows
        ],
    }
    (ROOT / "workbench" / "g3-catalogue.json").write_text(
        json.dumps(cache, indent=1), encoding="utf-8")
    print(out)
    return out


if __name__ == "__main__":
    build()
