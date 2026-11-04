"""The n=2 triple-tangent chain: integer cubics, C1 at every join.

Construction
------------
Take the selected arm vectors of the fixed-`n` family as tangents,

    T_k = (a_k, -b_k)          exact integers, +y up

and place the nodes so that each span turns from `T_k` to `T_{k+1}`:

    D_k     = S * (T_k + T_{k+1})     integer step, S = SPAN_SCALE
    N_{k+1} = N_k + D_k

Span `k` is the cubic

    P0 = N_k
    P1 = N_k     + T_k
    P2 = N_{k+1} - T_{k+1}
    P3 = N_{k+1}

so `P1-P0 = T_k` and `P3-P2 = T_{k+1}`. At node `N_k` the incoming derivative
is `3 T_k` and the outgoing derivative is `3 T_k`: equal as vectors, so the
chain is C1 exactly, and every control point is an integer.

Why `S = 2` and not `S = 1`: at `S = 1` the construction gives
`P2 = N_k + T_k = P1`, the inner handles coincide, and every span is a
degenerate cubic with zero measured curvature at its ends. `S = 2` keeps the
handles apart and the join is a genuine curvature comparison.

Curvature is *not* continuous. Measured over the full 43.6°→4.0° sweep the jump
at a join is 6.2% of the larger side (median) and 26.1% (max): near-G2, and
almost always C1 with a small kink in curvature, never a tangent break.
"""

from __future__ import annotations

import math
from fractions import Fraction

Pos = tuple[int, int]
Cubic = tuple[Pos, Pos, Pos, Pos]

SPAN_SCALE = 2


def tangents(points) -> list[Pos]:
    """Arm vectors as tangents, y up: (a, -b)."""
    return [(int(p["a"]), -int(p["b"])) for p in points]


def _add(p: Pos, q: Pos) -> Pos:
    return (p[0] + q[0], p[1] + q[1])


def _mul(k: int, p: Pos) -> Pos:
    return (k * p[0], k * p[1])


def nodes(ts: list[Pos], span_scale: int = SPAN_SCALE) -> list[Pos]:
    out = [(0, 0)]
    for t0, t1 in zip(ts, ts[1:]):
        out.append(_add(out[-1], _mul(span_scale, _add(t0, t1))))
    return out


def spans(ts: list[Pos], span_scale: int = SPAN_SCALE) -> list[Cubic]:
    ns = nodes(ts, span_scale)
    out = []
    for k, (t0, t1) in enumerate(zip(ts, ts[1:])):
        p0, p3 = ns[k], ns[k + 1]
        out.append((p0, _add(p0, t0), (p3[0] - t1[0], p3[1] - t1[1]), p3))
    return out


def _cross(u: Pos, v: Pos) -> int:
    return u[0] * v[1] - u[1] * v[0]


def _norm2(u: Pos) -> int:
    return u[0] * u[0] + u[1] * u[1]


def curvature_at(c: Cubic, t: int) -> Fraction:
    """Curvature of a cubic Bezier at t = 0 or 1, exactly.

    kappa = |B' x B''| / |B'|^3, with
        B'(0) = 3(P1-P0)   B''(0) = 6(P2-2P1+P0)
        B'(1) = 3(P3-P2)   B''(1) = 6(P3-2P2+P1)
    """
    p0, p1, p2, p3 = c
    if t == 0:
        u = (p1[0] - p0[0], p1[1] - p0[1])
        w = (p2[0] - 2 * p1[0] + p0[0], p2[1] - 2 * p1[1] + p0[1])
    else:
        u = (p3[0] - p2[0], p3[1] - p2[1])
        w = (p3[0] - 2 * p2[0] + p1[0], p3[1] - 2 * p2[1] + p1[1])
    if _norm2(u) == 0:
        return Fraction(0)
    return Fraction(2, 3) * Fraction(_cross(u, w), _norm2(u) ** 3)


def joins(ts: list[Pos], span_scale: int = SPAN_SCALE) -> list[Fraction]:
    """Curvature jump at each interior node, as a fraction of the larger side."""
    sp = spans(ts, span_scale)
    out = []
    for k in range(len(sp) - 1):
        left = curvature_at(sp[k], 1)
        right = curvature_at(sp[k + 1], 0)
        scale = max(abs(left), abs(right))
        out.append(Fraction(0) if scale == 0 else abs(left - right) / scale)
    return out


def check_c1(ts: list[Pos], span_scale: int = SPAN_SCALE) -> bool:
    """The join derivative is the same vector on both sides, exactly."""
    sp = spans(ts, span_scale)
    for left, right in zip(sp, sp[1:]):
        d_left = (left[3][0] - left[2][0], left[3][1] - left[2][1])
        d_right = (right[1][0] - right[0][0], right[1][1] - right[0][1])
        if d_left != d_right:
            return False
    return True


