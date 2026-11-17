"""Spine and character rails for one book plate.

A **character rail** is not a plain parallel offset. It starts at the same
`±d` from the spine, but bows: the rail is the parallel plus the difference
between integrating the speed turned slightly at each station and integrating
it untouched, weighted by `4t(1−t)` so the difference vanishes at both ends.
That is the sandbox's construction (`workbench/ph_nth_panels.js`,
`characterRail`), reproduced here for the plate export.

- `d = width.percent / 100 × the spine's bounding-box diagonal`.
- `eps = 0.08 × plus` on the left, `0.08 × minus` on the right.
- the bow profile: `bow = 4t(1−t)`, `s = 8t(1−t)(1−2t)`,
  `taper = 6.75 t²(1−t)`.

The curves come from `workbench/real-curves.json` (the operator's kept set).
If `|d·κ|` is too large the width is reduced until the base offset no longer
folds; if it still folds at the floor, the plate is drawn spine-only and says
so. Nothing here claims exactness: the spine is exact PH, the character is a
drawing.
"""

from __future__ import annotations

import json
import math
import sys
from functools import lru_cache
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab import ph_offset as ph  # noqa: E402

STEPS = 700
DEFAULT_WIDTH = 1.5
DEFAULT_PLUS = 2.0
DEFAULT_MINUS = 2.0
DEFAULT_PROFILE = "bow"
WIDTH_FLOOR = 0.2
FOLD_LIMIT = 0.9


@lru_cache(maxsize=1)
def _curves() -> dict:
    path = ROOT / "workbench" / "real-curves.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return {row["name"]: row for row in data["curves"]}


def _value(poly, t):
    total = 0.0
    for coefficient in reversed(poly):
        total = total * t + float(coefficient)
    return total


def _spine(u, v, steps=STEPS):
    """Position, tangent and normal at every station, integrated like the page."""
    out = []
    x = y = 0.0
    for i in range(steps + 1):
        t = i / steps
        p, q = _value(u, t), _value(v, t)
        speed2 = p * p + q * q
        tx = (p * p - q * q) / speed2 if speed2 > 1e-12 else 1.0
        ty = 2 * p * q / speed2 if speed2 > 1e-12 else 0.0
        out.append({"t": t, "x": x, "y": y, "tx": tx, "ty": ty,
                    "nx": -ty, "ny": tx})
        if i < steps:
            tm = (i + 0.5) / steps
            pm, qm = _value(u, tm), _value(v, tm)
            x += (pm * pm - qm * qm) / steps
            y += 2 * pm * qm / steps
    return out


def _profile(name, t):
    if name == "s":
        return 8 * t * (1 - t) * (1 - 2 * t)
    if name == "taper":
        return 6.75 * t * t * (1 - t)
    return 4 * t * (1 - t)


def _integrate(start, u, v, steps, eps=0.0, bump=None):
    """Integrate (u² − v², 2uv); with `eps`, turn the speed by eps·bump(t)."""
    x, y = start
    points = [(x, y)]
    for i in range(steps):
        t = (i + 0.5) / steps
        p, q = _value(u, t), _value(v, t)
        if eps:
            a = eps * bump(t)
            p, q = p - a * q, q + a * p
        x += (p * p - q * q) / steps
        y += 2 * p * q / steps
        points.append((x, y))
    return points


def _rail(spine, u, v, distance, sign, strength, profile, shear, steps=STEPS):
    start_spine = spine[0]
    start = (start_spine["x"] + sign * distance * start_spine["nx"],
             start_spine["y"] + sign * distance * start_spine["ny"])
    flat = _integrate(start, u, v, steps)
    bump = lambda t: _profile(profile, t)
    turned = _integrate(start, u, v, steps, eps=0.08 * strength, bump=bump)
    out = []
    for i, station in enumerate(spine):
        t = i / steps
        parallel = (station["x"] + sign * distance * station["nx"] + shear * t * station["tx"],
                    station["y"] + sign * distance * station["ny"] + shear * t * station["ty"])
        weight = 4 * t * (1 - t)
        out.append((parallel[0] + weight * (turned[i][0] - flat[i][0]),
                    parallel[1] + weight * (turned[i][1] - flat[i][1])))
    return out


def _bbox(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


def _diagonal(points):
    x0, y0, x1, y1 = _bbox(points)
    return math.hypot(x1 - x0, y1 - y0)


def load(spec) -> dict:
    """Spine, character rails, and the numbers a plate needs."""
    row = _curves().get(spec["name"])
    if row is None:
        raise KeyError(f"{spec['name']} is not in workbench/real-curves.json")
    u = [Fraction(str(value)) for value in row["speedX"]]
    v = [Fraction(str(value)) for value in row["speedY"]]
    width = float((row.get("width") or {}).get("percent", DEFAULT_WIDTH))
    character = row.get("character") or {}
    plus = float(character.get("plus", DEFAULT_PLUS))
    minus = float(character.get("minus", DEFAULT_MINUS))
    profile = character.get("profile", DEFAULT_PROFILE)
    if profile not in ("bow", "s", "taper"):
        profile = DEFAULT_PROFILE
    shear = float(row.get("shear", 0.0))

    spine = _spine(u, v)
    size = _diagonal([(station["x"], station["y"]) for station in spine])
    peak = ph.curvature_peak(u, v, samples=400)
    distance = width / 100.0 * size
    while abs(distance) * peak > FOLD_LIMIT and width > WIDTH_FLOOR:
        width /= 2.0
        distance = width / 100.0 * size
    rails = []
    if abs(distance) * peak <= FOLD_LIMIT:
        rails.append(_rail(spine, u, v, distance, 1, plus, profile, shear))
        rails.append(_rail(spine, u, v, distance, -1, minus, profile, shear))
        rail_note = f"character rails · width {width:g}% · {profile} {plus:g}/{minus:g}"
    else:
        distance = 0.0
        rail_note = f"rail folds at the {WIDTH_FLOOR:g}% floor · spine only"
    spine_points = [(station["x"], station["y"]) for station in spine]
    box = _bbox(spine_points + [point for rail in rails for point in rail])
    return {
        "name": spec["name"],
        "spine": spine_points,
        "rails": rails,
        "bbox": box,
        "size": size,
        "width": width,
        "plus": plus,
        "minus": minus,
        "profile": profile,
        "distance": distance,
        "fold": abs(distance) * peak,
        "note": rail_note,
    }
