"""The practical curve: the same study, fitted for a small SVG.

The exact study keeps one straight segment per chain chord, so the writer emits
one cubic per chord: 221 for the right half at a 0.5 degree step, plus the band,
plus the mirror. That is the right file when the plan is the point. It is the
wrong file to put twenty studies in a contact sheet.

This module walks the study's *structural* runs (the spans between its declared
corners), fits one clothoid through each run's endpoints and end tangents, and
subdivides a run only when the measured distance from the fitted curve to the
chain exceeds the tolerance. At 0.5 mm the half needs 14 clothoids and the band
4; with the mirror the page is 32 cubics instead of 1,164, at a measured 0.41 mm
worst deviation.

The tolerance is in design units, which are millimetres at 1:1. Three useful
settings:

- 0.25 mm: 22 clothoids, 0.22 mm worst, 40 cubics with the mirror.
- 0.5 mm: 18 clothoids, 0.41 mm worst, 32 cubics. The default.
- 1.0 mm: 16 clothoids, 0.91 mm worst, 28 cubics.

A capital C in a serif face is drawn with roughly 18 to 42 quadratic segments
(Times 21, Baskerville 19, Didot 38, Big Caslon 42), and `@` and `&` with 45 to
94. At 14 clothoids the practical half is in the same order as one letter C;
the exact version, at 221, is an order of magnitude past the whole glyph.

Pins
----

The practical curve is not a fixed simplification. The exact chain is what you
zoom into to choose a branch, and a chosen branch must land on a real vertex
with the exact heading, or the join is a lie. A **pin** is that choice: a point
on the exact chain (or its index) that becomes a hard split and a shared
tangent. The run is re-fitted through the pin, both sides use the chain's
outgoing heading there, and the rest of the curve is re-simplified within the
same tolerance. Add a branch, add its pin, re-run; the junction stays exact.
"""

from __future__ import annotations

import math

from . import engine, interpolate
from .clearance import segment_distance
from .grammar import STUDY_01, band, fleur_right
from .model import Design
from .piece import Piece, Trace

TOLERANCE = 0.5
MAX_PIECES_PER_RUN = 8


def _slices(points, ends):
    """The point runs between the study's structural span ends."""
    runs, previous = [], 0
    for end in ends:
        runs.append(points[previous:end + 1])
        previous = end
    return runs


def _heading(points, index, outgoing=True):
    """The exact chain's heading at a knot: the chord leaving or arriving."""
    if outgoing:
        first, last = index, min(index + 1, len(points) - 1)
    else:
        first, last = max(index - 1, 0), index
    return math.atan2(points[last][1] - points[first][1],
                      points[last][0] - points[first][0])


def _pin_indices(points, pins):
    """Pin positions or indices, as knot indices."""
    indices = set()
    for pin in pins or ():
        if isinstance(pin, int):
            indices.add(max(0, min(pin, len(points) - 1)))
        else:
            indices.add(min(range(len(points)),
                            key=lambda i: math.dist(points[i], pin)))
    return indices


def _anchors(run, count, theta0=None, theta1=None):
    """`count + 1` anchors by arc length, with the local end tangents."""
    lengths = [0.0]
    for a, b in zip(run, run[1:]):
        lengths.append(lengths[-1] + math.dist(a, b))
    total = lengths[-1]
    indices = []
    for k in range(count + 1):
        want = total * k / count
        index = min(range(len(lengths)), key=lambda j: abs(lengths[j] - want))
        if indices and index <= indices[-1]:
            index = min(indices[-1] + 1, len(run) - 1)
        indices.append(index)
    anchors = [run[i] for i in indices]
    thetas = []
    for k, i in enumerate(indices):
        if k == 0:
            first, last = i, min(i + 1, len(run) - 1)
        elif k == len(indices) - 1:
            first, last = max(i - 1, 0), i
        else:
            first, last = i - 1, i + 1
        thetas.append(math.atan2(run[last][1] - run[first][1],
                                 run[last][0] - run[first][0]))
    if theta0 is not None:
        thetas[0] = theta0
    if theta1 is not None:
        thetas[-1] = theta1
    return anchors, thetas


