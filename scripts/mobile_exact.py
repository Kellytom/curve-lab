"""The mobile, exactly: compound rational rotations at integer rates.

    .venv/bin/python scripts/mobile_exact.py

A vane is a rotation by a rational point of the circle — a p-triple. `3/4` means
the 3-4-5 tilt (cos = 4/5, sin = 3/5); `4/3` is the same tilt the other way. A
vane turning `n` times per unit parameter is `R(t)^n`, and `R` is the rational
circle

    R(t) = ((1 - t^2) + 2it) / (1 + t^2)

so `R^n` is a ratio of integer polynomials (degree 2n over 2n). Sums of vanes
with amplitudes are still ratios, and every point is an exact fraction: no cos,
no sin, no irrational number.

The whole mobile is periodic, so it has no ends — but any arc between two rational
parameters does, with exact endpoints and tangents, which is what a connectable
ornament part needs.
"""

from __future__ import annotations

import json
import math
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from finder_store import save_family  # noqa: E402

SAMPLES = 720
RAIL_SHARE = 0.010

# a rational unit complex number, as (re, im)
TILTS = {
    "3-4-5": (Fraction(4, 5), Fraction(3, 5)),
    "5-12-13": (Fraction(12, 13), Fraction(5, 13)),
    "8-15-17": (Fraction(15, 17), Fraction(8, 17)),
    "flat": (Fraction(1), Fraction(0)),
}


# complex polynomials over Q: lists of (re, im)
def cmul(a, b):
    out = [(Fraction(0), Fraction(0))] * (len(a) + len(b) - 1)
    out = [list(term) for term in out]
    for i, (ar, ai) in enumerate(a):
        for j, (br, bi) in enumerate(b):
            out[i + j][0] += ar * br - ai * bi
            out[i + j][1] += ar * bi + ai * br
    return [(Fraction(r), Fraction(i)) for r, i in out]


def cscale(a, k):
    return [(r * k, i * k) for r, i in a]


def cadd(a, b):
    n = max(len(a), len(b))
    a = list(a) + [(Fraction(0), Fraction(0))] * (n - len(a))
    b = list(b) + [(Fraction(0), Fraction(0))] * (n - len(b))
    return [(ar + br, ai + bi) for (ar, ai), (br, bi) in zip(a, b)]


def real_poly(k):
    """v^k as real coefficients."""
    v = [Fraction(1), Fraction(0), Fraction(1)]
    out = [Fraction(1)]
    for _ in range(k):
        product = [Fraction(0)] * (len(out) + len(v) - 1)
        for i, x in enumerate(out):
            for j, y in enumerate(v):
                product[i + j] += x * y
        out = product
    return out


def rot_power(n):
    """(u + 2it)^n with u = 1 - t^2, as a complex polynomial."""
    base = [(Fraction(1), Fraction(0)), (Fraction(0), Fraction(2)), (Fraction(-1), Fraction(0))]
    out = [(Fraction(1), Fraction(0))]
    for _ in range(n):
        out = cmul(out, base)
    return out


def mobile(vanes):
    """Return (x numerator, y numerator, denominator) as real polynomials.

    vanes: list of (amplitude, rate, tilt_name)
    """
    top_rate = max(rate for _, rate, _ in vanes)
    denominator = real_poly(top_rate)
    num_re = [Fraction(0)]
    num_im = [Fraction(0)]
    for amplitude, rate, tilt in vanes:
        rho_re, rho_im = TILTS[tilt]
        power = cscale(rot_power(rate), Fraction(amplitude))
        # multiply by rho and by v^(top_rate - rate)
        faded = real_poly(top_rate - rate)
        product = [Fraction(0)] * (len(power) + len(faded) - 1)
        re = [Fraction(0)] * (len(power) + len(faded) - 1)
        im = [Fraction(0)] * (len(power) + len(faded) - 1)
        for i, (pr, pi) in enumerate(power):
            for j, f in enumerate(faded):
                re[i + j] += (pr * rho_re - pi * rho_im) * f
                im[i + j] += (pr * rho_im + pi * rho_re) * f
        # align lengths
        def pad(a, n):
            return a + [Fraction(0)] * (n - len(a))
        n = max(len(num_re), len(re))
        num_re = [x + y for x, y in zip(pad(num_re, n), pad(re, n))]
        num_im = [x + y for x, y in zip(pad(num_im, n), pad(im, n))]
    return num_re, num_im, denominator


def evaluate(poly, t):
    total = Fraction(0)
    for c in reversed(poly):
        total = total * t + c
    return total


def point(num_re, num_im, den, t):
    d = evaluate(den, t)
    return evaluate(num_re, t) / d, evaluate(num_im, t) / d


def sampled(num_re, num_im, den, samples=SAMPLES):
    out = []
    for i in range(samples + 1):
        t = Fraction(-samples + 2 * i, samples)
        x, y = point(num_re, num_im, den, t)
        out.append([round(float(x), 6), round(float(y), 6)])
    return out


def rails(points, share=RAIL_SHARE):
    xs = [p[0] for p in points]; ys = [p[1] for p in points]
    size = math.hypot(max(xs) - min(xs), max(ys) - min(ys)) or 1.0
    d = share * size
    left, right = [], []
    for i, (px, py) in enumerate(points):
        a = points[max(0, i - 1)]; b = points[min(len(points) - 1, i + 1)]
        vx, vy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(vx, vy) or 1.0
        nx, ny = -vy / length, vx / length
        left.append([round(px + d * nx, 6), round(py + d * ny, 6)])
        right.append([round(px - d * nx, 6), round(py - d * ny, 6)])
    return [left, right]


VANES = (
    ("one vane, 3-4-5", [(1, 1, "3-4-5")]),
    ("3-4-5 + half 5-12-13, 2 turns", [(1, 1, "3-4-5"), (Fraction(1, 2), 2, "5-12-13")]),
    ("3-4-5 + half 8-15-17, 3 turns", [(1, 1, "3-4-5"), (Fraction(1, 2), 3, "8-15-17")]),
    ("two small, one big", [(1, 1, "3-4-5"), (Fraction(1, 3), 2, "5-12-13"), (Fraction(1, 4), 3, "8-15-17")]),
)


def main():
    curves = []
    for name, vanes in VANES:
        num_re, num_im, den = mobile(vanes)
        from math import gcd as _gcd
        grid = 1
        for c in num_re + num_im + den:
            grid = grid * c.denominator // _gcd(grid, c.denominator)
        integer = all((c * grid).denominator == 1 for c in num_re + num_im + den)
        degrees = (len(num_re) - 1, len(num_im) - 1, len(den) - 1)
        example = point(num_re, num_im, den, Fraction(1, 2))
        pts = sampled(num_re, num_im, den)
        print(f"{name:34} degrees {degrees} grid {grid} integer-after-scaling {integer} "
              f"t=1/2 -> ({example[0]}, {example[1]})")
        curves.append({
            "name": name,
            "definition": {"family": "mobile-exact",
                           "vanes": [[str(a), r, tilt] for a, r, tilt in vanes]},
            "degree": degrees[0],
            "proper": True,
            "path": pts,
            "rails": rails(pts),
            "peak": None,
            "features": {"crossing_pairs": 0, "tangent_45": [], "tangent_-45": []},
            "flags": [f"degrees {degrees}, grid {grid}",
                      "exact: rational rotations only"],
        })
    save_family("mobile-exact", curves,
                note="Mobiles as compound rational rotations at integer rates.")
    print("saved to workbench/finder.json (family: mobile-exact)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
