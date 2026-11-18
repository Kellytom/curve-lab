"""Gate 4 probe: how far a chain-built study 01 drifts from P01's nodes.

    .venv/bin/python scripts/spine_study_probe.py

The right half of study 01 has span laws the chain already speaks: a line is
zero turns, an arc is a constant turn, an Euler span is turns 0, 1, 2, ...
This walks those spans as one composite chain in exact rational arithmetic and
compares each span boundary with P01's own node, after rotating the reference
into the chain's frame (start east at the origin).

The probe does not draw anything and does not claim the gate. It measures the
price of the only exact route: every heading change must be a whole number of
triangle turns, and P01's start heading (77.97 degrees) and corners are not in
that group. A finer angle reduces the quantisation, and it does converge: 0.125
degrees reaches 0.11% of height, while 0.0625 degrees did not finish in a minute.
The cost is the limit, not the method. See `app/src/content/docs/docs/fidelity.md`.

The band is not included: it is a second stroke, and its 180 degree arcs need
the same treatment at the same cost.
"""

from __future__ import annotations

import math
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "pythagorean-spiral"))

from pythagorean_spiral.exact import Dir  # noqa: E402
from pythagorean_spiral.spiral import Spiral  # noqa: E402
from pythagorean_spiral.triples import for_angle  # noqa: E402

from curve_lab.grammar import STUDY_01, fleur_right  # noqa: E402

ANGLES = (1.0, 0.5, 0.25)


def composite(spans, alpha_deg: float):
    """One rational point list for the spans, plus each span's end index."""
    alpha = math.radians(alpha_deg)
    triangle = for_angle(alpha_deg)
    heading = Dir.east()
    point = (Fraction(0), Fraction(0))
    points = [point]
    ends: list[int] = []
    chords = 0

    for index, segment in enumerate(spans):
        if index:
            # P01's span corners are real turns; quantise them to the group.
            heading = heading * (triangle.direction ** round(segment.corner / alpha))

        sweep = (segment.kappa0 * segment.length
                 + 0.5 * segment.kd * segment.length ** 2)

        if segment.kd == 0 and abs(segment.kappa0) < 1e-12:
            turns, chord = [0], Fraction(segment.length)
        elif segment.kd == 0:
            radius = 1.0 / abs(segment.kappa0)
            count = max(1, round(abs(sweep) / alpha))
            turns = [1 if sweep > 0 else -1] * count
            chord = Fraction(2.0 * radius * math.sin(abs(sweep) / (2 * count)))
        else:
            peak = max(1, round((math.sqrt(1 + 8 * abs(sweep) / alpha) - 1) / 2))
            turns = (list(range(peak + 1)) if sweep > 0
                     else list(range(peak, -1, -1)))
            chord = Fraction(segment.length / (peak + 1))

        local = Spiral(triangle, length=chord).extend(turns)
        for x, y in local.nodes[1:]:
            points.append((point[0] + x * heading.re - y * heading.im,
                           point[1] + x * heading.im + y * heading.re))

        heading = heading * (triangle.direction ** sum(turns))
        point = points[-1]
        ends.append(len(points) - 1)
        chords += len(turns)

    return points, ends, chords, heading


def reference(right) -> list[tuple[float, float]]:
    """P01's nodes rotated into the chain's frame: start east, at the origin."""
    angle = right["angle"]
    c, s = math.cos(-angle), math.sin(-angle)
    ox, oy = right["start"]
    return [(c * (x - ox) - s * (y - oy), s * (x - ox) + c * (y - oy))
            for x, y in right["nodes"]]


def main() -> int:
    right = fleur_right(STUDY_01)
    ref = reference(right)
    height = right["nodes"][-1][1] - right["nodes"][0][1]
    print(f"study height {height:.0f} units; P01 start heading "
          f"{math.degrees(right['angle']):.2f} deg")
    for alpha in ANGLES:
        points, ends, chords, heading = composite(right["spans"], alpha)
        drifts = [math.dist((float(points[end][0]), float(points[end][1])), node)
                  for end, node in zip(ends, ref[1:])]
        worst = max(drifts)
        print(f"alpha {alpha:5.2f} deg: {chords:4d} chords, "
              f"worst boundary drift {worst:7.2f} units "
              f"({100 * worst / height:.2f}% of height), "
              f"end heading {heading.degrees:7.2f} deg")
        print("   per span: " + " ".join(f"{d:.1f}" for d in drifts))
    print("alpha 0.125 deg reaches 0.11%; 0.0625 deg did not finish in 60 s.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
