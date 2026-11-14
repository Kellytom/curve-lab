"""Is a curve a log-aesthetic curve? Fit rho^p = c0 s + c1 and say how well.

    .venv/bin/python scripts/lac_fit.py --control
    .venv/bin/python scripts/lac_fit.py --rows "1,0,0,0,0,0" "-3,30,-120,240,-240,96"

The test: read the curvature radius along the curve, raise it to a power p, and
see whether that is a straight line in arc length. For an LAC it is, for every
point, so the residual is zero to numerical precision. `--control` runs the same
test on curves generated from known p values, which is how the method was
checked before it was used to judge anything.

Residual is the 90th percentile relative error, not the worst point: at a cusp
the radius falls to zero and the relative error there says nothing about the fit
over the curve.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import lac_generate as L  # noqa: E402
from ph_crossings import spine  # noqa: E402

P_GRID = [p / 10 for p in range(-40, 41) if p != 0]


def radius_profile(points):
    """(arc length, curvature radius) along a polyline."""
    arc = [0.0]
    for i in range(len(points) - 1):
        arc.append(arc[-1] + math.hypot(points[i + 1][0] - points[i][0],
                                        points[i + 1][1] - points[i][1]))
    out = []
    for i in range(2, len(points) - 2):
        ax, ay = points[i - 1]
        bx, by = points[i]
        cx, cy = points[i + 1]
        ab = math.hypot(bx - ax, by - ay)
        bc = math.hypot(cx - bx, cy - by)
        ac = math.hypot(cx - ax, cy - ay)
        area = abs((bx - ax) * (cy - ay) - (cx - ax) * (by - ay)) / 2
        if ab * bc * ac < 1e-18:
            continue
        curvature = 4 * area / (ab * bc * ac)
        if curvature > 1e-12:
            out.append((arc[i], 1.0 / curvature))
    return out


def fit_residual(profile, power):
    """How straight rho^p is against arc length, as a relative error."""
    values = [radius ** power for _, radius in profile]
    arcs = [arc for arc, _ in profile]
    count = len(arcs)
    mean_arc = sum(arcs) / count
    mean_value = sum(values) / count
    spread = sum((arc - mean_arc) ** 2 for arc in arcs)
    if spread == 0:
        return None
    slope = sum((a - mean_arc) * (v - mean_value)
                for a, v in zip(arcs, values)) / spread
    intercept = mean_value - slope * mean_arc
    errors = sorted(abs(v - (slope * a + intercept)) / max(abs(v), 1e-12)
                    for a, v in zip(arcs, values))
    return errors[int(len(errors) * 0.9)]


def best_power(points):
    profile = radius_profile(points)
    if len(profile) < 10:
        return None, None
    scored = sorted((fit_residual(profile, p), p) for p in P_GRID)
    return scored[0]


def control():
    """The method must recover the p it was given, or it proves nothing."""
    print(f"{'generated p':>12} {'best fit p':>11} {'residual':>10}")
    for alpha in (-1.0, 0.0, 1.0, 2.0, 3.0):
        points = [(x, y) for x, y, _ in L.points_for(alpha, 90)]
        residual, power = best_power(points)
        print(f"{alpha:12g} {power:11.1f} {residual:10.5f}")
    print("\n(p = 0 is a circle: the radius is constant, so any p fits a flat line;"
          "\nthe scan starts at 0.1 for that reason.)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", nargs=2, metavar=("SPEED_X", "SPEED_Y"))
    parser.add_argument("--control", action="store_true")
    args = parser.parse_args()
    if args.control:
        control()
        return
    if not args.rows:
        parser.print_help()
        return
    def row(text):
        return [float(v) for v in text.replace(" ", "").split(",") if v]
    speed_x, speed_y = row(args.rows[0]), row(args.rows[1])
    _, x, y = spine(speed_x, speed_y, 900)
    residual, power = best_power(list(zip(x, y)))
    if residual is None:
        print("the curve is too short or has no curvature to fit")
        return
    verdict = ("an LAC" if residual < 0.01 else
               "close to an LAC" if residual < 0.05 else "not an LAC")
    print(f"best p {power:.1f}   residual {residual:.4f}   {verdict}")


if __name__ == "__main__":
    main()
