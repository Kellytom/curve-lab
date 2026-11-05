"""Tapered stems on the logarithmic spiral.

    from curve_lab.taper import LogSpiral, tapered_band

A constant-width parallel of a log spiral is *not* a log spiral. The exact
partner of `r = a·e^(bθ)` is a scaled and rotated copy,

    Q(θ) = k · P(θ + φ*)

with `φ*` chosen so that the line from `P` to `Q` is perpendicular to the outer
spiral. The width is then proportional to the radius:

    w(θ) = ω(k, b) · r(θ)

so a band between two spirals is a self-similar taper — exact, and the one
variable width in the catalogue that costs nothing.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

__all__ = ["LogSpiral", "taper_angle", "width_ratio", "tapered_band", "verify"]


@dataclass(frozen=True)
class LogSpiral:
    """r = a·e^(bθ), with +y up and θ in radians."""

    a: float
    b: float

    def radius(self, theta: float) -> float:
        return self.a * math.exp(self.b * theta)

    def point(self, theta: float) -> tuple[float, float]:
        r = self.radius(theta)
        return r * math.cos(theta), r * math.sin(theta)

    def tangent(self, theta: float) -> tuple[float, float]:
        r = self.radius(theta)
        dr = self.b * r
        v = (dr * math.cos(theta) - r * math.sin(theta),
             dr * math.sin(theta) + r * math.cos(theta))
        L = math.hypot(*v)
        return v[0] / L, v[1] / L

    def normal(self, theta: float) -> tuple[float, float]:
        tx, ty = self.tangent(theta)
        return -ty, tx

    def curvature_radius(self, theta: float) -> float:
        return self.radius(theta) * math.sqrt(1 + self.b * self.b)

    def arc_length(self, th0: float, th1: float) -> float:
        return self.a * math.sqrt(1 + self.b * self.b) / self.b * (
            math.exp(self.b * th1) - math.exp(self.b * th0))

    def scaled(self, k: float) -> "LogSpiral":
        return LogSpiral(self.a * k, self.b)


def taper_angle(k: float, b: float, span: float = 0.5, steps: int = 40001) -> float:
    """φ* — the rotation that puts the scaled spiral at constant normal distance."""
    best_phi, best_w = 0.0, float("inf")
    for i in range(steps):
        phi = -span + 2 * span * i / (steps - 1)
        e = k * math.exp(b * phi)
        w = math.sqrt(max(0.0, 1 + e * e - 2 * e * math.cos(phi)))
        if w < best_w:
            best_w, best_phi = w, phi
    return best_phi


def width_ratio(k: float, b: float, span: float = 0.5, steps: int = 40001) -> float:
    """ω(k,b) — the width of the band divided by the local radius."""
    phi = taper_angle(k, b, span, steps)
    e = k * math.exp(b * phi)
    return math.sqrt(max(0.0, 1 + e * e - 2 * e * math.cos(phi)))


def tapered_band(a: float, b: float, k: float, th0: float, th1: float, n: int = 240,
                 ratio: float | None = None) -> dict:
    """The inner spiral, the outer partner, and the width at every station."""
    spiral = LogSpiral(a, b)
    outer = spiral.scaled(k)
    phi = taper_angle(k, b)
    w_ratio = width_ratio(k, b) if ratio is None else ratio
    inner_pts, outer_pts, widths = [], [], []
    for i in range(n):
        th = th0 + (th1 - th0) * i / (n - 1)
        p = spiral.point(th)
        q = outer.point(th + phi)
        inner_pts.append(p)
        outer_pts.append(q)
        widths.append(math.dist(p, q))
    return {
        "inner": inner_pts,
        "outer": outer_pts,
        "widths": widths,
        "ratio": w_ratio,
        "phi": phi,
        "radii": [spiral.radius(th0 + (th1 - th0) * i / (n - 1)) for i in range(n)],
    }


def verify(a: float, b: float, k: float, th0: float, th1: float, n: int = 200) -> dict:
    """Re-measure the two claims: constant ratio, and the partner is a log spiral."""
    band = tapered_band(a, b, k, th0, th1, n)
    ratios = [w / r for w, r in zip(band["widths"], band["radii"])]
    # tangent-to-radius angle of the partner, about the origin
    angs = []
    outer = LogSpiral(a * k, b)
    for i in range(n):
        th = th0 + (th1 - th0) * i / (n - 1) + band["phi"]
        tx, ty = outer.tangent(th)
        v = math.atan2(ty, tx) - th
        angs.append((v + math.pi / 2) % math.pi - math.pi / 2)   # mod pi, no wrap jump
    spread = max(angs) - min(angs)
    return {
        "ratio_min": min(ratios),
        "ratio_max": max(ratios),
        "ratio_spread": max(ratios) - min(ratios),
        "tangent_angle_spread": spread,
        "phi": band["phi"],
    }
