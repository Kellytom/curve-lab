"""How an open ribbon ends: butt, point, arc, round and taper.

A terminal is geometry, not a stroke hint. `render_piece` already draws a ribbon
as two offset rails; a terminal adds the few spans that bridge those rail ends,
so the end shape survives export to a tool that ignores `stroke-linecap`.

The frame here is the one the rest of the package uses: y up, millimetres,
control points in the design plane. The SVG writer flips y once, at output.

- `butt`  the rails simply stop: the existing blunt end, and the baseline.
- `point` the rails meet at a sharp tip one half-width beyond the end.
- `arc`   one shallow dome, radius 5 mm, so it reads as a cut corner.
- `round` one dome of radius half the ribbon width: a semicircular end.
- `taper` the rails converge over several half-widths to a narrow tip.
"""

from __future__ import annotations

import math

TERMINALS = ("butt", "point", "arc", "round", "taper")
ARC_RADIUS = 5.0
TAPER_FACTOR = 4.0


def check_terminal(kind: str) -> str:
    """Return the terminal name, or raise for anything not in the vocabulary."""
    if kind not in TERMINALS:
        raise ValueError(
            f"unknown terminal {kind!r}; expected one of {', '.join(TERMINALS)}"
        )
    return kind


def terminal_extension(kind: str, width: float) -> float:
    """How far the end reaches past the rail ends, in millimetres."""
    check_terminal(kind)
    half = width / 2.0
    if kind == "butt":
        return 0.0
    if kind in ("point", "round"):
        return half
    if kind == "arc":
        radius = max(ARC_RADIUS, half)
        return radius - math.sqrt(radius * radius - half * half)
    return TAPER_FACTOR * half


def _unit(dx: float, dy: float) -> tuple[float, float]:
    length = math.hypot(dx, dy)
    if length < 1e-9:
        raise ValueError("terminal tangent is degenerate")
    return dx / length, dy / length


def _end(spans: list[dict], end: str) -> tuple[tuple[float, float], tuple[float, float]]:
    """The rail's end point and the outward unit tangent there."""
    if end not in ("start", "end"):
        raise ValueError(f"end must be 'start' or 'end', got {end!r}")
    if end == "end":
        span = spans[-1]
        point = span["p3"]
        dx, dy = point[0] - span["c2"][0], point[1] - span["c2"][1]
        if math.hypot(dx, dy) < 1e-9:
            dx, dy = point[0] - span["p0"][0], point[1] - span["p0"][1]
    else:
        span = spans[0]
        point = span["p0"]
        dx, dy = point[0] - span["c1"][0], point[1] - span["c1"][1]
        if math.hypot(dx, dy) < 1e-9:
            dx, dy = point[0] - span["p3"][0], point[1] - span["p3"][1]
    tangent = _unit(dx, dy)
    return (float(point[0]), float(point[1])), tangent


def _span(p0, p3, c1, c2) -> dict:
    return {
        "p0": (float(p0[0]), float(p0[1])),
        "c1": (float(c1[0]), float(c1[1])),
        "c2": (float(c2[0]), float(c2[1])),
        "p3": (float(p3[0]), float(p3[1])),
    }


def _straight(p0, p3) -> dict:
    a = ((p3[0] - p0[0]) / 3.0, (p3[1] - p0[1]) / 3.0)
    return _span(p0, p3, (p0[0] + a[0], p0[1] + a[1]),
                 (p3[0] - a[0], p3[1] - a[1]))


def _dome(p_pos, p_neg, outward, sagitta: float) -> dict:
    """One cubic whose midpoint sits `sagitta` past the chord and whose ends
    leave along `outward`, so it joins the rails without a kink."""
    pull = 4.0 / 3.0 * sagitta
    c1 = (p_pos[0] + outward[0] * pull, p_pos[1] + outward[1] * pull)
    c2 = (p_neg[0] + outward[0] * pull, p_neg[1] + outward[1] * pull)
    return _span(p_pos, p_neg, c1, c2)


def terminal_spans(rail_pos: dict, rail_neg: dict, kind: str,
                   end: str = "end", radius: float = ARC_RADIUS,
                   taper: float = TAPER_FACTOR) -> list[dict]:
    """Spans that close one ribbon end, running from the +half rail to the -half.

    `rail_pos` and `rail_neg` are the built rails at +width/2 and -width/2, so
    the cap starts on the real rail ends rather than on an idealised offset.
    `butt` returns no spans: the blunt end is the rails stopping.
    """
    check_terminal(kind)
    if kind == "butt":
        return []

    p_pos, t_pos = _end(rail_pos["spans"], end)
    p_neg, t_neg = _end(rail_neg["spans"], end)

    half = math.hypot(p_pos[0] - p_neg[0], p_pos[1] - p_neg[1]) / 2.0
    if half <= 1e-9:
        raise ValueError("a terminal needs a ribbon with a width")

    mid = ((p_pos[0] + p_neg[0]) / 2.0, (p_pos[1] + p_neg[1]) / 2.0)
    outward = _unit(t_pos[0] + t_neg[0], t_pos[1] + t_neg[1])

    if kind == "point":
        apex = (mid[0] + outward[0] * half, mid[1] + outward[1] * half)
        return [_straight(p_pos, apex), _straight(apex, p_neg)]

    if kind == "taper":
        length = taper * half
        apex = (mid[0] + outward[0] * length, mid[1] + outward[1] * length)
        shoulder = length * 0.5
        waist = length * 0.25
        return [
            _span(
                p_pos, apex,
                (p_pos[0] + outward[0] * shoulder, p_pos[1] + outward[1] * shoulder),
                (apex[0] - outward[0] * waist, apex[1] - outward[1] * waist),
            ),
            _span(
                apex, p_neg,
                (apex[0] - outward[0] * waist, apex[1] - outward[1] * waist),
                (p_neg[0] + outward[0] * shoulder, p_neg[1] + outward[1] * shoulder),
            ),
        ]

    if kind == "arc":
        r = max(radius, half)
        sagitta = r - math.sqrt(r * r - half * half)
    else:  # round: a semicircle, whose radius is the half width
        sagitta = half
    return [_dome(p_pos, p_neg, outward, sagitta)]
