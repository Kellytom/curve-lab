#!/usr/bin/env python3
"""Measure every curve, so two curves can be compared as numbers.

    .venv/bin/python scripts/analyse_curves.py            # report and write
    .venv/bin/python scripts/analyse_curves.py --limit 10 # a quick pass
    .venv/bin/python scripts/analyse_curves.py --check    # no write

Writes `workbench/curve-analysis.json` (registered format). The database is
loaded from that file by `app/scripts/load-analysis.mjs`, so Python computes and
Prisma writes: one writer, as everywhere else.

What is measured, and how honestly it is labelled:

- `method: exact` — the curve has speed rows, so `curve_lab/measure.py` gives
  grid, bend, arc, chord, inflections and closest in `Fraction`.
- `method: sampled` — the curve is a point path (a rational family, a rose), so
  the numbers come from a polyline: stated as sampled, never claimed exact.

Crossings are crossing *pairs* (DESIGN-int §Self-crossings), not places. A
stored `features.crossing_pairs` is used when present, because
`scripts/crossing_audit.py` keeps those honest.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab import measure  # noqa: E402
from scripts.ph_crossings import stable_crossings  # noqa: E402

REGISTRY = ROOT / "workbench" / "curve-registry.json"
OUT = ROOT / "workbench" / "curve-analysis.json"


def spine_points(row, samples=240):
    """Integrate the speed pair with a plain midpoint step: sampling only."""
    u = row.get("speedX") or []
    v = row.get("speedY") or []
    n = max(len(u), len(v))
    u = list(u) + [0] * (n - len(u))
    v = list(v) + [0] * (n - len(v))
    if not any(u) and not any(v):
        return []
    x = y = 0.0
    points = [(x, y)]
    for k in range(samples):
        t = (k + 0.5) / samples
        ux = sum(c * t**i for i, c in enumerate(u))
        vy = sum(c * t**i for i, c in enumerate(v))
        dx = ux * ux - vy * vy
        dy = 2 * ux * vy
        x += dx / samples
        y += dy / samples
        points.append((x, y))
    return points


def path_points(row):
    path = row.get("path")
    if not isinstance(path, list) or len(path) < 8:
        return []
    return [(float(p[0]), float(p[1])) for p in path]


def bbox(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


def polygon_area(points):
    area = 0.0
    for i in range(len(points) - 1):
        x0, y0 = points[i]
        x1, y1 = points[i + 1]
        area += x0 * y1 - x1 * y0
    return abs(area) / 2


def curvature_median(points):
    """Median curvature times the curve's size: scale-free, and robust.

    The maximum was useless: a polyline through a nearly straight run and then a
    tight turn reports a huge value from the triangle's short sides. The median
    says how bent the curve is on average, which is what compares two curves.
    """
    values = []
    for i in range(1, len(points) - 1):
        (x0, y0), (x1, y1), (x2, y2) = points[i - 1], points[i], points[i + 1]
        a = math.hypot(x1 - x0, y1 - y0)
        b = math.hypot(x2 - x1, y2 - y1)
        c = math.hypot(x2 - x0, y2 - y0)
        if a * b * c < 1e-9:
            continue
        cross = abs((x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0))
        values.append(2 * cross / (a * b * c))
    values.sort()
    return values[len(values) // 2] if values else 0.0


def curvature_max(points):
    """Largest curvature, multiplied by the curve's size: dimensionless.

    Curvature alone is 1/length, so two copies of one shape at different sizes
    would look different. Multiplying by the bounding-box size removes the
    scale. A cusp genuinely has unbounded curvature, so a value past 1e6 is
    reported as None rather than as a number nobody should compare.
    """
    peak = 0.0
    for i in range(1, len(points) - 1):
        (x0, y0), (x1, y1), (x2, y2) = points[i - 1], points[i], points[i + 1]
        a = math.hypot(x1 - x0, y1 - y0)
        b = math.hypot(x2 - x1, y2 - y1)
        c = math.hypot(x2 - x0, y2 - y0)
        if a * b * c < 1e-9:
            continue
        # the area of the triangle over the three sides is 4R; kappa = 1/R
        cross = abs((x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0))
        peak = max(peak, 2 * cross / (a * b * c))
    return None if peak > 1e6 else peak


def mirror_gap(points, axis="y"):
    """How far the point set is from its own mirror, as a share of its size."""
    if len(points) < 8:
        return 1.0
    x0, y0, x1, y1 = bbox(points)
    size = max(x1 - x0, y1 - y0) or 1
    if axis == "y":            # vertical line through the middle
        c = (x0 + x1) / 2
        mapped = [(2 * c - x, y) for x, y in points]
    elif axis == "yx":         # the diagonal y = x
        mapped = [(y, x) for x, y in points]
    else:                      # half turn about the middle
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        mapped = [(2 * cx - x, 2 * cy - y) for x, y in points]
    step = max(1, len(points) // 120)
    total = 0.0
    count = 0
    for i in range(0, len(points), step):
        px, py = mapped[i]
        best = min((px - qx) ** 2 + (py - qy) ** 2 for qx, qy in points[::step])
        total += math.sqrt(best)
        count += 1
    return round((total / max(count, 1)) / size, 4)


def analyse(row):
    points = path_points(row)
    kind = "path"
    method = "sampled"
    record = {
        "uid": row["uid"],
        "name": row["name"],
        "family": row.get("family_id") or row.get("family"),
        "kind": kind,
        "method": method,
        "degree": 0,
        "step": float(row.get("step") or 1),
        "grid": "0", "bend": 0.0, "arc": 0.0, "chord": 0.0,
        "inflections": 0, "inflectionMax": 0, "closest": 0.0,
        "crossings": 0, "meetingPoints": 0,
        "bboxW": 0.0, "bboxH": 0.0, "area": 0.0, "maxCurvature": 0.0, "curvatureMedian": 0.0,
        "mirrorY": 1.0, "halfTurn": 1.0, "mirrorYX": 1.0,
    }

    speed_x = row.get("speedX") or []
    speed_y = row.get("speedY") or []
    if speed_x or speed_y:
        kind = "rows"
        points = spine_points(row)
        try:
            m = measure.metrics(speed_x, speed_y)
            record.update({
                "kind": "rows", "method": "exact",
                "grid": str(int(m["grid"])), "bend": round(float(m["bend"]), 6),
                "arc": round(float(m["arc"]), 6), "chord": round(float(m["chord_length"]), 6),
                "inflections": int(m["inflection_count"]),
                "inflectionMax": int(m["inflection_max"]),
                "closest": round(float(m["closest"]), 6),
            })
        except Exception as error:  # noqa: BLE001 - a bad row must not stop the sweep
            record["method"] = "sampled"
            record["error"] = str(error)[:120]

    record["kind"] = kind
    if points:
        x0, y0, x1, y1 = bbox(points)
        record["bboxW"] = round(x1 - x0, 4)
        record["bboxH"] = round(y1 - y0, 4)
        record["area"] = round(polygon_area(points), 4)
        size = max(x1 - x0, y1 - y0) or 1
        record["curvatureMedian"] = round(curvature_median(points) * size, 4)
        peak = curvature_max(points)
        scaled = None if peak is None else peak * size
        # the cap is on the number that is compared (curvature times size), not the raw 1/length
        record["maxCurvature"] = None if scaled is None or scaled > 1e6 else round(scaled, 4)
        record["mirrorY"] = mirror_gap(points, "y")
        record["mirrorYX"] = mirror_gap(points, "yx")
        record["halfTurn"] = mirror_gap(points, "half")
        record["degree"] = max(len(speed_x), len(speed_y)) - 1 if speed_x or speed_y else 0

    # Crossings are crossing pairs, and are computed here because the registry
    # stores no crossing count. Meeting points are the distinct places those
    # pairs sit at: a triple point is three pairs, one place.
    if kind == "rows":
        try:
            hits = stable_crossings(speed_x, speed_y)
            record["crossings"] = len(hits)
            record["meetingPoints"] = len({(round(h["x"], 1), round(h["y"], 1)) for h in hits})
        except Exception:  # noqa: BLE001 - one bad curve must not stop the sweep
            pass
    return record


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    curves = [c for c in registry["curves"]]
    if args.limit:
        curves = curves[: args.limit]

    rows = []
    for index, row in enumerate(curves, 1):
        try:
            rows.append(analyse(row))
        except Exception as error:  # noqa: BLE001
            rows.append({"uid": row.get("uid"), "name": row.get("name"),
                         "kind": "error", "method": "sampled",
                         "error": str(error)[:120]})
        if index % 25 == 0:
            print(f"  {index} of {len(curves)}", flush=True)

    exact = sum(1 for r in rows if r.get("method") == "exact")
    crossed = sum(1 for r in rows if r.get("crossings"))
    print(f"{len(rows)} curves · {exact} exact · {crossed} with crossings")
    for key in ("crossings", "inflections", "maxCurvature", "mirrorY"):
        values = [r.get(key) for r in rows if isinstance(r.get(key), (int, float))] or [0]
        print(f"  {key}: min {min(values)} median {sorted(values)[len(values)//2]} max {max(values)}")

    if args.check:
        return 0
    OUT.write_text(json.dumps({"format": "curve-lab.curve-analysis/1", "curves": rows},
                              indent=1) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
