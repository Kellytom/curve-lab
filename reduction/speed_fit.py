# The speed-space re-fit: a float search, an exact verdict.
#
# The problem: a curve is designed with speed rows u, v of degree n (position
# degree 2n+1, rails 2n−1). The ceiling wants both inside 11 — speed degree 5
# gives position 11 and rails 9. Find u, v of degree ≤ m that best reproduce
# the designed curve.
#
# The formulation matches the DERIVATIVE, where the position lives linearly:
#
#     M(u, v) = ∫₀¹ (X′ − (u²−v²))² + (Y′ − 2uv)² dt
#
# The search runs in float64 (Gauss-Newton on 2(m+1) coefficients — fast, and
# the search machinery is not the claim). The RESULT is quantized to six
# decimals and then judged in exact rational arithmetic: the returned rows
# are Fractions, the position polynomial is exact, the L² miss is an exact
# rational, and the worst station miss is computed from exact squared
# distances (each a rational) before the square root. So "the fitted rows
# miss by at most X units at the stations" is a statement about the rational
# rows actually returned — a rational GN over huge designed coefficients
# was tried first and its fraction growth made it unusable.
#
# The miss is stated in curve units — never a percentage (operator,
# 2026-11-21: the words on the page must carry an exact meaning).

import math
from fractions import Fraction

Frac = Fraction


# ── rational polynomial helpers (the verdict side) ─────────────────────────

def mul(a, b):
    out = [Frac(0)] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                out[i + j] += ai * bj
    return out


def add(a, b):
    n = max(len(a), len(b))
    return [(a[i] if i < len(a) else Frac(0)) + (b[i] if i < len(b) else Frac(0))
            for i in range(n)]


def inner(p, q):
    """⟨p, q⟩ = ∫₀¹ p·q dt, exactly."""
    total = Frac(0)
    for i, pi in enumerate(p):
        if not pi:
            continue
        for j, qj in enumerate(q):
            if qj:
                total += pi * qj / (i + j + 1)
    return total


def trim(p):
    p = list(p)
    while p and p[-1] == 0:
        p.pop()
    return p


# ── the search (float64) ────────────────────────────────────────────────────

