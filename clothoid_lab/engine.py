"""Engine: place a chain of clothoid segments in the plane and read it back.

pyclothoids wraps Bertolazzi's C++ Clothoids. It exposes positions (X, Y) and
the fitting entry points, and not theta or kappa, so those are computed here
from the parameters. That is exact rather than approximate: for a clothoid the
tangent angle is t0 + k0 s + kd s^2 / 2 and the curvature is k0 + kd s.

The chain is built by walking the segments: each one starts where the last one
ended, facing the direction the last one ended in, and curving from whatever
curvature it is told to start at. When that curvature is inherited, the join is
G2. When it is not, the mismatch is measured and reported rather than hidden.
"""

from __future__ import annotations

import math

import pyclothoids as pc

from .model import Design, Segment


class Placed:
    """One segment, placed: its clothoid object plus the state it started from."""

    __slots__ = ("clothoid", "x0", "y0", "t0", "k0", "kd", "length", "s_base", "index")

    def __init__(self, clothoid, x0, y0, t0, k0, kd, length, s_base, index):
        self.clothoid = clothoid
        self.x0, self.y0, self.t0 = x0, y0, t0
        self.k0, self.kd, self.length = k0, kd, length
        self.s_base = s_base
        self.index = index

    def point(self, s_local: float) -> tuple[float, float]:
        return (self.clothoid.X(s_local), self.clothoid.Y(s_local))

    def tangent(self, s_local: float) -> float:
        """Tangent angle in radians, measured from +x, wrapping freely."""
        return self.t0 + self.k0 * s_local + 0.5 * self.kd * s_local * s_local

    def kappa(self, s_local: float) -> float:
        return self.k0 + self.kd * s_local

    def normal(self, s_local: float) -> tuple[float, float]:
        """Unit normal, the tangent turned a quarter turn counter-clockwise."""
        a = self.tangent(s_local)
        return (-math.sin(a), math.cos(a))

    def end(self) -> tuple[float, float, float, float]:
        L = self.length
        x, y = self.point(L)
        return (x, y, self.tangent(L), self.kappa(L))


class Chain:
    """The placed chain, addressed by one global arc length."""

    def __init__(self, placed: list[Placed], design: Design, joins: list[dict]):
        self.segments = placed
        self.design = design
        self.joins = joins
        self.length = sum(p.length for p in placed)

    def locate(self, s: float) -> tuple[Placed, float]:
        """Map a global arc length to its segment and local arc length."""
        s = min(max(s, 0.0), self.length)
        for p in self.segments:
            if s <= p.s_base + p.length + 1e-12:
                return p, min(s - p.s_base, p.length)
        last = self.segments[-1]
        return last, last.length

    def point(self, s: float) -> tuple[float, float]:
        p, u = self.locate(s)
        return p.point(u)

    def tangent(self, s: float) -> float:
        p, u = self.locate(s)
        return p.tangent(u)

    def kappa(self, s: float) -> float:
        p, u = self.locate(s)
        return p.kappa(u)

    def normal(self, s: float) -> tuple[float, float]:
        p, u = self.locate(s)
        return p.normal(u)

    def sample(self, n: int) -> list[tuple[float, float, float]]:
        """`n` points along the whole chain, as (x, y, s)."""
        if n < 2:
            raise ValueError("need at least two sample points")
        out = []
        for i in range(n):
            s = self.length * i / (n - 1)
            x, y = self.point(s)
            out.append((x, y, s))
        return out

    def min_radius(self) -> tuple[float, float]:
        """Smallest radius of curvature on the chain, as (radius, s)."""
        best, best_s = float("inf"), 0.0
        n = max(64, len(self.segments) * 64)
        for i in range(n + 1):
            s = self.length * i / n
            k = abs(self.kappa(s))
            if k > 1e-12 and 1.0 / k < best:
                best, best_s = 1.0 / k, s
        return best, best_s

    def bounds(self) -> tuple[float, float, float, float]:
        n = max(64, len(self.segments) * 128)
        xs, ys = [], []
        for i in range(n + 1):
            x, y = self.point(self.length * i / n)
            xs.append(x)
            ys.append(y)
        return min(xs), min(ys), max(xs), max(ys)

    @property
    def g2(self) -> bool:
        return all(abs(j["d_kappa"]) < 1e-9 for j in self.joins)

    @property
    def max_join_kappa_error(self) -> float:
        return max((abs(j["d_kappa"]) for j in self.joins), default=0.0)


def build(design: Design) -> Chain:
    """Walk the design and place every segment. Continuity is measured, not assumed."""
    ax = float(design.anchor.get("x", 0.0))
    ay = float(design.anchor.get("y", 0.0))
    at = float(design.anchor.get("angle", 0.0))

    x, y, t = ax, ay, at
    k = 0.0
    s_base = 0.0
    placed: list[Placed] = []
    joins: list[dict] = []

    for i, seg in enumerate(design.segments):
        k0 = k if seg.kappa0 is None else float(seg.kappa0)
        if i > 0:
            joins.append({
                "at": s_base,
                "between": (i - 1, i),
                "d_kappa": k0 - k,
                "inherited": seg.kappa0 is None,
            })
        cloth = pc.Clothoid.StandardParams(x, y, t, k0, seg.kd, seg.length)
        placed.append(Placed(cloth, x, y, t, k0, seg.kd, seg.length, s_base, i))
        x, y, t, k = placed[-1].end()
        s_base += seg.length

    return Chain(placed, design, joins)


def report(chain: Chain) -> dict:
    """The numbers that decide whether the drawing is what the design asked for."""
    r_min, r_at = chain.min_radius()
    x0, y0, x1, y1 = chain.bounds()
    return {
        "segments": len(chain.segments),
        "length": chain.length,
        "join_g2": chain.g2,
        "join_kappa_error_max": chain.max_join_kappa_error,
        "min_radius": r_min,
        "min_radius_at": r_at,
        "bounds": (x0, y0, x1, y1),
    }
