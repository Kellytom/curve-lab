"""Stage II: the plates.  Offsets, then branches.

    .venv/bin/python scripts/stage_two.py
    open docs/stage-two.html

A *spine* is a chain of chords turned by the triple's angle at every node.  A
*plate* is what gets drawn: an offset of the spine, or a branch of it.  The
point of this page is that both are constructions on the spine, so the chords
have to stay a chain -- the cubics come last, and are the one thing that cannot
be offset.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from curve_families import (  # noqa: E402
    THIN, aspect, doubling_chain, fitter, path_d, series_top, triple_angle,
)

ROOT = Path(__file__).resolve().parents[1]
INK = "#2e2413"
GOLD = "#c9a441"
GRID = "#e8dfc8"
LINE = "#d8ccae"

CSS = """
  :root { color-scheme: light; --paper:#f6f1e4; --card:#fffdf7; --ink:#2e2413;
    --muted:#7b6c4e; --gold:#8c6a21; --line:#d8ccae;
    --mono: ui-monospace,"SF Mono",Menlo,Consolas,monospace;
    --serif:"EB Garamond",Georgia,"Palatino Linotype",Palatino,serif; }
  * { box-sizing: border-box; }
  body { margin:0; color:var(--ink); font:16px/1.55 var(--serif);
    background: radial-gradient(900px 440px at 12% -8%, #fcf9ef 0, transparent 60%), var(--paper); }
  main { max-width: 920px; margin: 0 auto; padding: 34px 22px 70px; }
  h1 { font-size: 25px; margin: 0 0 4px; text-wrap: balance; }
  .lead { color: var(--gold); margin: 0 0 18px; }
  h2 { font: 600 11px/1.2 var(--mono); letter-spacing:.12em; text-transform:uppercase;
    color:var(--muted); margin:26px 0 8px; }
  .panel { background:var(--card); border:1px solid var(--line); border-radius:6px; padding:12px; }
  .strip { margin: 0 0 14px; }
  .strip:last-child { margin-bottom: 0; }
  .strip svg { display:block; width:100%; height:auto; background:#fff;
    border:1px solid var(--line); border-radius:3px; }
  .strip p { margin:5px 0 0; font:10px/1.3 var(--mono); color:var(--muted); }
  .strip strong { color:var(--ink); }
  table { border-collapse:collapse; width:100%; font:12px/1.5 var(--mono); }
  th, td { border-bottom:1px solid var(--line); padding:6px 4px; text-align:left; }
  th { color:var(--muted); font-weight:500; }
  .scroll { overflow-x:auto; }
  .back { font:12px var(--mono); margin-bottom:16px; }
  code { font:12px var(--mono); color:var(--gold); }
  a { color: var(--gold); }
  .next { border-left:3px solid var(--gold); padding-left:10px; color:var(--muted); }
  .two { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
  .two svg { border:1px solid var(--line); border-radius:3px; }
  @media (max-width:620px) {
    main { padding:22px 14px 60px; }
    table { font-size:10px; } th,td { padding:4px 2px; }
    .two { grid-template-columns:1fr; }
  }
"""


# -- geometry ---------------------------------------------------------------

def turn_of(points, i: int) -> float:
    """Signed turn at node i of a polyline, in radians."""
    (x0, y0), (x1, y1), (x2, y2) = points[i - 1], points[i], points[i + 1]
    a = math.atan2(y1 - y0, x1 - x0)
    b = math.atan2(y2 - y1, x2 - x1)
    d = b - a
    while d > math.pi:
        d -= 2 * math.pi
    while d < -math.pi:
        d += 2 * math.pi
    return d


def offset_chain(points, d):
    """Offset a chain by d to the left of travel (negative: right).

    Each chord is slid by d along its left normal, then consecutive slid chords
    are intersected.  That is the polygon offset, exactly: the node angles do
    not change and every chord shortens by d*tan(turn/2) at each end.
    """
    if d == 0:
        return list(points)
    segs = []
    for i in range(len(points) - 1):
        (x0, y0), (x1, y1) = points[i], points[i + 1]
        dx, dy = x1 - x0, y1 - y0
        length = math.hypot(dx, dy)
        ux, uy = dx / length, dy / length
        segs.append(((x0 - uy * d, y0 + ux * d), (ux, uy), length))

    out = [segs[0][0]]
    for i in range(1, len(segs)):
        (p0, u0, _), (p1, u1, _) = segs[i - 1], segs[i]
        denom = u0[0] * u1[1] - u0[1] * u1[0]
        if abs(denom) < 1e-12:
            out.append(p1)
            continue
        t = ((p1[0] - p0[0]) * u1[1] - (p1[1] - p0[1]) * u1[0]) / denom
        out.append((p0[0] + u0[0] * t, p0[1] + u0[1] * t))
    (sx, sy), (ux, uy), length = segs[-1]
    turn = abs(turn_of(points, len(points) - 2))
    trim = abs(d) * math.tan(turn / 2)
    out.append((sx + ux * length, sy + uy * length))     # free end, untrimmed
    return out


def closing_distance(points, d_sign: float = 1.0) -> float:
    """The offset at which the shortest chord is eaten up."""
    shortest = min(math.dist(points[i], points[i + 1])
                   for i in range(len(points) - 1))
    turn = abs(turn_of(points, 1))
    return shortest / (2 * math.tan(turn / 2))


def effective_b(points, triple) -> float:
    """The chain's own log-spiral rate: ln(first chord / last chord) / turn."""
    chords = [math.dist(points[i], points[i + 1]) for i in range(len(points) - 1)]
    turn = len(chords) * triple_angle(triple)
    return math.log(chords[-1] / chords[0]) / turn


def arc_cubic(points, i0: int, i1: int):
    """One cubic over nodes i0..i1 by the parabola rule.

    The arm is chord/(3 cos^2(delta/2)); that is exact for a circular arc, and
    the repo uses it for every span (`pythagorean_spiral/spans.py`).
    """
    p0, p3 = points[i0], points[i1]
    chord = math.dist(p0, p3)
    t0 = math.atan2(points[i0 + 1][1] - p0[1], points[i0 + 1][0] - p0[0])
    t1 = math.atan2(p3[1] - points[i1 - 1][1], p3[0] - points[i1 - 1][0])
    heading = math.atan2(p3[1] - p0[1], p3[0] - p0[0])
    arm = chord / (3 * math.cos((t0 - heading) / 2) ** 2)
    return (p0,
            (p0[0] + arm * math.cos(t0), p0[1] + arm * math.sin(t0)),
            (p3[0] - arm * math.cos(t1), p3[1] - arm * math.sin(t1)),
            p3)


def cubic_at(span, t):
    p0, c1, c2, p3 = span
    u = 1 - t
    return (u ** 3 * p0[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t ** 3 * p3[0],
            u ** 3 * p0[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t ** 3 * p3[1])


def offset_cubic(span, d):
    """The naive cubic offset: slide the four control points along their normals."""
    p0, c1, c2, p3 = span
    (x0, y0), (x3, y3) = p0, p3

    def normal(a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy) or 1.0
        return (-dy / length, dx / length)

    n0, n1 = normal(p0, c1), normal(c2, p3)
    return ((x0 + n0[0] * d, y0 + n0[1] * d),
            (c1[0] + n0[0] * d, c1[1] + n0[1] * d),
            (c2[0] + n1[0] * d, c2[1] + n1[1] * d),
            (x3 + n1[0] * d, y3 + n1[1] * d))


def seg_dist(p, a, b) -> float:
    ax, ay = a
    bx, by = b
    vx, vy = bx - ax, by - ay
    length = vx * vx + vy * vy
    t = 0.0 if length == 0 else max(0.0, min(1.0, ((p[0] - ax) * vx + (p[1] - ay) * vy) / length))
    return math.hypot(p[0] - (ax + t * vx), p[1] - (ay + t * vy))


def poly_dist(p, poly) -> float:
    return min(seg_dist(p, poly[i], poly[i + 1]) for i in range(len(poly) - 1))


# -- growth -----------------------------------------------------------------

def spine(top: int, triple=THIN, origin=(0.0, 0.0), heading: float = 0.0,
          scale: float = 1.0, side: int = 1):
    """A spine from a point, along a heading.  The first chord continues it."""
    alpha = triple_angle(triple) * side
    x, y = origin
    pts = [(x, y)]
    for i, k in enumerate(range(top, 0, -1)):
        chord = triple[2] * scale * 2.0 ** i
        for _ in range(k):
            x += chord * math.cos(heading)
            y += chord * math.sin(heading)
            pts.append((x, y))
            heading += alpha
    return pts, heading


def heading_at(points, i):
    """The outgoing chord at node i -- the direction a branch must leave on."""
    j = min(i, len(points) - 2)
    a, b = points[j], points[j + 1]
    return math.atan2(b[1] - a[1], b[0] - a[0])


def grow(points, top: int, triple, levels: int, rule: str = "one",
         scale: float = 0.34, side: int = 1, shrink: float = 0.032):
    """Branch at every node of a spine, and recurse.

    A child starts at the node's own chord size times `shrink`, so the join
    reads as a continuation rather than a hair.  `rule` picks the side:
    "one", "alternate", or "both".  `levels` counts the branch levels still to
    grow below this spine.
    """
    strokes = [(points, levels)]
    if levels <= 0:
        return strokes
    child_top = 4          # every branch is the same little spine
    for i in range(1, len(points) - 1):
        heading = heading_at(points, i)
        local = math.dist(points[i], points[i + 1])
        start = shrink * local / triple[2]
        sides = (side, -side) if rule == "both" else (
            (side * (-1) ** i if rule == "alternate" else side,))
        for s in sides:
            child, _ = spine(child_top, triple, points[i], heading, start, s)
            strokes.extend(grow(child, child_top, triple, levels - 1,
                                rule, scale * 0.62, s, shrink))
    return strokes


# -- drawing ----------------------------------------------------------------

def upright(points, root):
    """Turn the whole tree so the root spine runs vertically, growing up."""
    a = math.atan2(root[-1][1] - root[0][1], root[-1][0] - root[0][0])
    rot = math.pi / 2 - a
    c, s = math.cos(rot), math.sin(rot)
    return [(c * x - s * y, s * x + c * y) for x, y in points]


def tree_svg(strokes, w=760, h=760, flip: bool = False) -> str:
    """`flip` mirrors the whole tree left to right, so B keeps pointing up."""
    root = strokes[0][0]
    strokes = [(upright(pts, root), depth) for pts, depth in strokes]
    if flip:
        strokes = [([(-x, y) for x, y in pts], depth) for pts, depth in strokes]
    flat = [p for pts, _ in strokes for p in pts]
    draw, _ = fitter(flat, h, w, margin=18.0)
    parts = []
    for pts, depth in strokes:
        width = 2.4 if depth >= 1 else 0.9
        shade = INK if depth >= 1 else "#8a7444"
        parts.append(f'<path d="{path_d(draw(pts))}" fill="none" '
                     f'stroke="{shade}" stroke-width="{width:.1f}" '
                     f'stroke-linecap="round"/>')
    return f"""<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="{w}" height="{h}" fill="#fff"
          stroke="{LINE}" stroke-width="1"/>
    {''.join(parts)}
  </svg>"""


def offset_svg(points, offsets, w=760, h=760, crop=None) -> str:
    """The spine with parallel plates, every curve fitted to the same frame.

    `crop` keeps only the first n chords of every line -- the plates are the
    same construction, the window just moves to where they separate.
    """
    lines = []
    for d, shade, width, dash in offsets:
        line = offset_chain(points, d)
        lines.append((line[:crop + 1] if crop is not None else line,
                      shade, width, dash))
    frame = [p for line, _, _, _ in lines for p in line]
    draw, _ = fitter(frame, h, w, margin=18.0)
    parts = []
    for line, shade, width, dash in lines:
        parts.append(f'<path d="{path_d(draw(line))}" fill="none" stroke="{shade}" '
                     f'stroke-width="{width}" {dash}/>')
    return f"""<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="{w}" height="{h}" fill="#fff"
          stroke="{LINE}" stroke-width="1"/>
    {''.join(parts)}
  </svg>"""


def two_up(a: str, b: str) -> str:
    return f'<div class="two">{a}{b}</div>'


def pair(n: int, panels) -> str:
    """Two illustrations side by side: A, and B, the same tree turned over."""
    a, b, caption = panels
    return f"""<div class="strip"><div class="two">{a}{b}</div>
  <p><strong>Fig. {n}</strong> · {caption} · <strong>A</strong> as grown,
  <strong>B</strong> the same tree mirrored</p></div>"""


def strip(svg: str, caption: str, n: int) -> str:
    return f'<div class="strip">{svg}<p><strong>Fig. {n}</strong> · {caption}</p></div>'


# -- the page ---------------------------------------------------------------

def main() -> int:
    top = 9
    st = series_top(top)
    chain = doubling_chain(top)
    alpha = triple_angle(THIN)
    close = closing_distance(chain)
    chord_min = min(math.dist(chain[i], chain[i + 1]) for i in range(len(chain) - 1))

    # -- 1. the offsets --------------------------------------------------
    hook = 17                        # the two smallest stacks: where plates separate
    bands = [(-0.62 * close, GOLD, 1.1, ""),
             (-0.30 * close, "#a8894a", 1.1, ""),
             (0.0, INK, 2.4, ""),
             (0.30 * close, "#a8894a", 1.1, ""),
             (0.62 * close, GOLD, 1.1, "")]
    whole = offset_svg(chain, bands)
    zoom = offset_svg(chain, bands, crop=hook)

    rows = []
    for frac in (0.0, 0.15, 0.30, 0.45, 0.62):
        line = offset_chain(chain, frac * close)
        rows.append((frac, effective_b(line, THIN),
                     min(math.dist(line[i], line[i + 1])
                         for i in range(len(line) - 1))))
    table = "".join(
        f"<tr><td>{frac:.2f} × {close:.0f}</td><td>{b:.2f}</td>"
        f"<td>{shortest:.0f}</td></tr>" for frac, b, shortest in rows)

    # -- 2. cubics -------------------------------------------------------
    bounds, start = [0], 0
    for k in range(top, 0, -1):
        start += k
        bounds.append(start)
    spans = [arc_cubic(chain, bounds[i], bounds[i + 1])
             for i in range(len(bounds) - 1)]

    d = 0.30 * close
    exact = offset_chain(chain, d)                        # the plate, exactly
    proper = [arc_cubic(exact, bounds[i], bounds[i + 1])   # spans on the plate
              for i in range(len(bounds) - 1)]
    naive = [offset_cubic(s, d) for s in spans]           # control points moved

    worst, worst_at = 0.0, 0
    for i, span in enumerate(naive):
        base = [cubic_at(proper[i], j / 60) for j in range(61)]
        for j in range(41):
            gap = poly_dist(cubic_at(span, j / 40), base)
            if gap > worst:
                worst, worst_at = gap, i

    hook_spans = 2
    frame = [pt for s in spans[:hook_spans] + proper[:hook_spans]
             + naive[:hook_spans] for pt in s]
    draw, _ = fitter(frame, 760, 760, 18.0)

    def at(pt):
        q = draw([pt])[0]
        return f"{q[0]:.2f} {q[1]:.2f}"

    def cubic_d(span):
        return f"M {at(span[0])} C {at(span[1])} {at(span[2])} {at(span[3])}"

    def paths(span_set, shade, width, extra=""):
        return "".join(f'<path d="{cubic_d(s)}" fill="none" stroke="{shade}" '
                       f'stroke-width="{width}" {extra}/>'
                       for s in span_set[:hook_spans])

    cubic_panel = f"""<svg viewBox="0 0 760 760" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="760" height="760" fill="#fff"
          stroke="{LINE}" stroke-width="1"/>
    {paths(spans, INK, 2.4)}
    {paths(proper, "#6b5a38", 1.6)}
    {paths(naive, GOLD, 1.2, 'stroke-dasharray="6 5"')}
  </svg>"""

    # -- 3. the growth rules --------------------------------------------
    rules = (("both sides at every node", "both"),
             ("alternating sides", "alternate"),
             ("one side at every node", "one"))
    branch_top = 6                       # a shorter spine: the branches stay legible
    branch_chain = doubling_chain(branch_top)
    growth = []
    for label, rule in rules:
        tree = grow(branch_chain, branch_top, THIN, 1, rule)
        chords = sum(len(p) - 1 for p, _ in tree)
        growth.append((tree_svg(tree), tree_svg(tree, flip=True),
                       f"<strong>{label}</strong> · {len(tree)} plates · "
                       f"{chords} chords"))

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Clothoid intermediate curves stage II</title>
<style>{CSS}</style>
</head>
<body>
<main>
  <p class="back"><a href="curve-families.html">← the curves</a> ·
  <a href="sandbox.html">sandbox</a></p>
  <h1>Clothoid intermediate curves stage II</h1>
  <p class="lead">A spine is a chain of chords. Everything drawn from it — an
  offset, a branch — is a plate, and every plate is a construction on the
  spine, not a copy of it.</p>

  <h2>Offset parallel curves</h2>
  <div class="panel">
    <p>Slide every chord by some distance <code>d</code> along its normal, then
    re-intersect the neighbours. The node angles do not
    change — a spine turns by {math.degrees(alpha):.2f}° at every node, and so
    does every offset of it. What changes is the chord length: each end is
    trimmed by <code>d·tan(α/2)</code>, so a chord of length <code>c</code>
    becomes <code>c − 2d·tan(α/2)</code>.</p>
    <p>That subtraction is the whole story. It is a constant, not a ratio, so an
    offset is <em>not</em> a scaled copy of the spine: the short chords at the
    hook lose proportionally far more than the long ones at the arm, which means
    every offset has its own b. Push far enough and the innermost chord is eaten
    to nothing — at <code>d = c/(2·tan(α/2)) = {close:.0f}</code> the plate
    closes at a point. That number is the hook's own radius of curvature,
    <code>c/α = {chord_min / alpha:.0f}</code>: the plate closes when the offset
    reaches the centre it is turning about.</p>
    {two_up(
      strip(whole, f"<strong>the spine</strong> (ink) and four plates, at 0.30 "
                   f"and 0.62 of the closing distance, on both sides", 1),
      strip(zoom, f"<strong>the same plates, zoomed</strong> to the first "
                  f"{hook} chords: the distance that is a skin over the arm is "
                  f"a third of the radius at the hook, so they fan out", 2))}
    <div class="scroll"><table style="margin-top:10px">
      <tr><th>offset d</th><th>its own b</th><th>shortest chord</th></tr>
      {table}
    </table></div>
    <p style="margin-top:10px">The spine is b = {effective_b(chain, THIN):.2f}.
    Offsetting inward raises b and outward lowers it, which is why a plate
    family reads as one gesture at different tensions.</p>
  </div>

  <h2>Root and branch</h2>
  <div class="panel">
    <p>The root is a spine. A branch is another spine, scaled down and started
    at a node along that node's own tangent — which is the outgoing chord
    direction, so the join is G1 for free: there is no blend to compute and no
    corner to round. The child then turns by the same angle at every node, only
    faster, because its chords are shorter.</p>
    <p><em>Where</em> a branch may go is the <a
    href="branch-points.html">branch-points</a> question — clearance from the
    rest of the study. This is <em>how</em> it grows. Each panel is the
    {branch_top}-stack spine turned upright, branching at every node
    ({series_top(branch_top)["chords"]} chords,
    {series_top(branch_top)["turn"]:.0f}°).</p>
    {pair(3, growth[0])}
    {pair(4, growth[1])}
    {pair(5, growth[2])}
    <p style="margin-top:10px">Same spine, same child, three rules — and the
    difference between a fern and a fishbone is only whether the side flips.
    Depth is the next dial: each child is a spine too, so it branches as well.</p>
  </div>

  <h2>Where the cubics fit</h2>
  <div class="panel">
    <p>A span is a cubic through two nodes. The repo fits it with the parabola
    rule — arm <code>= chord / (3·cos²(δ/2))</code>, exact for a circular arc —
    and groups the chords so no span carries more than about 45°, which is how
    {len(spans)} cubics stand in for {len(chain) - 1} chords. Nodes are smoothed
    onto the bisector, so consecutive spans meet G1 and the chain stops reading
    as a polygon.</p>
    <p>But a cubic does not survive offsetting. The exact offset of a cubic is a
    degree-10 curve, not a cubic. The usual shortcut — slide the four control
    points along their normals — is an approximation: it lands
    {100 * worst / d:.0f}% of the offset distance away from a plate fitted
    properly, and that share does not shrink as the offset gets smaller. It is
    a shape error, not a rounding error.</p>
    {strip(cubic_panel, f"<strong>{len(spans)} spans</strong> on the spine (ink) · "
                        f"the plate at d = {d:.0f}, spans fitted to the offset spine "
                        f"(dark) · the same plate by moving the four control points "
                        f"(gold) · worst gap {100 * worst / d:.0f}% of the offset, "
                        f"on span {worst_at + 1} of {len(spans)}", 6)}
    <p style="margin-top:10px">So the order is fixed: <strong>offset the spine
    first</strong>, then fit spans to the plate that comes out. Offsetting the
    cubics and hoping is the one move this geometry punishes.</p>
    <p class="next">Next: leaves. A leaf is a plate that stops — one span at the
    end of a branch, sized by the chord that carries it.</p>
  </div>
</main>
</body>
</html>
"""
    path = ROOT / "docs" / "stage-two.html"
    path.write_text(page, encoding="utf-8")
    print(path)
    print(f"close={close:.0f} chord_min={chord_min:.0f} worst_cubic={worst:.0f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
