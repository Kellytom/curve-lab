"""French curves and mirrored leaves, built from Euler spans.

    used by `scripts/showcase.py`

A French curve is a drawing aid: a short run of changing curvature, used to
join two strokes. Here each one is a chain of three clothoid spans with a
declared curvature at each join, so the shape is Euler, not a traced outline.

A leaf is one section mirrored across its own chord. The sections include the
Euler span solved through two points with two tangents, the log spiral, the
squircle arc and the integer cubic half.

Every panel here is generated; no shape is remembered.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab import engine, interpolate  # noqa: E402
from curve_lab.model import Design, Segment  # noqa: E402
from curve_lab.taper import LogSpiral  # noqa: E402
from curve_lab.pyth_cubic import case  # noqa: E402

INK = "#2e2413"

# Three spans per French curve: (kappa0, kappa1, length). Curvature is 1/mm.
FRENCH = [
    ((0.000, 0.020, 90.0), (0.020, 0.040, 70.0), (0.040, 0.010, 60.0)),
    ((0.005, 0.030, 80.0), (0.030, 0.030, 60.0), (0.030, 0.000, 70.0)),
    ((0.000, 0.015, 110.0), (0.015, 0.050, 55.0), (0.050, 0.020, 50.0)),
    ((0.010, 0.004, 70.0), (0.004, 0.035, 80.0), (0.035, 0.045, 60.0)),
    ((0.000, 0.045, 60.0), (0.045, 0.020, 75.0), (0.020, 0.000, 90.0)),
    ((-0.010, 0.010, 75.0), (0.010, 0.040, 65.0), (0.040, 0.030, 60.0)),
    ((0.020, 0.006, 65.0), (0.006, 0.028, 85.0), (0.028, 0.050, 55.0)),
    ((0.000, 0.010, 100.0), (0.010, 0.025, 75.0), (0.025, 0.055, 45.0)),
]


def _chain(profile, n=300):
    segments = [Segment(kappa0=k0, kd=(k1 - k0) / L, length=L)
                for k0, k1, L in profile]
    design = Design(segments=segments,
                    anchor={"x": 0.0, "y": 0.0, "angle": 0.0})
    chain = engine.build(design)
    return [chain.point(chain.length * i / (n - 1)) for i in range(n)]


def _midpoint_mirror(pts):
    """Mirror a section across its own chord and close it into a leaf."""
    x0, y0 = pts[0]
    x1, y1 = pts[-1]
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / L, dx / L
    out = list(pts)
    for x, y in reversed(pts[1:-1]):
        d = (x - x0) * nx + (y - y0) * ny
        out.append((x - 2.0 * d * nx, y - 2.0 * d * ny))
    out.append(pts[0])
    return out


def _euler_section(p0, t0, p1, t1, n=80):
    k0, kd, length = interpolate.fit(p0, t0, p1, t1)
    chain = engine.build(Design(
        segments=[Segment(kappa0=k0, kd=kd, length=length)],
        anchor={"x": p0[0], "y": p0[1], "angle": t0}))
    return [chain.point(chain.length * i / (n - 1)) for i in range(n)]


def french_panels():
    from showcase_catalogue import _entry

    out = []
    for i, profile in enumerate(FRENCH):
        out.append(_entry(
            len(out) + 1, f"French curve {i + 1}",
            [(_chain(profile), INK, 1.8, None)],
            "three Euler spans · curvature declared at each join",
            "scripts/curve_morphs.py FRENCH"))
    return out


def leaf_sections():
    """Eight sections, each to be mirrored across its chord."""
    out = []
    out.append(("Euler, two tangents",
                _euler_section((0.0, 0.0), 0.0, (110.0, 42.0), 1.05)))
    out.append(("Euler, steep recovery",
                _euler_section((0.0, 0.0), -0.35, (95.0, 55.0), 1.35)))
    ls = LogSpiral(14.0, 0.26)
    out.append(("log spiral",
                [ls.point(2.6 * i / 80) for i in range(81)]))
    out.append(("squircle, 45° arc", [
        (math.copysign(abs(math.cos(t)) ** 0.5, math.cos(t)),
         math.copysign(abs(math.sin(t)) ** 0.5, math.sin(t)))
        for t in [i * math.pi / 4 / 80 for i in range(81)]]))
    c = case(3, 4, 5)
    out.append(("integer cubic, half", [
        (lambda t: ((1 - t) ** 3 * c["p0"][0] + 3 * (1 - t) ** 2 * t * c["p1"][0]
                    + 3 * (1 - t) * t * t * c["p2"][0] + t ** 3 * c["p3"][0],
                    (1 - t) ** 3 * c["p0"][1] + 3 * (1 - t) ** 2 * t * c["p1"][1]
                    + 3 * (1 - t) * t * t * c["p2"][1] + t ** 3 * c["p3"][1]))(i / 80)
        for i in range(81)]))
    out.append(("circle, quarter", [
        (80.0 * math.sin(t), 80.0 * (1 - math.cos(t)))
        for t in [i * math.pi / 2 / 80 for i in range(81)]]))
    out.append(("cycloid, half arch", [
        (40.0 * (t - math.sin(t)), 40.0 * (1 - math.cos(t)))
        for t in [i * math.pi / 80 for i in range(81)]]))
    out.append(("astroid, quadrant", [
        (50.0 * math.cos(t) ** 3, 50.0 * math.sin(t) ** 3)
        for t in [i * math.pi / 2 / 80 for i in range(81)]]))
    return out


def leaf_panels():
    from showcase_catalogue import _entry

    out = []
    for title, section in leaf_sections():
        out.append(_entry(
            len(out) + 1, f"leaf · {title}",
            [(_midpoint_mirror(section), INK, 1.7, None)],
            "one section, mirrored across its chord",
            "scripts/curve_morphs.py leaf_sections"))
    return out
