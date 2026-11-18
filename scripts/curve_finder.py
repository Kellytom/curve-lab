"""First results for the curve finder: properness, collapse, and where the bend is.

    .venv/bin/python scripts/curve_finder.py           # table + workbench/finder.json
    .venv/bin/python scripts/curve_finder.py --check   # no write, exit 1 on a broken record

The question this starts from: take a high-degree rational curve and ask what it
really is. A curve traced more than once is a lower-degree curve wearing a
costume; the rest are genuinely high degree, and the interesting place on them
is where curvature peaks — often a 45° tangent.

Simple numbers on purpose: integer coefficients, so every reported point is a
rational number and the grid can be stated.
"""

from __future__ import annotations

import json
import math
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab.datafile import FORMATS  # noqa: E402
from curve_lab.reduction import reduce_curve  # noqa: E402

OUT = ROOT / "workbench" / "finder.json"
SAMPLES = 900
NEAR_45 = 0.75      # degrees: "the tangent is at 45°" for a reading
NEAR_MIDDLE = 0.01  # how close to t = 1/2 counts as "around the middle"


def parse(coefficients):
    return [Fraction(c) for c in coefficients]


def evaluate(poly, t):
    value = Fraction(0)
    for coefficient in reversed(poly):
        value = value * t + coefficient
    return value


def derivative(poly):
    return [poly[i] * i for i in range(1, len(poly))] or [Fraction(0)]


def speed_and_curvature(x, y, t):
    dx, dy = derivative(x), derivative(y)
    ddx, ddy = derivative(dx), derivative(dy)
    vx, vy = evaluate(dx, t), evaluate(dy, t)
    ax, ay = evaluate(ddx, t), evaluate(ddy, t)
    speed2 = vx * vx + vy * vy
    if speed2 == 0:
        return None
    # the scan is numeric; the points it reports are still rational
    kappa = abs(float(vx * ay - vy * ax)) / (float(speed2) ** 1.5)
    angle = math.degrees(math.atan2(float(vy), float(vx)))
    return {"t": t, "kappa": kappa, "angle": angle, "x": evaluate(x, t), "y": evaluate(y, t)}


def peak(x, y, samples=SAMPLES):
    """Where curvature is largest, by a scan then a local refinement."""
    best = None
    for i in range(samples + 1):
        t = Fraction(i, samples)
        found = speed_and_curvature(x, y, t)
        if found and (best is None or found["kappa"] > best["kappa"]):
            best = found
    if best is None:
        return None
    # golden-section-ish refinement on the two neighbours
    step = Fraction(1, samples)
    lo, hi = max(Fraction(0), best["t"] - step), min(Fraction(1), best["t"] + step)
    for _ in range(40):
        a = lo + (hi - lo) / 3
        b = hi - (hi - lo) / 3
        ka = speed_and_curvature(x, y, a)
        kb = speed_and_curvature(x, y, b)
        if ka and kb and ka["kappa"] > kb["kappa"]:
            hi = b
        else:
            lo = a
    refined = speed_and_curvature(x, y, (lo + hi) / 2)
    return refined if refined and refined["kappa"] >= best["kappa"] else best


def flags(peak_point):
    out = []
    if peak_point is None:
        return out
    angle = abs(peak_point["angle"])
    if min(abs(angle - 45), abs(angle - 135)) <= NEAR_45:
        out.append("tangent 45°")
    if abs(float(peak_point["t"]) - 0.5) <= NEAR_MIDDLE:
        out.append("peak at t=1/2")
    return out


def sample_path(x, y, steps=240):
    points = []
    for i in range(steps + 1):
        t = Fraction(i, steps)
        points.append([round(float(evaluate(x, t)), 6), round(float(evaluate(y, t)), 6)])
    return points


def curves():
    """Two families, on purpose: covers that must collapse, and proper curves.

    A cover: x = t^n, y = t^(2n). Every one of these is the parabola y = x^2,
    traced n times — the collapse should hand back (u, u^2) each time.
    A proper curve: x = t, y = t^n — the power parabolas, which cannot collapse.
    """
    out = []
    for n in (2, 3, 4, 5):
        out.append({"name": f"y=x^2 as t^{n} cover",
                    "x": [Fraction(0)] * n + [Fraction(1)],
                    "y": [Fraction(0)] * (2 * n) + [Fraction(1)]})
    for n in (2, 3, 4, 5, 6, 7, 8, 9):
        out.append({"name": f"y=x^{n}",
                    "x": [Fraction(0), Fraction(1)],
                    "y": [Fraction(0)] * n + [Fraction(1)]})
    return out


def record(name, x, y):
    verdict = reduce_curve(x, y)
    point = peak(x, y)
    entry = {
        "name": name,
        "x": [str(c) for c in x],
        "y": [str(c) for c in y],
        "degree": max(len(x), len(y)) - 1,
        "proper": verdict["proper"],
        "cover": verdict.get("cover"),
        "substitution": verdict.get("substitution"),
        "note": verdict.get("note"),
        "path": sample_path(x, y),
        "peak": None if point is None else {
            "t": float(point["t"]),
            "kappa": float(point["kappa"]),
            "angle": round(point["angle"], 3),
            "x": float(point["x"]),
            "y": float(point["y"]),
        },
        "flags": flags(point),
    }
    return entry


def main(argv):
    entries = [record(item["name"], item["x"], item["y"]) for item in curves()]
    for entry in entries:
        peak_text = (f"peak t={entry['peak']['t']:.4f} angle={entry['peak']['angle']:+.2f}°"
                     if entry["peak"] else "no peak")
        what = "proper" if entry["proper"] else f"cover ×{entry['cover']}"
        print(f"{entry['name']:22} deg {entry['degree']}  {what:10} {peak_text:32} "
              f"{', '.join(entry['flags'])}")
    if "--check" in argv:
        return 0 if all(entry["path"] for entry in entries) else 1
    document = {"format": FORMATS["finder.json"], "note": "First curve-finder results: properness, "
                "collapse and the curvature peak.", "curves": entries}
    OUT.write_text(json.dumps(document, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
