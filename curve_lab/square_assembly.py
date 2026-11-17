"""Four curves on the edges of a square (a polygon follows the same rule).

The curve is a cubic whose chord runs from P0 to P3. Put the chord on the
square's edge, one copy per edge, each turned to its edge. The one angle a
curve can offer a corner is its **leg**, the tangent at the chord's end. The
rule is:

    the leg bisects the corner

So a 90° corner wants a 45° leg, and the two legs that meet there are at right
angles — a miter. For a regular n-gon the leg is 90° − 180°/n; a pentagram
point wants 18°, a pentagon 54°.

`stretch_to_leg` reaches that angle by scaling the curve across its chord, not
by turning the chord: the ends stay on the edge, which is what keeps the square
closed at the measured side.

Everything is floats and analytic; the curves are the caller's own cubics.
"""

from __future__ import annotations

import math

Point = tuple[float, float]
Cubic = list[Point]


def cubic_at(points: Cubic, t: float) -> Point:
    mt = 1.0 - t
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = points
    return (mt ** 3 * x0 + 3 * mt * mt * t * x1 + 3 * mt * t * t * x2 + t ** 3 * x3,
            mt ** 3 * y0 + 3 * mt * mt * t * y1 + 3 * mt * t * t * y2 + t ** 3 * y3)


def cubic_derivative(points: Cubic, t: float) -> Point:
    mt = 1.0 - t
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = points
    return (3 * mt * mt * (x1 - x0) + 6 * mt * t * (x2 - x1) + 3 * t * t * (x3 - x2),
            3 * mt * mt * (y1 - y0) + 6 * mt * t * (y2 - y1) + 3 * t * t * (y3 - y2))


def chord_length(points: Cubic) -> float:
    return math.hypot(points[3][0] - points[0][0], points[3][1] - points[0][1])


def start_leg(points: Cubic) -> float:
    """The start tangent's angle above the chord, in degrees."""
    dx, dy = cubic_derivative(points, 0.0)
    return math.degrees(math.atan2(dy, dx))


def end_leg(points: Cubic) -> float:
    dx, dy = cubic_derivative(points, 1.0)
    return math.degrees(math.atan2(dy, dx))


def stretch_to_leg(points: Cubic, leg_degrees: float) -> Cubic:
    """Scale across the chord so the start leg is `leg_degrees` above it.

    The chord is the x axis, so only y changes; the ends stay put. A leg below
    the chord is mirrored first, so the curve arches inside the polygon.
    """
    out = list(points)
    if start_leg(out) < 0:
        out = [(x, -y) for x, y in out]
    dx, dy = cubic_derivative(out, 0.0)
    if dy == 0:
        raise ValueError("the start tangent is parallel to the chord")
    factor = math.tan(math.radians(leg_degrees)) * dx / dy
    return [(x, y * factor) for x, y in out]


def rotate(points: Cubic, degrees: float) -> Cubic:
    angle = math.radians(degrees)
    c, s = math.cos(angle), math.sin(angle)
    return [(x * c - y * s, x * s + y * c) for x, y in points]


def translate(points: Cubic, origin: Point) -> Cubic:
    return [(x + origin[0], y + origin[1]) for x, y in points]


def scale(points: Cubic, factor: float) -> Cubic:
    return [(x * factor, y * factor) for x, y in points]


def square_edges(side: float):
    """The four edges, counter-clockwise, as (name, start, direction)."""
    return [
        ("south", (0.0, 0.0), 0.0),
        ("east", (side, 0.0), 90.0),
        ("north", (side, side), 180.0),
        ("west", (0.0, side), 270.0),
    ]


def assemble(points: Cubic, side: float | None = None,
             leg_degrees: float | None = None) -> list[dict]:
    """One copy per edge, inside the square.

    `side` defaults to the curve's chord. `leg_degrees` stretches each copy so
    its leg is that angle; None leaves the curve as drawn.
    """
    length = chord_length(points)
    if length <= 0:
        raise ValueError("the chord has no length")
    side = length if side is None else float(side)
    curve = scale(points, side / length)
    if leg_degrees is not None:
        curve = stretch_to_leg(curve, leg_degrees)
    out = []
    for name, origin, direction in square_edges(side):
        placed = translate(rotate(curve, direction), origin)
        out.append({
            "name": name,
            "points": placed,
            "start": cubic_at(placed, 0.0),
            "end": cubic_at(placed, 1.0),
            "start_leg": start_leg(rotate(curve, direction)),
            "end_leg": end_leg(rotate(curve, direction)),
        })
    return out


def corner_kinks(curves: list[dict]) -> list[tuple[str, float]]:
    """The angle between the tangent lines where adjacent edges meet.

    0 is a smooth continuation; 90 is a clean miter (the two legs are
    perpendicular). Anything else is a visible corner.
    """
    out = []
    for index, curve in enumerate(curves):
        following = curves[(index + 1) % len(curves)]
        a = curve["end_leg"]
        b = following["start_leg"]
        difference = abs(a - b) % 180.0
        out.append((f"{curve['name']}->{following['name']}",
                    min(difference, 180.0 - difference)))
    return out


def ring_kinks(curves: list[dict]) -> list[tuple[str, float]]:
    """The same measurement for a chain: every join, including the wrap."""
    out = []
    for index, curve in enumerate(curves):
        following = curves[(index + 1) % len(curves)]
        difference = abs(curve["end_leg"] - following["start_leg"]) % 180.0
        out.append((f"{curve['name']}{curve.get('copy', '')}->"
                    f"{following['name']}{following.get('copy', '')}",
                    min(difference, 180.0 - difference)))
    return out


def frame(points: Cubic, per_side: int = 3,
          leg_degrees: float | None = None,
          alternate: bool = False,
          side: float | None = None) -> dict:
    """A border of `per_side` copies on each edge.

    The side defaults to `per_side × the chord`, so three curves fill one side
    end to end; pass `side` to set the total and let each copy shorten to fit.
    `alternate` flips every other copy across the chord, which makes the joins
    inside a side continuous at the cost of a kink at the corners.
    """
    if per_side < 1:
        raise ValueError("a frame needs at least one curve per side")
    length = chord_length(points)
    if length <= 0:
        raise ValueError("the chord has no length")
    side = per_side * length if side is None else float(side)
    copy_length = side / per_side
    base = stretch_to_leg(points, leg_degrees) if leg_degrees is not None \
        else list(points)
    base = scale(base, copy_length / length)
    curves = []
    for name, origin, direction in square_edges(side):
        for copy in range(per_side):
            shape = base
            if alternate and copy % 2:
                shape = [(x, -y) for x, y in base]
            local = translate(shape, (copy * copy_length, 0.0))
            placed = translate(rotate(local, direction), origin)
            curves.append({
                "name": name,
                "copy": f"[{copy}]",
                "points": placed,
                "start": cubic_at(placed, 0.0),
                "end": cubic_at(placed, 1.0),
                "start_leg": start_leg(rotate(shape, direction)),
                "end_leg": end_leg(rotate(shape, direction)),
            })
    return {"side": side, "curves": curves, "kinks": ring_kinks(curves)}
