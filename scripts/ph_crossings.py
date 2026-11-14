"""Where a spine crosses itself.

    .venv/bin/python scripts/ph_crossings.py --rows "1,0,0" "0,1,0"
    .venv/bin/python scripts/ph_crossings.py --search

The crossing is reported as a pair of parameters `t1 < t2` and the point where
the two passes meet. That pair is a coordinate: it says which two parts of the
stroke sit on top of each other, so a family can be searched by where it loops
rather than only by its shape.

`closest` in `ph_quintic_metrics` is a different question: it is how near the
speed path comes to zero, not where the curve meets itself.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ph_quintic_metrics as metrics  # noqa: E402


def spine(speed_x, speed_y, samples: int = 600):
    """Sample the spine: the position is the integral of w squared.

    The steps are taken at the midpoint of each interval, which is the same rule
    the page uses, so a count here and a count on the page agree.
    """
    t = np.linspace(0.0, 1.0, samples + 1)
    middle = (t[:-1] + t[1:]) / 2
    p = np.polyval(np.array(speed_x, dtype=float)[::-1], middle)
    q = np.polyval(np.array(speed_y, dtype=float)[::-1], middle)
    step = 1.0 / samples
    x = np.concatenate(([0.0], np.cumsum((p * p - q * q) * step)))
    y = np.concatenate(([0.0], np.cumsum((2 * p * q) * step)))
    return t, x, y


def self_crossings(speed_x, speed_y, samples: int = 600, tol: float = 1e-9):
    """Every proper crossing of the spine with itself, as (t1, t2, x, y).

    Two segments cross when both orientation tests change sign. Neighbouring
    segments share an endpoint and are skipped, and so are segments two apart,
    whose shared corner is not a crossing.
    """
    t, x, y = spine(speed_x, speed_y, samples)
    a = np.column_stack((x[:-1], y[:-1]))      # segment starts
    b = np.column_stack((x[1:], y[1:]))        # segment ends
    count = len(a)
    i, j = np.triu_indices(count, k=2)
    keep = j > i + 1
    i, j = i[keep], j[keep]
    if not len(i):
        return []
    a1, b1, a2, b2 = a[i], b[i], a[j], b[j]
    def cross(u, v):
        return u[:, 0] * v[:, 1] - u[:, 1] * v[:, 0]
    d1 = cross(b1 - a1, a2 - a1)
    d2 = cross(b1 - a1, b2 - a1)
    d3 = cross(b2 - a2, a1 - a2)
    d4 = cross(b2 - a2, b1 - a2)
    hit = (d1 * d2 < -tol) & (d3 * d4 < -tol)
    out = []
    for index in np.nonzero(hit)[0]:
        # the crossing point, from the first segment's parameter
        length = d1[index] - d2[index]
        share = d1[index] / length if abs(length) > tol else 0.5
        point = a1[index] + (b1[index] - a1[index]) * share
        out.append({
            "t1": round(float(t[i[index]]), 4),
            "t2": round(float(t[j[index]]), 4),
            "x": round(float(point[0]), 4),
            "y": round(float(point[1]), 4),
        })
    return out


def pair_crossings(first, second):
    """Where two polylines cross, as a list of points.

    A proper crossing needs both orientation tests to change sign, so a shared
    endpoint or a tangency does not count. Vectorised over all segment pairs:
    a thousand segments each way is a million tests, which numpy does in one go.
    """
    a = np.array(first[:-1], dtype=float)
    b = np.array(first[1:], dtype=float)
    c = np.array(second[:-1], dtype=float)
    d = np.array(second[1:], dtype=float)
    if not (len(a) and len(c)):
        return []
    # every segment of the first against every segment of the second: the two
    # index axes must stay separate, or the subtraction silently pairs segment
    # i with segment i and the count is nonsense
    ax, ay = a[:, 0][:, None], a[:, 1][:, None]
    bx, by = b[:, 0][:, None], b[:, 1][:, None]
    cx, cy = c[:, 0][None, :], c[:, 1][None, :]
    dx, dy = d[:, 0][None, :], d[:, 1][None, :]
    ux, uy = bx - ax, by - ay
    vx, vy = dx - cx, dy - cy
    d1 = ux * (cy - ay) - uy * (cx - ax)
    d2 = ux * (dy - ay) - uy * (dx - ax)
    d3 = vx * (ay - cy) - vy * (ax - cx)
    d4 = vx * (by - cy) - vy * (bx - cx)
    hit = (d1 * d2 < 0) & (d3 * d4 < 0)
    rows, columns = np.nonzero(hit)
    points = []
    for i, j in zip(rows, columns):
        share = d1[i, j] / (d1[i, j] - d2[i, j])
        points.append((a[i, 0] + (b[i, 0] - a[i, 0]) * share,
                       a[i, 1] + (b[i, 1] - a[i, 1]) * share))
    # one crossing can be reported by several segment pairs, so cluster the
    # points: two reports closer than a thousandth of the size are one meeting
    if not points:
        return []
    size = max(1e-9, float(np.ptp(np.array(first), axis=0).max()))
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
        hits = stable_crossings(speed_x, speed_y)
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
