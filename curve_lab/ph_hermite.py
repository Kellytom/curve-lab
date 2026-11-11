"""PHH and PPH in 2D: the PH quintic Hermite interpolant and a C² PH spline.

PHH — **PH Hermite**: a PH quintic through two points with prescribed endpoint
tangents.  With ``w(t) = a(1−t)² + 2b t(1−t) + c t²`` and ``z'(t) = w(t)²``,
the condition ``z(1) = z(0) + Δ`` is one quadratic in ``b``:

    2b² + 3(a+c)b + (3a² + ac + 3c² − 15Δ) = 0

so for *any* endpoint generators ``a``, ``c`` on the prescribed tangent lines the
endpoint is hit exactly.  The two speeds ``|a|²``, ``|c|²`` are free; this module
declares one rule for them (``s0 = s2 = √|Δ|``) and lets the caller override.

PPH — **piecewise PH**: PH spans joined with C² continuity.  Each join asks for
``z``, ``z'`` and ``z''`` to agree.  Since ``z' = w²`` and ``z'' = 2 w w'``, a
join is set by taking the next span's ``a`` equal to the previous span's ``c``
and solving ``2 a w'(0) = 2 c w'(1)`` for its ``b`` — exactly, with no fitting.

Nothing here is 3D.  The planar reading is the operator's only limitation.
"""

from __future__ import annotations

import cmath
import math

__all__ = ["hermite", "continue_span", "w_at", "point_at", "derivatives",
           "arc_length", "curvature", "join_defects", "control_points"]


def _bern2(a, b, c, t):
    u = 1.0 - t
    return a * u * u + 2.0 * b * t * u + c * t * t


def _w_sq_bern(a, b, c):
    """Degree-4 Bernstein coefficients of w² (complex)."""
    return (a * a,
            a * b,
            (a * c + 2.0 * b * b) / 3.0,
            b * c,
            c * c)


def control_points(span):
    """The five Bernstein control points of the quintic z, in model space."""
    w = span["w"]
    r = _w_sq_bern(*w)
    pts = [span["p0"]]
    for k in range(5):
        pts.append(pts[-1] + r[k] / 5.0)
    return pts


def w_at(span, t):
    return _bern2(*span["w"], t)


def point_at(span, t):
    """Evaluate z(t) from the Bernstein control points."""
    P = span["_cp"] if "_cp" in span else control_points(span)
    u = 1.0 - t
    z = 0j
    for i, p in enumerate(P):
        z += math.comb(5, i) * u ** (5 - i) * t ** i * p
    return z


def derivatives(span, t):
    """z, z', z'' at t, all exact in w (z' = w², z'' = 2 w w')."""
    w = w_at(span, t)
    dw = 2.0 * ((1.0 - t) * (span["w"][1] - span["w"][0])
                + t * (span["w"][2] - span["w"][1]))
    return point_at(span, t), w * w, 2.0 * w * dw


def arc_length(span):
    """Exact arc length: ∫|w|² is a polynomial, so this is a finite sum."""
    a, b, c = span["w"]
    s = (a * a.conjugate(),
         a * b.conjugate(),
         (a * c.conjugate() + 2.0 * b * b.conjugate()) / 3.0,
         b * c.conjugate(),
         c * c.conjugate())
    return sum(s, 0j).real / 5.0


def curvature(span, t):
    z1 = derivatives(span, t)[1]
    z2 = derivatives(span, t)[2]
    return (z1.conjugate() * z2).imag / abs(z1) ** 3


def _c(p):
    """Accept a complex number or an (x, y) pair."""
    if isinstance(p, (tuple, list)):
        return complex(p[0], p[1])
    return complex(p)


def hermite(p0, p1, theta0, theta1, s0=None, s2=None, root=1):
    """The PH quintic through p0 and p1 with tangents theta0, theta1 (radians).

    ``root`` selects the ± branch of √(5Δ).  The default speed rule is
    ``s0 = s2 = √|Δ|``; pass ``s0``/``s2`` to choose another member of the
    two-parameter family.
    """
    p0 = _c(p0)
    p1 = _c(p1)
    delta = p1 - p0
    d = abs(delta)
    if d == 0.0:
        raise ValueError("PHH needs two distinct points")
    s0 = math.sqrt(d) if s0 is None else float(s0)
    s2 = math.sqrt(d) if s2 is None else float(s2)
    a = s0 * cmath.exp(0.5j * theta0)
    c = s2 * cmath.exp(0.5j * theta1)
    # 2b² + 3(a+c)b + (3a² + ac + 3c² − 15Δ) = 0
    qa = 2.0
    qb = 3.0 * (a + c)
    qc = 3.0 * a * a + a * c + 3.0 * c * c - 15.0 * delta
    b = (-qb + root * cmath.sqrt(qb * qb - 4.0 * qa * qc)) / (2.0 * qa)
    span = {"p0": p0, "p1": p1, "w": (a, b, c), "n": 5}
    span["_cp"] = control_points(span)
    return span


def continue_span(span, theta_next, s_next):
    """A second PH quintic span that meets ``span`` with C² continuity.

    ``z'`` and ``z''`` agree by construction: the new ``a`` is the old ``c``,
    and the new ``b`` is fixed by the old end slope.  ``theta_next`` and
    ``s_next`` place the far end; the join itself takes no fitting.
    """
    a1, b1, c1 = span["w"]
    slope = 2.0 * (c1 - b1)          # w'(1) of the previous span
    a2 = c1
    b2 = c1 + slope / 2.0
    c2 = float(s_next) * cmath.exp(0.5j * theta_next)
    p0 = span["p1"]
    w = (a2, b2, c2)
    r = _w_sq_bern(*w)
    p1 = p0 + sum((math.comb(4, k) * r[k] for k in range(5)), 0j) / 5.0
    span2 = {"p0": p0, "p1": p1, "w": w, "n": 5}
    span2["_cp"] = control_points(span2)
    return span2


def join_defects(left, right):
    """The C² join report: position, velocity and acceleration differences."""
    z0, d0, dd0 = derivatives(left, 1.0)
    z1, d1, dd1 = derivatives(right, 0.0)
    return {"position": abs(z1 - z0),
            "velocity": abs(d1 - d0),
            "acceleration": abs(dd1 - dd0),
            "curvature": abs(curvature(right, 0.0) - curvature(left, 1.0)),
            "speed": abs(abs(d1) - abs(d0))}


def _main():
    p0, p1 = 0j, complex(4.0, 1.5)
    s = hermite(p0, p1, math.radians(10), math.radians(-40))
    print("endpoint miss", abs(point_at(s, 1.0) - p1))
    print("arc", arc_length(s), "speed0", abs(s["w"][0]) ** 2)
    s2 = continue_span(s, math.radians(-95), 1.4)
    print("join", join_defects(s, s2))


if __name__ == "__main__":
    _main()
