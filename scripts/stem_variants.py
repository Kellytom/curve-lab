"""Stem kinds the showcase was missing.

The catalogue was a sampler: one representative per family. These are the
shapes a stem is actually cut from, and each is one curve you can pick and
take to Inkscape:

- half a parabola, vertex outwards;
- one wing of a hyperbola;
- a recovered LAC spine cut where its heading has turned 90° or 130°;
- an Euler S that swings from +θ to −θ, including the 3/4 slope (36.87°).

Every case returns a polyline in model units, +y up.
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from curve_lab import engine  # noqa: E402
from curve_lab.model import Design, Segment  # noqa: E402


def parabola_half(t1: float = 2.4, n: int = 240):
    """y = x²/2 from the vertex to x = t1. The other half is its mirror."""
    return [(t1 * i / n, 0.5 * (t1 * i / n) ** 2) for i in range(n + 1)]


def hyperbola_wing(t1: float = 1.6, n: int = 240):
    """x² − y² = 1, the x > 0 wing from the vertex upward."""
    out = []
    for i in range(n + 1):
        t = t1 * i / n
        out.append((math.cosh(t), math.sinh(t)))
    return out


def heading_turn(pts):
    """Total signed heading change, in degrees, along a polyline."""
    total = 0.0
    prev = None
    for a, b in zip(pts, pts[1:]):
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        if prev is not None:
            d = ang - prev
            while d > math.pi:
                d -= 2 * math.pi
            while d < -math.pi:
                d += 2 * math.pi
            total += d
        prev = ang
    return math.degrees(total)


_LAC_CARDS = None


def lac_cut(degrees: float, card_name: str = "p = 0, turn 270"):
    """A recovered LAC spine, cut where its heading has turned `degrees`.

    The full spine turns 270°; a stem only wants the first part, which is how
    the 0–90° and 0–130° stems in the stem library were made.
    """
    global _LAC_CARDS
    if _LAC_CARDS is None:
        import stem_library as SL
        SL.build()
        _LAC_CARDS = [c for c in SL.CARDS if c["group"] == "Log-aesthetic"]
    card = next(c for c in _LAC_CARDS if card_name in c["name"])
    pts = max(card["branches"], key=len)
    want = abs(math.radians(degrees))
    total = 0.0
    prev = None
    for i in range(1, len(pts)):
        a, b = pts[i - 1], pts[i]
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        if prev is not None:
            d = ang - prev
            while d > math.pi:
                d -= 2 * math.pi
            while d < -math.pi:
                d += 2 * math.pi
            total += d
        prev = ang
        if abs(total) >= want:
            return pts[:i + 1]
    return pts


def euler_swing(degrees: float, length: float = 6.0, n: int = 400):
    """Two Euler spans whose heading runs from +θ at the join to −θ at the end.

    The first span turns +θ (curvature 0 → +κ). The second runs curvature
    +κ → −6κ, which turns the heading back through −θ — the S, not a bend.
    """
    kappa = 2.0 * math.radians(degrees) / (length * length)   # first span turn
    design = Design(
        name=f"euler swing ±{degrees:g}",
        segments=[Segment(kd=kappa, length=length),
                  Segment(kd=-4.0 * kappa, length=length)],
        anchor={"x": 0.0, "y": 0.0, "angle": 0.0},
        stroke=1.0,
    )
    chain = engine.build(design)
    return [chain.point(chain.length * i / (n - 1)) for i in range(n)]


def heading_profile(pts):
    """Headings relative to the first segment, in degrees."""
    angs = [math.atan2(b[1] - a[1], b[0] - a[0])
            for a, b in zip(pts, pts[1:])]
    a0 = angs[0]
    return [math.degrees((a - a0 + math.pi) % (2 * math.pi) - math.pi)
            for a in angs]


def measured_swing(pts):
    """(join heading, extreme heading, end heading) in degrees, measured."""
    prof = heading_profile(pts)
    return (prof[len(prof) // 2],
            max(prof, key=abs),
            prof[-1])


def cases():
    """(title, points, note, source) — one curve each."""
    s30 = euler_swing(30)
    s75 = euler_swing(math.degrees(math.atan(0.75)))
    j30, p30, e30 = measured_swing(s30)
    j75, p75, e75 = measured_swing(s75)
    out = [
        ("parabola · half stem",
         parabola_half(),
         "y = x²/2 from the vertex · the other half is the mirror",
         "curve_lab · parabola in y"),
        ("hyperbola · one wing",
         hyperbola_wing(),
         "x² − y² = 1, x > 0 · the other wing is its mirror",
         "curve_lab · conic"),
        ("Euler S · +30° to −30°",
         s30,
         f"two clothoid spans · join {j30:.1f}°, peak {p30:.1f}°, end {e30:.1f}°",
         "curve_lab.model.Design · two Segment(kd) spans"),
        ("Euler S · ±3/4 slope",
         s75,
         f"the same S at atan(3/4) = {math.degrees(math.atan(0.75)):.2f}° · join {j75:.1f}°, end {e75:.1f}°",
         "curve_lab.model.Design · two Segment(kd) spans"),
    ]
    # every recovered spine, cut where a stem actually ends: 0–90° and 0–130°
    import stem_library as SL
    SL.build()
    lac = [c for c in SL.CARDS if c["group"] == "Log-aesthetic"]
    for i, card in enumerate(lac):
        for degrees in (90, 130):
            pts = lac_cut(degrees, card_name=card["name"])
            m = re.search(r"p = ([\-\d./]+)", card["name"])
            dial = m.group(1) if m else "?"
            out.append((
                f"S{35 + i:02d} · p = {dial} · cut at {degrees}°",
                pts,
                f"{card['name']} · measured turn {abs(heading_turn(pts)):.1f}°",
                "workbench/spirals/lac.json · stem library",
            ))
    return out


if __name__ == "__main__":
    for title, pts, note, source in cases():
        print(f"{title}: {len(pts)} points · {note}")
