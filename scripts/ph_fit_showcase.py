"""Fit each showcase curve to a degree-11 PH speed, for the part-2 sandbox.

    .venv/bin/python scripts/ph_fit_showcase.py 20      # a quick look

The method is the one that recovered the operator's 30.134 replica: for a PH
curve the speed is the square root of the derivative, so

    w(t) = sqrt(z'(t))

Sampled along the source, that is a complex series; a degree-5 polynomial is
fitted to it by least squares, and the fitted curve is the integral of w^2.
The curve is not exact: a general curve is not a PH curve, so `rms` and `max`
record how far the fit misses, as a fraction of the source's size. Every curve
that comes out of here is labelled `fitted`, never `exact`.
"""

from __future__ import annotations

import cmath
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

DEGREE = 5          # w is degree 5, so the position is degree 11
SIMPLE_DEGREE = 3   # the rough grade: w cubic, position degree 7
SAMPLES = 200       # samples along the source
FIT_POINTS = 160    # points used by the least squares


def resample(points, n=SAMPLES):
    """Equal spacing by cumulative chord length."""
    distances = [0.0]
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        distances.append(distances[-1] + math.hypot(x1 - x0, y1 - y0))
    total = distances[-1]
    if total <= 1e-12:
        return None
    out = []
    j = 0
    for i in range(n + 1):
        target = total * i / n
        while j + 1 < len(distances) - 1 and distances[j + 1] < target:
            j += 1
        span = distances[j + 1] - distances[j]
        f = 0.0 if span <= 1e-15 else (target - distances[j]) / span
        x = points[j][0] + f * (points[j + 1][0] - points[j][0])
        y = points[j][1] + f * (points[j + 1][1] - points[j][1])
        out.append((x, y))
    return out


def solve(matrix, rhs):
    n = len(rhs)
    rows = [row[:] + [rhs[i]] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(rows[r][col]))
        rows[col], rows[pivot] = rows[pivot], rows[col]
        if abs(rows[col][col]) < 1e-18:
            return None
        for r in range(col + 1, n):
            f = rows[r][col] / rows[col][col]
            for c in range(col, n + 1):
                rows[r][c] -= f * rows[col][c]
    out = [0.0] * n
    for r in range(n - 1, -1, -1):
        s = rows[r][n] - sum(rows[r][c] * out[c] for c in range(r + 1, n))
        out[r] = s / rows[r][r]
    return out


def fit_series(us, values, degree=DEGREE):
    """Least squares polynomial of the given degree through (u, value)."""
    size = degree + 1
    matrix = [[sum(u ** (i + j) for u in us) for j in range(size)] for i in range(size)]
    rhs = [sum(v * u ** i for u, v in zip(us, values)) for i in range(size)]
    return solve(matrix, rhs)


def fit_speeds(path, degree=DEGREE):
    """The degree-`degree` speed through a resampled path, or None."""
    n = len(path) - 1
    roots = []
    for i in range(len(path)):
        a = max(0, i - 1)
        b = min(n, i + 1)
        if b == a:
            return None
        dz = complex(path[b][0] - path[a][0], path[b][1] - path[a][1]) / (b - a)
        root = cmath.sqrt(dz)
        if roots and (root * roots[-1].conjugate()).real < 0:
            root = -root
        roots.append(root)
    us = [i / n for i in range(len(path))]
    real = fit_series(us, [r.real for r in roots], degree)
    imag = fit_series(us, [r.imag for r in roots], degree)
    if real is None or imag is None:
        return None
    return real, imag


def integrate_speeds(speed_x, speed_y, steps=400):
    points = [(0.0, 0.0)]
    x = y = 0.0
    for i in range(steps):
        u = (i + 0.5) / steps
        p = sum(c * u ** k for k, c in enumerate(speed_x))
        q = sum(c * u ** k for k, c in enumerate(speed_y))
        x += (p * p - q * q) / steps
        y += 2 * p * q / steps
        points.append((x, y))
    return points


def round_significant(value, digits=3):
    if value == 0:
        return 0.0
    return round(value, -int(math.floor(math.log10(abs(value)))) + digits - 1)


