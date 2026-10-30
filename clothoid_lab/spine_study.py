"""Gate 4 candidate: study 01 drawn as Pythagorean chains.

This is the law-fitted route, option A in `docs/SESSIONS.md`. Each span of the
old study is walked in the law the chain already speaks:

- a line is zero turns over one chord,
- a circular arc is a constant turn per chord,
- an Euler span is turns 0, 1, 2, ... (heading quadratic in the chord index),
- a corner between spans is a whole number of triangle turns.

Everything is built in exact rational arithmetic: the chords are `Fraction`
lengths along `Dir` headings, so every node before placement is rational. The
result is a composite chain, one point list per stroke, handed to the engine as
straight segments with the chain's own corner at each node.

It is **not** P01's node table. P01's start heading is 77.97 degrees and its
corners are arbitrary; the chain can only take whole triangle turns, so the
start is quantised to the nearest and each corner with it. `report()` measures
the drift; whether that drift is acceptable is the promotion-gate decision, not
this module's.
"""

from __future__ import annotations

import math
from fractions import Fraction

from .grammar import STUDY_01, band, fleur_right
from .model import Design, Segment
from .piece import Piece, Trace

ALPHA_DEG = 0.5


def _wrap(angle: float) -> float:
    return math.atan2(math.sin(angle), math.cos(angle))


def _spine():
    """The spine layer's exact types, loaded through the one bridge."""
    from . import spine

    spine.load()
    from pythagorean_spiral.spiral import Spiral
    from pythagorean_spiral.triples import for_angle

    return Spiral, for_angle


def composite(spans, alpha_deg: float = ALPHA_DEG, start=(0.0, 0.0),
              heading: float = 0.0):
    """Walk the spans as one rational chain.

    Returns `(points, ends, heading)`: every node as a `Fraction` pair, the
    index of each span's last node, and the exact final heading. The start
    heading is snapped to the nearest whole triangle turn, because a chain has
    no other kind.
    """
    Spiral, for_angle = _spine()
    alpha = math.radians(alpha_deg)
    triangle = for_angle(alpha_deg)
    direction = triangle.direction ** round(heading / alpha)
    point = (Fraction(start[0]), Fraction(start[1]))
    points = [point]
    ends: list[int] = []

    for index, segment in enumerate(spans):
        if index:
            direction = direction * (
                triangle.direction ** round(segment.corner / alpha))

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
            points.append((point[0] + x * direction.re - y * direction.im,
                           point[1] + x * direction.im + y * direction.re))

        direction = direction * (triangle.direction ** sum(turns))
        point = points[-1]
        ends.append(len(points) - 1)

    return points, ends, direction


def design_from_points(points, name: str = "chain") -> Design:
    """The composite as straight segments, one corner per node."""
    if len(points) < 2:
        raise ValueError("a chain needs at least one chord")
    segments = []
    previous = None
    first_angle = 0.0
    for (ax, ay), (bx, by) in zip(points, points[1:]):
        dx, dy = float(bx - ax), float(by - ay)
        length = math.hypot(dx, dy)
        if length <= 1e-12:
            raise ValueError("the chain has a zero-length chord")
        angle = math.atan2(dy, dx)
        if previous is None:
            first_angle = angle
            corner = 0.0
        else:
            corner = _wrap(angle - previous)
        segments.append(Segment(kd=0.0, length=length, kappa0=0.0,
                                corner=corner))
        previous = angle
    return Design(
        name=name,
        segments=segments,
        anchor={"x": float(points[0][0]), "y": float(points[0][1]),
                "angle": first_angle},
        g1=True,
    )


def study_01_from_chains(alpha_deg: float = ALPHA_DEG) -> Piece:
    """The right half mirrored, plus the band, every stroke a chain."""
    right = fleur_right(STUDY_01)
    ring = band(STUDY_01)

    half, _, _ = composite(right["spans"], alpha_deg,
                           start=right["start"], heading=right["angle"])
    rim, _, _ = composite(ring["spans"], alpha_deg,
                          start=ring["start"], heading=ring["angle"])

    return Piece(
        name="Fleur study 01 — chain candidate",
        mirror=True,
        stroke=0.6,
        traces=[
            # Centre lines: the engine's rails cross at every chain corner
            # (they are built for smooth clothoids), so the filled ribbon is the
            # spine layer's miter job, not this page's.
            Trace("half", design_from_points(half, "half")),
            Trace("band", design_from_points(rim, "band"), mirror=False),
        ],
    )


def report(alpha_deg: float = ALPHA_DEG) -> dict:
    """The drift of every span end from P01's node, plus the chain's size."""
    right = fleur_right(STUDY_01)
    points, ends, heading = composite(right["spans"], alpha_deg,
                                      start=right["start"],
                                      heading=right["angle"])
    drifts = [math.dist((float(points[end][0]), float(points[end][1])), node)
              for end, node in zip(ends, right["nodes"][1:])]
    height = right["nodes"][-1][1] - right["nodes"][0][1]
    return {
        "alpha_deg": alpha_deg,
        "chords": len(points) - 1,
        "spans": len(ends),
        "drifts": drifts,
        "worst": max(drifts),
        "worst_fraction": max(drifts) / height,
        "end_heading_deg": heading.degrees,
        "height": height,
    }
