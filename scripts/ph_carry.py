"""Can one PH formula carry any of these curves? Degree is the accuracy dial.

    .venv/bin/python scripts/ph_carry.py

The sandbox's formula is z'(t) = w(t)^2 with w a polynomial of degree k. Any
smooth arc can be carried by it: sample the target, take the square root of its
derivative, fit a polynomial of degree k to that, integrate the square, and
measure how far the result is from the target after the best similarity fit.

If the deviation falls as k rises, then the formula is general and the degree is
the price of accuracy. That is the "one formula" question answered with numbers
rather than with a claim.

The LAC law rho^p = c0 s + c1 is a specification: it says what the curve should
be. This is a representation: it says how to draw it with the machinery the
sandbox already has. The Euler spiral and the log spiral are not polynomial
curves, so they cannot be carried exactly at any degree - only approached, and
the table says how closely.
"""

from __future__ import annotations

import cmath
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def target_points(fn, t0=0.0, t1=1.0, samples=400):
    return [complex(*fn(t0 + (t1 - t0) * i / samples)) for i in range(samples + 1)]


def fit_speed(points, degree):
    """The polynomial w whose square is closest to the target's derivative."""
    step = 1.0 / (len(points) - 1)
    roots = []
    previous = None
    for i in range(len(points) - 1):
        derivative = (points[i + 1] - points[i]) / step
        root = cmath.sqrt(derivative)
        if previous is not None and abs(root + previous) < abs(root - previous):
            root = -root                      # keep the branch continuous
        roots.append(root)
        previous = root
    ts = np.array([(i + 0.5) * step for i in range(len(roots))])
    basis = np.vander(ts, degree + 1, increasing=True)
    real = np.linalg.lstsq(basis, np.array([r.real for r in roots]), rcond=None)[0]
    imag = np.linalg.lstsq(basis, np.array([r.imag for r in roots]), rcond=None)[0]
    return real, imag


def ph_points(real, imag, samples=400):
    """Integrate w squared, which is the curve."""
    out = []
    x = y = 0.0
    step = 1.0 / samples
    for i in range(samples):
        t = (i + 0.5) * step
        p = sum(c * t ** j for j, c in enumerate(real))
        q = sum(c * t ** j for j, c in enumerate(imag))
        x += (p * p - q * q) * step
        y += 2 * p * q * step
        out.append(complex(x, y))
    return out


def deviation(a, b):
    """Worst distance after the best similarity, as a fraction of the size."""
    one = np.array([[z.real, z.imag] for z in a])
    two = np.array([[z.real, z.imag] for z in b])
    count = min(len(one), len(two))
    one, two = one[:count], two[:count]
    one = one - one.mean(0)
    two = two - two.mean(0)
    one /= np.sqrt((one ** 2).sum()) or 1e-9
    two /= np.sqrt((two ** 2).sum()) or 1e-9
    correlation = ((one[:, 0] * two[:, 0] + one[:, 1] * two[:, 1]).sum()
                   + 1j * (one[:, 0] * two[:, 1] - one[:, 1] * two[:, 0]).sum())
    angle = np.angle(correlation)
    rotation = np.array([[np.cos(angle), np.sin(angle)], [-np.sin(angle), np.cos(angle)]])
    two = two @ rotation.T
    return float(np.abs(one - two).max() / math.sqrt(2))


def involute(t):
    """One and a half turns, so the spiral reads as a spiral."""
    a = 3 * math.pi * t
    return (math.cos(a) + a * math.sin(a), math.sin(a) - a * math.cos(a))


def catenary(t):
    x = -1.5 + 3.0 * t
    return (x, math.cosh(x))


def euler_spiral(t):
    """theta = 2 pi u squared: one full turn, curvature growing with arc length."""
    steps = 200
    u = t
    x = y = 0.0
    h = u / steps
    for i in range(steps):
        s = (i + 0.5) * h
        angle = 2 * math.pi * s * s
        x += math.cos(angle) * h
        y += math.sin(angle) * h
    return (x, y)


def log_spiral(t):
    """r = e^(b theta): the self-similar LAC, two turns with a clear growth."""
    b = 0.25
    angle = 4 * math.pi * t
    r = math.exp(b * angle)
    return (r * math.cos(angle), r * math.sin(angle))


def main():
    targets = [
        ("involute (LAC p = 2)", involute),
        ("catenary", catenary),
        ("euler spiral (LAC p = -1)", euler_spiral),
        ("log spiral (LAC p = 1)", log_spiral),
    ]
    degrees = (3, 5, 7, 9)
    print(f"{'target':28s}" + "".join(f"{'k=' + str(k):>10}" for k in degrees))
    for name, fn in targets:
        points = target_points(fn, samples=240)
        cells = []
        for degree in degrees:
            real, imag = fit_speed(points, degree)
            carried = ph_points(real, imag, samples=240)
            cells.append(f"{deviation(carried, points[1:]):10.5f}")
        print(f"{name:28s}" + "".join(cells))
    print("\nThe number is the worst distance from the target after the best "
          "similarity fit,\nas a fraction of the curve's size. Falling with k "
          "means the formula is general\nand the degree buys the accuracy.")


if __name__ == "__main__":
    main()
