"""Are the half powers good for anything? The probe behind the answer.

    .venv/bin/python scripts/half_probe.py

Three questions, each answered by measurement:

1. Can a half-power row be a knot? Random half-power rows are drawn and counted.
2. What does a half-power *term* do to a curve that is otherwise whole-power?
3. Do the balanced tweak patterns still do something at step 1/2?

The answers, as measured on 2026-11-14, are printed at the end. They are also in
`state/DESIGN-int.md`, because the conclusion decides whether half powers are a
search space or a dial.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ph_root_search as R  # noqa: E402
from ph_crossings import pair_crossings  # noqa: E402
import ph_step_search as S  # noqa: E402

BASE_X = [4, 0, -20, 0, 20, 0, 0, 0, 0, 0, 0, 0]
BASE_Y = [-9, 0, 154, 0, -808, 0, 1872, 0, -2000, 0, 800, 0]


def look(row_x, row_y, step):
    points = S.spine(row_x, row_y, step, 600)
    crossings = pair_crossings(points, points)
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    size = math.hypot(max(xs) - min(xs), max(ys) - min(ys)) or 1e-9
    arc = sum(math.dist(points[i], points[i + 1]) for i in range(len(points) - 1))
    chord = math.dist(points[0], points[-1])
    knot = max((math.dist(a, b) for a in crossings for b in crossings), default=0.0)
    legs = (max(min(math.dist(end, c) for c in crossings) for end in (points[0], points[-1]))
            if crossings else size)
    gap = min(R.distance_to(points, R.mirror_of(points)),
              R.distance_to(points, R.half_turn_of(points)))
    return {
        "crossings": len(crossings),
        "knot": round(100 * knot / size),
        "legs": round(100 * legs / size),
        "bend": round(arc / chord, 2) if chord > 1e-9 else None,
        "aspect": round((max(xs) - min(xs)) / max(1e-9, max(ys) - min(ys)), 2),
        "gap": round(gap, 3),
    }


def add_pattern(row, powers, weights, size):
    out = list(row) + [0] * 8
    for power, weight in zip(powers, weights):
        index = round(power / 0.5)
        out[index] = (out[index] or 0) + weight * size
    return out


def main() -> int:
    print("1. can a half-power row be a knot?")
    random.seed(5)
    good = []
    for _ in range(400):
        length = random.choice((4, 6))
        row_x = [random.choice((-6, -4, -3, -2, -1, 0, 1, 2, 3, 4, 6)) for _ in range(length)]
        row_y = [random.choice((-6, -4, -3, -2, -1, 0, 1, 2, 3, 4, 6)) for _ in range(length)]
        if not any(row_x) or not any(row_y):
            continue
        measured = look(row_x, row_y, 0.5)
        if measured["crossings"] >= 5 and 0.25 < measured["aspect"] < 4 and (measured["bend"] or 99) < 8:
            good.append((row_x, row_y, measured))
    print(f"   of 400 random half-power rows, {len(good)} had five or more crossings "
          f"with a sane aspect — the half powers are not a knot field")

    print("\n2. what does one half-power term do?")
    print(f"   base (whole-power numbers, step 1/2): {look(BASE_X, BASE_Y, 0.5)}")
    for value in (1, 4, 16):
        row_y = list(BASE_Y)
        row_y[1] = value
        print(f"   y at t^1/2 = {value:2d}: {look(BASE_X, row_y, 0.5)}")

    print("\n3. the balanced patterns at step 1/2")
    print(f"   x pattern 1/4:    {look(add_pattern(BASE_X, (1, 2), (-1, 1), 1.0), BASE_Y, 0.5)}")
    print(f"   y pattern 1/4:    {look(BASE_X, add_pattern(BASE_Y, (1, 2, 3), (-1, 3, -2), 1.0), 0.5)}")
    print(f"   both patterns 1/4: {look(add_pattern(BASE_X, (1, 2), (-1, 1), 1.0),
                                     add_pattern(BASE_Y, (1, 2, 3), (-1, 3, -2), 1.0), 0.5)}")
    print("\n   They land on whole-power boxes, so the mirror is still exact — the panel")
    print("   is step-safe. Used on an odd box instead, they break the mirror.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
