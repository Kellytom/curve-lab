"""Pythagorean-hodograph cubics: a p-triple rendered as a curve.

A cubic Bezier whose hodograph is a pythagorean triple.  With

    u(t) = u0 + (u1-u0)t,   v(t) = v0 + (v1-v0)t

the control points are

    p1 = p0 + (u0^2 - v0^2,  2 u0 v0) / 3
    p2 = p1 + (u0 u1 - v0 v1, u0 v1 + u1 v0) / 3
    p3 = p2 + (u1^2 - v1^2,  2 u1 v1) / 3

and (u^2 - v^2, 2uv, u^2 + v^2) is Euclid's formula.  What comes free:

    speed        sigma(t) = u(t)^2 + v(t)^2          polynomial
    arc length   s = (u0^2+v0^2 + u0u1+v0v1 + u1^2+v1^2) / 3   exact
    tangent      theta(t) = 2 atan(v(t)/u(t))        the half-angle doubles
    curvature    kappa(t) = 2(uv' - u'v) / (u^2+v^2)^2   rational
"""

from __future__ import annotations

import math


class PHCubic:
    """A cubic PH segment from (u0, v0) to (u1, v1)."""

    def __init__(self, u0: float, v0: float, u1: float, v1: float,
                 origin=(0.0, 0.0), scale: float = 1.0):
        self.u0, self.v0, self.u1, self.v1 = u0, v0, u1, v1
        self.origin = origin
        self.scale = scale

    # -- the two polynomials -------------------------------------------
    def u(self, t: float) -> float:
        return self.u0 + (self.u1 - self.u0) * t

    def v(self, t: float) -> float:
        return self.v0 + (self.v1 - self.v0) * t

    # -- exact quantities ----------------------------------------------
    def speed(self, t: float) -> float:
        return self.u(t) ** 2 + self.v(t) ** 2

    def arc(self) -> float:
        """Closed-form length: sigma is quadratic, so this is exact."""
        k = self.scale ** 2
        return k * (self.u0 ** 2 + self.v0 ** 2
                    + self.u0 * self.u1 + self.v0 * self.v1
                    + self.u1 ** 2 + self.v1 ** 2) / 3.0

    def tangent(self, t: float) -> float:
        """Tangent angle in radians: twice the hodograph angle."""
        return 2.0 * math.atan2(self.v(t), self.u(t))

    def curvature(self, t: float) -> float:
        du = self.u1 - self.u0
        dv = self.v1 - self.v0
        denom = self.speed(t) ** 2
        return 2.0 * (self.u(t) * dv - du * self.v(t)) / denom / self.scale

    # -- geometry ------------------------------------------------------
    def control_points(self):
        s = self.scale
        x0, y0 = self.origin
        p0 = (x0, y0)
        p1 = (p0[0] + s * (self.u0 ** 2 - self.v0 ** 2) / 3.0,
              p0[1] + s * (2 * self.u0 * self.v0) / 3.0)
        p2 = (p1[0] + s * (self.u0 * self.u1 - self.v0 * self.v1) / 3.0,
              p1[1] + s * (self.u0 * self.v1 + self.u1 * self.v0) / 3.0)
        p3 = (p2[0] + s * (self.u1 ** 2 - self.v1 ** 2) / 3.0,
              p2[1] + s * (2 * self.u1 * self.v1) / 3.0)
        return p0, p1, p2, p3

    def point(self, t: float):
        p0, p1, p2, p3 = self.control_points()
        w = 1 - t
        return (w ** 3 * p0[0] + 3 * w * w * t * p1[0]
                + 3 * w * t * t * p2[0] + t ** 3 * p3[0],
                w ** 3 * p0[1] + 3 * w * w * t * p1[1]
                + 3 * w * t * t * p2[1] + t ** 3 * p3[1])

    def rotated(self, angle: float):
        """A copy with every point rotated about the origin."""
        c, s = math.cos(angle), math.sin(angle)
        pts = [self.control_points()[i] for i in range(4)]
        rot = [(c * x - s * y, s * x + c * y) for x, y in pts]
        return rot, self.arc()


def from_tangents(theta0: float, theta1: float, scale: float = 1.0):
    """The simplest pair whose half-angles are these: t = tan(theta/2).

    Any integer pair on the ray t is a valid choice; t = 1 gives (u, v) = (1, 1)
    and theta = 90 degrees, so the pairs (n, 1) walk 90, 53.13, 36.87, 28.07...
    """
    u0, v0 = 1.0, math.tan(theta0 / 2.0)
    u1, v1 = 1.0, math.tan(theta1 / 2.0)
    return PHCubic(u0, v0, u1, v1, scale=scale)


def from_hermite(p0, theta0, p3, theta1):
    """A PH cubic through two points with two tangents -- closed form.

    A cubic PH control polygon has two equal interior angles and leg lengths
    in geometric progression, L2^2 = L1 L3.  Rotating Delta = p3 - p0 by
    -theta0 and writing k = sqrt(L3/L1), the closure conditions give a
    quadratic in k:

        k^2 (b cos2a - a sin2a) + k (b cos a - a sin a) + b = 0

    with (a, b) the components of the rotated Delta and alpha half the turn.
    Pick the root that makes all three legs positive.
    """
    dx, dy = p3[0] - p0[0], p3[1] - p0[1]
    c0, s0 = math.cos(theta0), math.sin(theta0)
    a_ = dx * c0 + dy * s0
    b_ = -dx * s0 + dy * c0
    alpha = (theta1 - theta0) / 2.0
    ca, sa = math.cos(alpha), math.sin(alpha)
    c2, s2 = math.cos(2 * alpha), math.sin(2 * alpha)

    A = b_ * c2 - a_ * s2
    B = b_ * ca - a_ * sa
    C = b_

    roots = []
    if abs(A) < 1e-12:
        roots = [-C / B] if abs(B) > 1e-12 else []
    else:
        disc = B * B - 4 * A * C
        if disc < 0:
            raise ValueError("no real PH cubic for this Hermite data")
        roots = [(-B + math.sqrt(disc)) / (2 * A), (-B - math.sqrt(disc)) / (2 * A)]

    best = None
    for k in roots:
        denom = 1 + k * ca + k * k * c2
        if abs(denom) < 1e-12:
            continue
        l1 = a_ / denom
        l2, l3 = k * l1, k * k * l1
        if l1 > 0 and l2 > 0 and l3 > 0:
            if best is None or l2 < best[0]:
                best = (l2, (l1, l2, l3))
    if best is None:
        raise ValueError("no positive-leg PH cubic for this Hermite data")
    (l1, l2, l3) = best[1]
    u0 = math.sqrt(3 * l1) * math.cos(theta0 / 2.0)
    v0 = math.sqrt(3 * l1) * math.sin(theta0 / 2.0)
    u1 = math.sqrt(3 * l3) * math.cos(theta1 / 2.0)
    v1 = math.sqrt(3 * l3) * math.sin(theta1 / 2.0)
    return PHCubic(u0, v0, u1, v1, origin=p0), (l1, l2, l3)