def _poly_mul_f(a, b):
    out = [0.0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                out[i + j] += ai * bj
    return out


def _inner_f(p, q):
    total = 0.0
    for i, pi in enumerate(p):
        if pi:
            for j, qj in enumerate(q):
                if qj:
                    total += pi * qj / (i + j + 1)
    return total


def reffit_float(target_x, target_y, m, start=None, iterations=80):
    """Gauss-Newton in float64 on the derivative's L² miss. Returns float
    rows (u, v) of length m+1."""
    dx = [(i + 1) * c for i, c in enumerate(target_x[1:])]
    dy = [(i + 1) * c for i, c in enumerate(target_y[1:])]
    px = [float(c) for c in target_x]
    u = [0.0] * (m + 1)
    v = [0.0] * (m + 1)
    if start is not None:
        su, sv = start
        for k in range(min(m + 1, len(su))):
            u[k] = float(su[k])
        for k in range(min(m + 1, len(sv))):
            v[k] = float(sv[k])
    if not any(u) and not any(v):
        u[0] = 1.0

    def residual(u, v):
        u2 = _poly_mul_f(u, u)
        v2 = _poly_mul_f(v, v)
        uv = _poly_mul_f(u, v)
        rx = [((dx[i] if i < len(dx) else 0.0) - (u2[i] if i < len(u2) else 0.0)
               + (v2[i] if i < len(v2) else 0.0)) for i in range(len(dx))]
        ry = [((dy[i] if i < len(dy) else 0.0) - 2.0 * (uv[i] if i < len(uv) else 0.0))
              for i in range(len(dy))]
        return rx, ry

    def objective(u, v):
        rx, ry = residual(u, v)
        return _inner_f(rx, rx) + _inner_f(ry, ry)

    best = objective(u, v)
    for _ in range(iterations):
        rx, ry = residual(u, v)
        size = 2 * (m + 1)
        # Jacobian columns as polynomials: du_k → (−2t^k u, −2t^k v);
        # dv_k → (+2t^k v, −2t^k u)
        cols = []
        for k in range(m + 1):
            tk = [0.0] * k + [1.0]
            cols.append(([-2.0 * c for c in _poly_mul_f(tk, u)],
                         [-2.0 * c for c in _poly_mul_f(tk, v)]))
        for k in range(m + 1):
            tk = [0.0] * k + [1.0]
            cols.append(([2.0 * c for c in _poly_mul_f(tk, v)],
                         [-2.0 * c for c in _poly_mul_f(tk, u)]))
        normal = [[_inner_f(cols[i][0], cols[j][0]) + _inner_f(cols[i][1], cols[j][1])
                   for j in range(size)] for i in range(size)]
        grad = [_inner_f(cols[i][0], rx) + _inner_f(cols[i][1], ry) for i in range(size)]
        if max(abs(g) for g in grad) < 1e-14:
            break
        step = _solve_float(normal, [-g for g in grad])
        if step is None:
            break
        t = 1.0
        improved = False
        for _ in range(20):
            nu = [u[k] + t * step[k] for k in range(m + 1)]
            nv = [v[k] + t * step[m + 1 + k] for k in range(m + 1)]
            value = objective(nu, nv)
            if value < best:
                u, v, best = nu, nv, value
                improved = True
                break
            t *= 0.5
        if not improved:
            break
    return u, v


def _solve_float(matrix, rhs):
    n = len(rhs)
    a = [row[:] + [rhs[i]] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(a[r][col]))
        if abs(a[pivot][col]) < 1e-30:
            return None
        a[col], a[pivot] = a[pivot], a[col]
        pv = a[col][col]
        a[col] = [v / pv for v in a[col]]
        for r in range(n):
            if r != col and a[r][col] != 0.0:
                f = a[r][col]
                a[r] = [vr - f * vc for vr, vc in zip(a[r], a[col])]
    return [a[i][n] for i in range(n)]


# ── the verdict (exact) ─────────────────────────────────────────────────────

def quantize(rows, decimals=15):
    """Float rows → exact Fractions. The precision must sit far below the
    rows' own scale: the derivative is quadratic in the rows, so an absolute
    rounding error e becomes a 2·|row|·e wiggle. Six places was the first
    choice and was wrong by construction on the large-coefficient families
    (register 56): 5e-7 normalized became 50 units of row error on c-0253,
    a 1e11 L² floor at the curve's own degree. Fifteen places puts the
    rounding floor below the float search's own convergence."""
    return [Fraction(f"{c:.{decimals}f}") for c in rows]


def position_of_rows(u, v):
    """The exact position polynomial of the rows (integral, coefficient-
    wise — the law of measure.py; never a running sum)."""
    u2 = mul(u, u)
    v2 = mul(v, v)
    uv = mul(u, v)
    n = max(len(u2), len(v2), len(uv))
    xs = [(u2[i] if i < len(u2) else Frac(0)) - (v2[i] if i < len(v2) else Frac(0))
          for i in range(n)]
    ys = [2 * (uv[i] if i < len(uv) else Frac(0)) for i in range(n)]
    x = [Frac(0)] + [c / (j + 1) for j, c in enumerate(xs)]
    y = [Frac(0)] + [c / (j + 1) for j, c in enumerate(ys)]
    return trim(x), trim(y)


def exact_l2(xa, ya, xb, yb):
    """The exact L² miss between two position polynomials' derivatives."""
    def deriv(p):
        return [(i + 1) * c for i, c in enumerate(p[1:])]
    dxa, dya = deriv(xa), deriv(ya)
    dxb, dyb = deriv(xb), deriv(yb)
    rx = add(dxa, [-c for c in dxb])
    ry = add(dya, [-c for c in dyb])
    return inner(rx, rx) + inner(ry, ry)


def station_miss(xa, ya, xb, yb, count=241):
    """The worst station distance, in curve units: exact squared distances
    (rationals), the square root only for the printed number."""
    worst_sq = Frac(0)
    for k in range(count):
        t = Fraction(k, count - 1)
        ax = sum(c * t ** i for i, c in enumerate(xa))
        ay = sum(c * t ** i for i, c in enumerate(ya))
        bx = sum(c * t ** i for i, c in enumerate(xb))
        by = sum(c * t ** i for i, c in enumerate(yb))
        d2 = (ax - bx) ** 2 + (ay - by) ** 2
        if d2 > worst_sq:
            worst_sq = d2
    return math.sqrt(float(worst_sq)) if worst_sq else 0.0


def _norm_scale(target_x, target_y, start):
    """The rational q that brings the problem to O(1): rows are scaled by
    q, the position by q². The power of ten nearest the designed rows' own
    magnitude, else near the square root of the position's."""
    from math import log10
    if start is not None and any(start[0] + start[1]):
        magnitude = max(abs(float(c)) for c in list(start[0]) + list(start[1]) if c)
    else:
        magnitude = max((abs(float(c)) for c in target_x + target_y), default=1.0)
        magnitude = magnitude ** 0.5 if magnitude else 1.0
    if magnitude == 0:
        return Frac(1)
    exponent = round(log10(magnitude))
    return Frac(10) ** exponent


def reffit(target_x, target_y, m, start=None):
    """Fit speed rows of degree ≤ m to the position curve, judged exactly.

    start: the designed rows (the reduction use case has them) — truncated
    to m as the initial guess. Returns (u, v, report) with u, v exact
    Fractions and report['max_miss'] the station miss in curve units.

    The search runs on the normalized problem (rows ÷ q, position ÷ q²): the
    optimum is scale-invariant, and the normalization keeps the float Gram
    matrices at O(1) instead of squaring coefficients of ~1e8 into 1e32 —
    without it the loop family's fits diverged."""
    q = _norm_scale(target_x, target_y, start)
    nx = [c / (q * q) for c in target_x]
    ny = [c / (q * q) for c in target_y]
    nstart = None
    if start is not None:
        nstart = ([c / q for c in start[0]], [c / q for c in start[1]])
    fu, fv = reffit_float(nx, ny, m, nstart)
    u = [c * q for c in quantize(fu)]
    v = [c * q for c in quantize(fv)]
    fx, fy = position_of_rows(u, v)
    report = {
        "l2": exact_l2(target_x, target_y, fx, fy),
        "max_miss": station_miss(target_x, target_y, fx, fy),
        "degree": max(len(trim(u)), len(trim(v))) - 1 if (trim(u) or trim(v)) else 0,
        "scale": q,
    }
    return u, v, report