def normalised(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    size = max(1e-12, max(xs) - min(xs), max(ys) - min(ys))
    return [(x / size, y / size) for x, y in points]


def fit_curve(points, degree=DEGREE):
    path = resample(points, FIT_POINTS)
    if not path or len(path) < degree + 2:
        return None
    full = fit_speeds(path, degree)
    if full is None:
        return None
    speed_x, speed_y = full
    fitted = integrate_speeds(speed_x, speed_y)
    ox = path[0][0] - fitted[0][0]
    oy = path[0][1] - fitted[0][1]
    fitted = [(px + ox, py + oy) for px, py in fitted]
    size = max(1e-9, max(p[0] for p in path) - min(p[0] for p in path),
               max(p[1] for p in path) - min(p[1] for p in path))
    worst = 0.0
    total = 0.0
    for px, py in fitted:
        best = min(math.hypot(px - sx, py - sy) for sx, sy in path[::4])
        worst = max(worst, best)
        total += best * best
    rms = math.sqrt(total / len(fitted))

    # the rough grade: the same speed with three significant figures. The
    # monomial coefficients are ill-conditioned, so this is a *different*
    # curve; the deviation says by how much.
    simple_x = [round_significant(v) for v in speed_x]
    simple_y = [round_significant(v) for v in speed_y]
    simple_points = integrate_speeds(simple_x, simple_y)
    # one shared scale for both curves: a curve that collapses must read as
    # collapsed, not as a rescaling
    fx = [p[0] for p in fitted]
    fy = [p[1] for p in fitted]
    reference = max(1e-12, max(fx) - min(fx), max(fy) - min(fy))
    simple_xs = [p[0] for p in simple_points]
    simple_ys = [p[1] for p in simple_points]
    deviation = max(math.hypot(ax - bx, ay - by)
                    for (ax, ay), (bx, by)
                    in zip([(x / reference, y / reference) for x, y in fitted],
                           [(x / reference, y / reference) for x, y in simple_points]))

    return {
        "original": [[round(x, 6), round(y, 6)] for x, y in path[::4]],
        "speedX": [round(v, 6) for v in speed_x],
        "speedY": [round(v, 6) for v in speed_y],
        "rms": round(rms / size, 5),
        "max": round(worst / size, 5),
        "simple": {
            "speedX": simple_x,
            "speedY": simple_y,
            "deviation": round(deviation, 4),
        },
    }


def catalogue():
    import showcase_catalogue
    return showcase_catalogue.CATALOGUE


def paths_of(panel):
    """The point lists of a panel: a catalogue curve is (points, colour, ...)."""
    out = []
    for item in panel.get("curves", []):
        points = item[0] if isinstance(item, (tuple, list)) and len(item) == 4 else item
        if isinstance(points, (list, tuple)) and len(points) >= 8:
            out.append(points)
    return out


def fitted(limit=None, max_error=0.03):
    """One fitted speed per showcase path, best first."""
    entries = []
    for panel in catalogue():
        title = panel.get("title") or panel.get("key", "curve")
        for index, path in enumerate(paths_of(panel)):
            result = fit_curve([(float(a), float(b)) for a, b in path])
            if not result or result["rms"] > max_error:
                continue
            name = title if index == 0 else f"{title} · {index + 1}"
            entries.append({
                "name": name[:70],
                "original": result["original"],
                "speedX": result["speedX"],
                "speedY": result["speedY"],
                "bend": None,
                "pitch": None,
                "from": f"fitted, rms {result['rms']:.3f}",
                "source": panel.get("key", ""),
                "simple": result["simple"],
            })
    entries.sort(key=lambda e: e["from"])
    return entries[:limit] if limit else entries


def write_json(limit=120):
    rows = fitted(limit=limit)
    document = {"title": "showcase curves fitted to a degree-11 PH speed",
                "method": "w = sqrt(z') sampled, then a degree-5 least squares fit; "
                          "rms and max are fractions of the source's size",
                "curves": rows}
    out = ROOT / "workbench" / "ph-fitted-curves.json"
    out.write_text(json.dumps(document, indent=1) + "\n")
    print(out.relative_to(ROOT), len(rows), "curves")
    return rows


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--write":
        write_json(int(sys.argv[2]) if len(sys.argv) > 2 else 120)
        raise SystemExit(0)
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    rows = []
    for panel in catalogue():
        for index, path in enumerate(paths_of(panel)):
            result = fit_curve([(float(a), float(b)) for a, b in path])
            if result:
                rows.append((result["rms"], result["max"], panel.get("title", ""), index, result))
    rows.sort()
    print(f"{len(rows)} fits; best {min(r[0] for r in rows):.4f}, "
          f"median {rows[len(rows) // 2][0]:.4f}")
    for rms, worst, title, index, result in rows[:limit]:
        print(f"  rms {rms:.4f}  max {worst:.4f}  {title[:56]} [{index}]  "
              f"x {result['speedX']}  y {result['speedY']}")