def deviation(design, points, samples: int = 300) -> float:
    """Worst distance from a fitted chain to the chain it replaces."""
    chain = engine.build(design)
    worst = 0.0
    for k in range(samples + 1):
        s = min(chain.length * k / samples, chain.length * (1 - 1e-9))
        point = chain.point(s)
        best = min(segment_distance(point, point, a, b)[0]
                   for a, b in zip(points, points[1:]))
        worst = max(worst, best)
    return worst


def fit_run(run, tolerance: float, theta0=None, theta1=None):
    """The fewest clothoids through the run that stay inside `tolerance`."""
    for count in range(1, MAX_PIECES_PER_RUN + 1):
        anchors, thetas = _anchors(run, count, theta0, theta1)
        design = interpolate.from_points(anchors, thetas, name="run")
        error = deviation(design, run, samples=120)
        if error <= tolerance:
            return design, error, count
    raise ValueError(
        f"a run of {len(run)} points needs more than {MAX_PIECES_PER_RUN} "
        f"clothoids at {tolerance:g} mm (best {error:.2f} mm)")


def design_from_runs(points, ends, tolerance: float = TOLERANCE, pins=()):
    """Assemble the runs into one design, splitting at pins and corners.

    `pins` are points on the exact chain, or knot indices. Each becomes a hard
    split, and the two sides share the chain's outgoing heading there, so a
    branch can attach without a measured correction.
    """
    points = [(float(x), float(y)) for x, y in points]
    pin_indices = _pin_indices(points, pins)
    runs = []
    previous = 0
    for end in ends:
        runs.append((previous, end))
        previous = end

    segments = []
    anchor = None
    previous_end = None
    report = []
    pin_report = []

    for start, end in runs:
        cuts = [start]
        cuts.extend(sorted(i for i in pin_indices if start < i < end))
        cuts.append(end)
        for a, b in zip(cuts, cuts[1:]):
            run = points[a:b + 1]
            theta0 = _heading(points, a, outgoing=True)
            if b == end:
                theta1 = _heading(points, b, outgoing=False)
            else:
                theta1 = _heading(points, b, outgoing=True)
            design, error, count = fit_run(run, tolerance, theta0, theta1)

            if anchor is None:
                anchor = dict(design.anchor)
            else:
                design.segments[0].corner = math.atan2(
                    math.sin(design.anchor["angle"] - previous_end),
                    math.cos(design.anchor["angle"] - previous_end))

            chain = engine.build(design)
            end_point = chain.point(chain.length * (1 - 1e-9))
            if b in pin_indices:
                pin_report.append({
                    "index": b,
                    "point": points[b],
                    "error": math.dist(end_point, points[b]),
                })
            previous_end = chain.tangent(chain.length * (1 - 1e-9))
            segments.extend(design.segments)
            report.append({"pieces": count, "error": error})

    return Design(name="practical", segments=segments, anchor=anchor,
                  g1=True), {"runs": report, "pins": pin_report}


def practical_study_01(tolerance: float = TOLERANCE, pins=()):
    """The study as a practical piece, plus its measured report."""
    right = fleur_right(STUDY_01)
    ring = band(STUDY_01)

    half_points, half_ends, _ = _composite(right)
    band_points, band_ends, _ = _composite(ring)

    half, half_report = design_from_runs(half_points, half_ends, tolerance,
                                         pins)
    rim, band_report = design_from_runs(band_points, band_ends, tolerance)

    piece = Piece(
        name="Fleur study 01 — practical curve",
        mirror=True,
        stroke=0.6,
        traces=[Trace("half", half), Trace("band", rim, mirror=False)],
    )
    report = {
        "tolerance": tolerance,
        "segments": len(half.segments) + len(rim.segments),
        "half": half_report["runs"],
        "band": band_report["runs"],
        "pins": half_report["pins"],
        "deviation": max(item["error"] for item in
                         half_report["runs"] + band_report["runs"]),
    }
    return piece, report


def _composite(study):
    from . import spine_study

    return spine_study.composite(study["spans"], 0.5, start=study["start"],
                                 heading=study["angle"])
