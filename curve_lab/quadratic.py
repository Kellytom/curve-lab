"""Exact degree elevation for quadratic Béziers.

A quadratic is a parabola. Elevating it to a cubic does not change the curve:

    C0 = Q0
    C1 = (Q0 + 2 Q1) / 3
    C2 = (2 Q1 + Q2) / 3
    C3 = Q2

With integer or rational quadratic controls the result is rational; multiply by
3 when integer cubic controls are needed.
"""

from __future__ import annotations

from fractions import Fraction


def elevate(q0, q1, q2):
    """Return the cubic controls of the degree-elevated quadratic."""
    return [
        (Fq(q0[0]), Fq(q0[1])),
        ((Fq(q0[0]) + 2 * Fq(q1[0])) / 3,
         (Fq(q0[1]) + 2 * Fq(q1[1])) / 3),
        ((2 * Fq(q1[0]) + Fq(q2[0])) / 3,
         (2 * Fq(q1[1]) + Fq(q2[1])) / 3),
        (Fq(q2[0]), Fq(q2[1])),
    ]


def Fq(value) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(value)


def at(points, t):
    """Exact point on a quadratic or cubic with four/three controls."""
    if len(points) == 3:
        u = 1 - t
        return (u*u*points[0][0] + 2*u*t*points[1][0] + t*t*points[2][0],
                u*u*points[0][1] + 2*u*t*points[1][1] + t*t*points[2][1])
    u = 1 - t
    return (u*u*u*points[0][0] + 3*u*u*t*points[1][0]
            + 3*u*t*t*points[2][0] + t*t*t*points[3][0],
            u*u*u*points[0][1] + 3*u*u*t*points[1][1]
            + 3*u*t*t*points[2][1] + t*t*t*points[3][1])


def ascent():
    """The integer G1 two-parabola S used by the probe page."""
    left = [(-30, 0), (-20, 10), (-10, 10), (0, 0)]
    right = [(0, 0), (10, -10), (20, -10), (30, 0)]
    return left, right
