"""A guide spine: the polynomial that places anchors for PH segments.

    from ph_guide_spine import GuideSpine
    spine = GuideSpine((1.0, -0.5, 0.5, -0.5, 0.3, -0.2, 0.1), span=625)
    for t, x, y in spine.anchors(5):
        ...

The spine is not a PH curve.  It is an ordinary polynomial

    x(t) = span * t
    y(t) = span * (n1 t + n2 t^2 + ... + n7 t^7)

used to place the anchors and tangents that the quintic PH segments then
connect.  Two things make it useful:

- the k-th derivative at t = 0 is `n_k * span * k!` - the control vector of
  order k, in the state-space sense (u5 is the 5th-order input);
- sampling at t = i/count keeps x on an exact grid, so the anchors sit on
  whole numbers when span and n are chosen kindly.

Mixed signs are what turn the all-positive ramp into an arch: positive low
orders lift, negative high orders brake.  See docs/PH-GUIDE-SPINE.md.
"""

from __future__ import annotations

import math
from fractions import Fraction

from ph_quintic_metrics import to_fraction

__all__ = ["GuideSpine", "control_vectors", "anchors", "slopes"]


class GuideSpine:
    """y(t) = span * sum n_k t^k, x(t) = span * t."""

    def __init__(self, n_values, span=Fraction(625)):
        self.n_values = [to_fraction(value) for value in n_values]
        self.span = Fraction(span)

    def y_ratio(self, t):
        """y(t) / span."""
        t = Fraction(t)
        return sum(n * t ** (k + 1) for k, n in enumerate(self.n_values))

    def point(self, t):
        t = Fraction(t)
        return (self.span * t, self.span * self.y_ratio(t))

    def slope(self, t):
        """dy/dx at t (dx/dt = span, so the span cancels)."""
        t = Fraction(t)
        return sum((k + 1) * n * t ** k for k, n in enumerate(self.n_values))

    def anchors(self, count=5):
        """count + 1 points at t = i/count, as (t, x, y) exact Fractions."""
        return [(Fraction(i, count), *self.point(Fraction(i, count)))
                for i in range(count + 1)]

    def anchor_table(self, count=5):
        """The anchor rows the design notes use: integers plus the slope."""
        rows = []
        for t, x, y in self.anchors(count):
            rows.append({
                "t": t,
                "x": round(float(x)),
                "y": round(float(y)),
                "y_exact": y,
                "slope": float(self.slope(t)),
            })
        return rows

    def control_vectors(self):
        """u_k = n_k * span * k! - the k-th derivative at t = 0."""
        return [n * self.span * math.factorial(k + 1)
                for k, n in enumerate(self.n_values)]


def control_vectors(n_values, span=625):
    return GuideSpine(n_values, span).control_vectors()


def anchors(n_values, span=625, count=5):
    return GuideSpine(n_values, span).anchor_table(count)


def slopes(n_values, count=5):
    spine = GuideSpine(n_values)
    return [float(spine.slope(Fraction(i, count))) for i in range(count + 1)]