# --- G2: free handle length per node -------------------------------------
#
# With one handle length per node, h_k, the curvature at the end of span k and
# at the start of span k+1 work out to
#
#     kappa1_k     = (2/3) C_k (S - h_k)     / (h_{k+1}^2 |T_{k+1}|^3)
#     kappa0_{k+1} = (2/3) C_{k+1} (S - h_{k+2}) / (h_{k+1}^2 |T_{k+1}|^3)
#
# where C_k = cross(T_k, T_{k+1}). The h_{k+1}^2 |T_{k+1}|^3 denominator cancels,
# so equal curvature at the join is the linear recurrence
#
#     C_k (S - h_k) = C_{k+1} (S - h_{k+2})
#
# — two free starting values, then everything follows. C1 still holds because
# both sides of a join share h_{k+1}.


def _cross_int(t0: Pos, t1: Pos) -> int:
    return t0[0] * t1[1] - t0[1] * t1[0]


def g2_handles(ts: list[Pos], span_scale: int = SPAN_SCALE,
               h0: Fraction = Fraction(1), h1: Fraction = Fraction(1)) -> list[Fraction]:
    """Handle lengths that make every interior join exactly G2 (rational)."""
    cs = [_cross_int(t0, t1) for t0, t1 in zip(ts, ts[1:])]
    if any(c == 0 for c in cs):
        raise ValueError("parallel consecutive arms: recurrence divides by cross == 0")
    hs = [Fraction(h0), Fraction(h1)]
    for k in range(len(cs) - 1):
        hs.append(Fraction(span_scale) - Fraction(cs[k], cs[k + 1]) * (Fraction(span_scale) - hs[k]))
    return hs


def spans_with(ts: list[Pos], hs: list[Fraction]) -> list[tuple]:
    """Cubics with a per-node handle length; positions stay integers."""
    ns = nodes(ts)
    out = []
    for k, (t0, t1) in enumerate(zip(ts, ts[1:])):
        p0, p3 = ns[k], ns[k + 1]
        h0, h1 = hs[k], hs[k + 1]
        out.append((
            (Fraction(p0[0]), Fraction(p0[1])),
            (p0[0] + h0 * t0[0], p0[1] + h0 * t0[1]),
            (p3[0] - h1 * t1[0], p3[1] - h1 * t1[1]),
            (Fraction(p3[0]), Fraction(p3[1])),
        ))
    return out


def curvature_gap(ts: list[Pos], hs: list[Fraction]) -> Fraction:
    """Largest |kappa_left - kappa_right| over the joins, exactly."""
    sp = spans_with(ts, hs)
    worst = Fraction(0)
    for left, right in zip(sp, sp[1:]):
        diff = abs(curvature_at(left, 1) - curvature_at(right, 0))
        worst = max(worst, diff)
    return worst


def common_denominator(hs: list[Fraction]) -> int:
    out = 1
    for h in hs:
        d = Fraction(h).denominator
        out = out * d // math.gcd(out, d)
    return out


def report(points, span_scale: int = SPAN_SCALE) -> dict:
    ts = tangents(points)
    sp = spans(ts, span_scale)
    jumps = joins(ts, span_scale)
    controls = [p for c in sp for p in c]
    xs = [p[0] for p in controls]
    ys = [p[1] for p in controls]
    return {
        "tangents": len(ts),
        "spans": len(sp),
        "nodes": len(ts),
        "integer": all(isinstance(v, int) for p in controls for v in p),
        "c1": check_c1(ts, span_scale),
        "span_scale": span_scale,
        "width": max(xs) - min(xs),
        "height": max(ys) - min(ys),
        "length": sum(
            math.isqrt((sp[k][3][0] - sp[k][0][0]) ** 2 + (sp[k][3][1] - sp[k][0][1]) ** 2)
            for k in range(len(sp))
        ),
        "jump_median": sorted(jumps)[len(jumps) // 2] if jumps else Fraction(0),
        "jump_max": max(jumps) if jumps else Fraction(0),
    }


def g2_report(points, span_scale: int = SPAN_SCALE) -> dict:
    ts = tangents(points)
    hs = g2_handles(ts, span_scale)
    gap = curvature_gap(ts, hs)
    den = common_denominator(hs)
    return {
        "joins": len(ts) - 2,
        "curvature_gap": gap,
        "g2": gap == 0,
        "min_handle": min(hs),
        "max_handle": max(hs),
        "common_denominator": den,
        "integer_grid": len(str(den)) <= 6,
    }


if __name__ == "__main__":
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from curve_lab import pyth_triples

    pts = pyth_triples.selected_chain(2, 3500, 44.0, 4.0)
    for k, v in report(pts).items():
        print(f"{k:14} {v}")
