"""Where a spine crosses itself, and where two spines cross.

    .venv/bin/python scripts/ph_crossings.py --rows "1,0,0" "0,1,0"
    .venv/bin/python scripts/ph_crossings.py --search

The crossing is reported as a pair of parameters `t1 < t2` and the point where
the two passes meet. That pair is a coordinate: it says which two parts of the
stroke sit on top of each other, so a family can be searched by where it loops
rather than only by its shape.

`closest` in `ph_quintic_metrics` is a different question: it is how near the
speed path comes to zero, not where the curve meets itself.

Plain Python only: the test suite runs where numpy is not installed, and a
second, faster code path would be a second thing to keep correct. The bounding
box test in front of every pair keeps it quick enough.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ph_quintic_metrics as metrics  # noqa: E402


def _poly(coefficients, t):
    total = 0.0
    for coefficient in reversed(coefficients):
        total = total * t + coefficient
    return total


def spine(speed_x, speed_y, samples: int = 600):
    """Sample the spine: the position is the integral of w squared.

    The steps are taken at the midpoint of each interval, which is the same rule
    the page uses, so a count here and a count on the page agree.
    """
    t = [i / samples for i in range(samples + 1)]
    step = 1.0 / samples
    x = [0.0]
    y = [0.0]
    for i in range(samples):
        middle = (i + 0.5) * step
        p = _poly(speed_x, middle)
        q = _poly(speed_y, middle)
        x.append(x[-1] + (p * p - q * q) * step)
        y.append(y[-1] + 2 * p * q * step)
    return t, x, y


def _cross(ax, ay, bx, by):
    return ax * by - ay * bx


def _segments_cross(a, b, c, d, tolerance=0.0):
    """Two segments cross when both orientation tests change sign."""
    ax, ay = a
    bx, by = b
    cx, cy = c
    dx, dy = d
    if max(cx, dx) < min(ax, bx) or min(cx, dx) > max(ax, bx):
        return None
    if max(cy, dy) < min(ay, by) or min(cy, dy) > max(ay, by):
        return None
    d1 = _cross(bx - ax, by - ay, cx - ax, cy - ay)
    d2 = _cross(bx - ax, by - ay, dx - ax, dy - ay)
    d3 = _cross(dx - cx, dy - cy, ax - cx, ay - cy)
    d4 = _cross(dx - cx, dy - cy, bx - cx, by - cy)
    if d1 * d2 < -tolerance and d3 * d4 < -tolerance:
        share = d1 / (d1 - d2) if abs(d1 - d2) > 1e-15 else 0.5
        return (ax + (bx - ax) * share, ay + (by - ay) * share)
    return None


def self_crossings(speed_x, speed_y, samples: int = 600):
    """Every proper crossing of the spine with itself, as (t1, t2, x, y).

    Neighbouring segments share an endpoint and are skipped, and so are segments
    two apart, whose shared corner is not a crossing.
    """
    t, x, y = spine(speed_x, speed_y, samples)
    points = list(zip(x, y))
    out = []
    for i in range(len(points) - 1):
        for j in range(i + 2, len(points) - 1):
            hit = _segments_cross(points[i], points[i + 1], points[j], points[j + 1])
            if hit:
                out.append({"t1": round(t[i], 4), "t2": round(t[j], 4),
                            "x": round(hit[0], 4), "y": round(hit[1], 4)})
    return out


def stable_crossings(speed_x, speed_y, coarse: int = 600, fine: int = 2400):
    """Crossings that survive a finer sampling.

    A near-tangential touch appears and disappears as the sample count moves,
    so a crossing is kept only when the coarse pass finds it and the fine pass
    finds it again at the same pair of parameters.
    """
    first = self_crossings(speed_x, speed_y, samples=coarse)
    if not first:
        return []
    second = self_crossings(speed_x, speed_y, samples=fine)
    kept = []
    for hit in first:
        for other in second:
            if abs(hit["t1"] - other["t1"]) < 0.02 and abs(hit["t2"] - other["t2"]) < 0.02:
                kept.append(other)
                break
    return kept


def pair_crossings(first, second):
    """Where two polylines cross, as a list of points.

    One crossing can be reported by several segment pairs, so the points are
    clustered: two reports closer than a thousandth of the size are one meeting.
    """
    points = []
    for i in range(len(first) - 1):
        for j in range(len(second) - 1):
            hit = _segments_cross(first[i], first[i + 1], second[j], second[j + 1])
            if hit:
                points.append(hit)
    if not points:
        return []
    xs = [point[0] for point in first]
    ys = [point[1] for point in first]
    size = max(1e-9, max(xs) - min(xs), max(ys) - min(ys))
    kept = []
    for point in points:
        if not any(abs(point[0] - other[0]) < 1e-3 * size and
                   abs(point[1] - other[1]) < 1e-3 * size for other in kept):
            kept.append(point)
    return kept


def describe(speed_x, speed_y, samples: int = 600):
    hits = self_crossings(speed_x, speed_y, samples)
    measured = metrics.metrics(speed_x, speed_y)
    return {
        "speedX": list(speed_x),
        "speedY": list(speed_y),
        "crossings": hits,
        "bend": round(measured["bend"], 3),
        "pitch": measured["pitch"],
        "inflection": None if measured["inflection"] is None else round(measured["inflection"], 3),
    }


def parse_row(text):
    return [float(part) for part in text.replace(" ", "").split(",") if part]


def search(curves: int = 3000, seed: int = 7):
    """Random small-integer speeds of degree 2 to 4, grouped by crossing count.

    A loop needs the tangent to turn more than half a circle, which a straight
    speed path cannot do, so the speeds are at least quadratic here.
    """
    import random
    random.seed(seed)
    found = {}
    tried = 0
    while tried < curves:
        length = random.choice((3, 4, 5))
        speed_x = [random.choice((-4, -3, -2, -1, 1, 2, 3, 4))] + [
            random.choice((-6, -4, -3, -2, -1, 0, 1, 2, 3, 4, 6)) for _ in range(length - 1)]
        speed_y = [random.choice((-6, -4, -3, -2, -1, 0, 1, 2, 3, 4, 6)) for _ in range(length)]
        tried += 1
        hits = stable_crossings(speed_x, speed_y, coarse=600, fine=2400)
        if not hits or len(hits) > 3:
            continue
        bucket = found.setdefault(len(hits), [])
        if len(bucket) >= 60:
            continue
        record = describe(speed_x, speed_y, samples=1200)
        record["crossings"] = hits      # the pair that survived both sample counts
        bucket.append(record)
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", nargs=2, metavar=("SPEED_X", "SPEED_Y"))
    parser.add_argument("--search", action="store_true")
    args = parser.parse_args()
    if args.rows:
        print(json.dumps(describe(parse_row(args.rows[0]), parse_row(args.rows[1])), indent=2))
        return
    if args.search:
        found = search()
        for count in sorted(found):
            print(f"\n{count} crossing{'s' if count > 1 else ''}")
            seen = set()
            for item in found[count]:
                key = (tuple(item["speedX"]), tuple(item["speedY"]))
                if key in seen:
                    continue
                seen.add(key)
                print(f"  x {item['speedX']}  y {item['speedY']}  bend {item['bend']}"
                      f"  pitch {item['pitch']}  at {[(c['t1'], c['t2']) for c in item['crossings']]}")
                if len(seen) >= 6:
                    break
        return
    parser.print_help()


if __name__ == "__main__":
    main()
