"""True Euler spiral segments and the 2021 endpoint-parabola cubic fit.

The arm rule in `curve_lab.bezier` is already the rule from Levien's 2021
post: for a chord and an endpoint tangent angle theta, the cubic handle is at

    arm = |chord| / (3 cos^2(theta/2))
        = 2 |chord| / (3 (1 + cos theta))

which is exactly where the tangent ray meets the endpoint parabola

    x = 1/3 - (3/4) y^2       (left, chord normalized to (0,0)-(1,0))
    x = 2/3 + (3/4) y^2       (right).

This module provides the true Euler spiral for comparison: curvature is linear
in arc length, kappa(s) = k0 + k1 s, and the position is a Fresnel integral.
It also reports the measured cubic error and arclength so the O(n^5) claim can
be checked instead of assumed.

The arm formula is the published 2021 rule, also implemented in kurbo's
`src/euler.rs` (`EulerSeg::to_cubics`) under Apache-2.0, copyright 2021 The
kurbo Authors:
https://github.com/linebender/kurbo/pull/169
This is an independent Python implementation for measurement, not a copy of
that file.
"""

from __future__ import annotations

import math

from .bezier import cubic_at, fit_span, span_error


def _gauss_legendre(n: int = 24):
    """Nodes and weights on [-1, 1], Newton iteration on Legendre roots."""
    nodes = [0.0] * n
    weights = [0.0] * n
    for i in range((n + 1) // 2):
        x = math.cos(math.pi * (i + 0.75) / (n + 0.5))
        for _ in range(30):
            p1, p2 = 1.0, 0.0
            for j in range(1, n + 1):
                p3 = p2
                p2 = p1
                p1 = ((2 * j - 1) * x * p2 - (j - 1) * p3) / j
            pp = n * (x * p1 - p2) / (x * x - 1.0)
            dx = p1 / pp
            x -= dx
            if abs(dx) < 1e-15:
                break
        w = 2.0 / ((1.0 - x * x) * pp * pp)
        nodes[i], nodes[n - 1 - i] = -x, x
        weights[i] = weights[n - 1 - i] = w
    return nodes, weights


_GL_NODES, _GL_WEIGHTS = _gauss_legendre(24)


def _integrate(f, a: float, b: float) -> float:
    if b <= a:
        return 0.0
    mid = 0.5 * (a + b)
    half = 0.5 * (b - a)
    return half * sum(w * f(mid + half * x)
                      for x, w in zip(_GL_NODES, _GL_WEIGHTS))


class EulerSegment:
    """An Euler spiral normalized so its chord is (0,0)-(1,0).

    The raw curve starts at the origin with heading 0; the end is rotated to
    the x-axis and scaled to unit chord. `point(0..1)` is normalized arclength.
    """

    def __init__(self, k0: float, k1: float, length: float):
        if length <= 0:
            raise ValueError("length must be positive")
        self.k0 = float(k0)
        self.k1 = float(k1)
        self.length = float(length)
        ex, ey = self._raw_point(1.0)
        self._chord = math.hypot(ex, ey)
        if self._chord < 1e-12:
            raise ValueError("the segment closes; choose other curvatures")
        self._phi = math.atan2(ey, ex)
        self._cos = math.cos(self._phi)
        self._sin = math.sin(self._phi)

    @property
    def arclength(self) -> float:
        """True arclength after normalization to unit chord."""
        return self.length / self._chord

    @property
    def endpoint_tangents(self) -> tuple[float, float]:
        return self.tangent(0.0), self.tangent(1.0)

    def _raw_point(self, s: float):
        raw = s * self.length

        def heading(u):
            return self.k0 * u + 0.5 * self.k1 * u * u

        return (_integrate(lambda u: math.cos(heading(u)), 0.0, raw),
                _integrate(lambda u: math.sin(heading(u)), 0.0, raw))

    def point(self, s: float):
        x, y = self._raw_point(s)
        # rotate the chord onto +x, then scale it to 1
        return ((x * self._cos + y * self._sin) / self._chord,
                (-x * self._sin + y * self._cos) / self._chord)

    def tangent(self, s: float) -> float:
        raw = s * self.length
        return self.k0 * raw + 0.5 * self.k1 * raw * raw - self._phi


def cubic_arclength(span: dict, samples: int = 400) -> float:
    total = 0.0
    prev = cubic_at(span, 0.0)
    for i in range(1, samples + 1):
        p = cubic_at(span, i / samples)
        total += math.hypot(p[0] - prev[0], p[1] - prev[1])
        prev = p
    return total


def fit_segment(segment: EulerSegment, n: int = 1) -> dict:
    """Fit n equal-arclength cubics with the 2021 parabola arm rule."""
    spans = []
    for i in range(n):
        spans.append(fit_span(i / n, (i + 1) / n,
                              segment.point, segment.tangent))
    errors = [span_error(span, segment.point) for span in spans]
    lengths = [cubic_arclength(span) for span in spans]
    return {
        "n": n,
        "spans": spans,
        "error": max(errors),
        "errors": errors,
        "arclength": sum(lengths),
        "lengths": lengths,
        "true_arclength": segment.arclength,
        "arclength_error": sum(lengths) - segment.arclength,
        "clamped": sum(1 for span in spans if span.get("clamped")),
    }


def case(kind: str) -> EulerSegment:
    """Two representative segments: symmetric S and asymmetric bend."""
    if kind == "symmetric":
        # curvature -2 -> +2, net turn zero; the curve is symmetric about
        # its midpoint, with parallel end tangents.
        return EulerSegment(-2.0, 4.0, 1.0)
    if kind == "asymmetric":
        # curvature -1 -> +3; a strong one-sided bend.
        return EulerSegment(-1.0, 4.0, 1.0)
    raise ValueError(f"unknown case {kind!r}")


def study(kind: str, counts=(1, 2, 4, 8, 16)) -> dict:
    segment = case(kind)
    rows = [fit_segment(segment, n) for n in counts]
    slopes = []
    for a, b in zip(rows, rows[1:]):
        if a["error"] > 0 and b["error"] > 0:
            slopes.append(math.log(a["error"] / b["error"]) / math.log(2))
    return {
        "kind": kind,
        "segment": segment,
        "rows": rows,
        "slope": sum(slopes) / len(slopes) if slopes else 0.0,
        "endpoint_tangents": segment.endpoint_tangents,
        "true_arclength": segment.arclength,
    }
