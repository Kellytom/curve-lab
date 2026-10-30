"""Where can a branch go? The practical curve with candidate pins.

    .venv/bin/python scripts/branch_points.py
    open docs/branch-points.html

A branch is exact only at a pin: a point chosen on the exact chain that becomes
a hard split with the chain's heading. This page pins six candidate knots along
the right half, throws a straight probe branch out of each one, and reports how
close that probe comes to the rest of the study (half, mirror and band). The
open ones are drawn.

The practical curve is 34 cubics (36 with one pin) against 1,164 for the exact
chain, so the page also keeps the x-instead-of-y count in view.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clothoid_lab import practical, spine_study  # noqa: E402
from clothoid_lab.clearance import segment_distance  # noqa: E402
from clothoid_lab.grammar import STUDY_01, band, fleur_right  # noqa: E402
from clothoid_lab.model import Design, Segment  # noqa: E402
from clothoid_lab.piece import Piece, Trace, build_piece, render_piece  # noqa: E402

PAGE = (200.0, 250.0)
PROBE = 40.0
START = 5.0
CLEARANCE = 3.0
FRACTIONS = (0.12, 0.28, 0.42, 0.58, 0.72, 0.88)


def study_points():
    right = fleur_right(STUDY_01)
    ring = band(STUDY_01)
    half, _, _ = spine_study.composite(
        right["spans"], 0.5, start=right["start"], heading=right["angle"])
    rim, _, _ = spine_study.composite(
        ring["spans"], 0.5, start=ring["start"], heading=ring["angle"])
    half = [(float(x), float(y)) for x, y in half]
    rim = [(float(x), float(y)) for x, y in rim]
    mirror = [(-x, y) for x, y in half]
    return half, rim, mirror


def cumulative(points):
    out = [0.0]
    for a, b in zip(points, points[1:]):
        out.append(out[-1] + math.dist(a, b))
    return out


def distance_to(study, point):
    return min(segment_distance(point, point, a, b)[0]
               for track in study for a, b in zip(track, track[1:]))


def probe(origin, heading):
    x, y = origin
    points = [(x + t * math.cos(heading), y + t * math.sin(heading))
              for t in (START + i * 0.5 for i in range(int((PROBE - START) / 0.5) + 1))]
    return points


def branch_design(origin, heading):
    return Design(
        name="probe",
        segments=[Segment(kd=0.0, length=PROBE, kappa0=0.0)],
        anchor={"x": origin[0], "y": origin[1], "angle": heading},
    )


def main() -> int:
    exact = spine_study.study_01_from_chains(0.5)
    exact_cubics = sum(len(g.spans) for g in build_piece(exact, tol=0.02)[0]
                       if g.role == "spine")
    practical_piece, practical_report = practical.practical_study_01()
    practical_groups, _ = build_piece(practical_piece, tol=0.1)
    practical_cubics = sum(len(g.spans) for g in practical_groups
                           if g.role == "spine")

    half, rim, mirror = study_points()
    study = [half, rim, mirror]
    lengths = cumulative(half)
    total = lengths[-1]

    candidates = []
    for number, fraction in enumerate(FRACTIONS, start=1):
        want = total * fraction
        index = min(range(len(lengths)), key=lambda i: abs(lengths[i] - want))
        origin = half[index]
        outgoing = half[min(index + 1, len(half) - 1)]
        heading = math.atan2(outgoing[1] - origin[1],
                             outgoing[0] - origin[0])
        probes = []
        for side, turn in (("left", math.pi / 2), ("right", -math.pi / 2)):
            points = probe(origin, heading + turn)
            clearance = min(distance_to(study, p) for p in points)
            probes.append((side, heading + turn, clearance))
        side, branch_heading, clearance = max(probes, key=lambda item: item[2])
        candidates.append({
            "number": number, "fraction": fraction, "point": origin,
            "heading": heading, "side": side, "branch_heading": branch_heading,
            "clearance": clearance, "open": clearance >= CLEARANCE,
        })

    # the map: exact knots, practical cubic ends, then numbered candidates
    exact_dots = []
    seen = set()
    for x, y in half + [(-x, y) for x, y in half]:
        key = (round(x, 5), round(y, 5))
        if key not in seen:
            seen.add(key)
            exact_dots.append((x, y))
    practical_dots = []
    seen = set()
    for group in practical_groups:
        if group.role != "spine":
            continue
        for span in group.spans:
            x, y = span["p0"]
            key = (round(x, 5), round(y, 5))
            if key not in seen:
                seen.add(key)
                practical_dots.append((x, y))

    annotations = [
        {"kind": "circle", "x": x, "y": y, "r": 0.55, "fill": "#bfae8c"}
        for x, y in exact_dots
    ]
    annotations.extend(
        {"kind": "circle", "x": x, "y": y, "r": 1.5, "fill": "#8c6a21"}
        for x, y in practical_dots
    )
    for item in candidates:
        annotations.append({"kind": "circle", "x": item["point"][0],
                            "y": item["point"][1], "r": 2.7,
                            "fill": "#2e2413" if item["open"] else "#b04a3a"})
        annotations.append({"kind": "text", "x": item["point"][0],
                            "y": item["point"][1], "dx": 3.0, "dy": -3.0,
                            "text": str(item["number"]), "size": 4.0,
                            "fill": "#7b6c4e"})
    map_svg, _ = render_piece(practical_piece, tol=0.1, frame=PAGE,
                              margin=12, annotations=annotations)

    # three open candidates, each drawn with its branch
    panels = []
    for item in [c for c in candidates if c["open"]][:3]:
        piece, _ = practical.practical_study_01(0.5, pins=[item["point"]])
        piece.traces.append(Trace(
            f"branch {item['number']}",
            branch_design(item["point"], item["branch_heading"]),
            mirror=False))
        px, py = item["point"]
        hx = px + PROBE * math.cos(item["branch_heading"])
        hy = py + PROBE * math.sin(item["branch_heading"])
        marks = [
            {"kind": "line", "x1": px, "y1": py, "x2": hx, "y2": hy,
             "stroke": "#8c6a21", "width": 1.4, "front": True},
            {"kind": "circle", "x": px, "y": py, "r": 2.4,
             "fill": "#8c6a21", "front": True},
        ]
        svg, _ = render_piece(piece, tol=0.1, frame=PAGE, margin=12,
                              annotations=marks)
        panels.append((item, svg))

    rows = "\n".join(
        f"<tr><td>{c['number']}</td>"
        f"<td>{c['fraction']:.0%}</td>"
        f"<td>({c['point'][0]:.1f}, {c['point'][1]:.1f})</td>"
        f"<td>{math.degrees(c['heading']):.1f}°</td>"
        f"<td>{c['side']}</td>"
        f"<td>{c['clearance']:.1f}</td>"
        f"<td>{'open' if c['open'] else 'blocked'}</td></tr>"
        for c in candidates)

    panel_html = "\n".join(
        f'<div class="cell"><div class="art">{svg}</div>'
        f'<p><strong>Branch {item["number"]}</strong> at '
        f'{item["fraction"]:.0%} of the chain, {item["side"]}, '
        f'{item["clearance"]:.1f} units clear.</p></div>'
        for item, svg in panels)

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Where to branch — the practical curve</title>
<style>
  :root {{ color-scheme: light; --paper:#f6f1e4; --card:#fffdf7; --ink:#2e2413;
    --muted:#7b6c4e; --gold:#8c6a21; --line:#d8ccae; --red:#b04a3a;
    --mono: ui-monospace,"SF Mono",Menlo,Consolas,monospace;
    --serif:"EB Garamond",Georgia,"Palatino Linotype",Palatino,serif; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; color:var(--ink); font:16px/1.55 var(--serif);
    background: radial-gradient(900px 440px at 12% -8%, #fcf9ef 0, transparent 60%), var(--paper); }}
  main {{ max-width: 900px; margin: 0 auto; padding: 34px 22px 70px; }}
  h1 {{ font-size: 28px; margin: 0 0 4px; }}
  .lead {{ color: var(--gold); margin: 0 0 18px; }}
  h2 {{ font: 600 11px/1.2 var(--mono); letter-spacing:.12em; text-transform:uppercase;
    color:var(--muted); margin:26px 0 8px; }}
  .panel {{ background:var(--card); border:1px solid var(--line); border-radius:6px; padding:14px; }}
  .art svg {{ display:block; width:100%; height:auto; background:#fff; }}
  .cells {{ display:grid; grid-template-columns:repeat(3,1fr); gap:10px; }}
  .cell {{ border:1px solid var(--line); border-radius:4px; padding:8px; background:#fff; }}
  .cell p {{ margin:6px 0 0; font:10px/1.4 var(--mono); color:var(--muted); }}
  table {{ border-collapse:collapse; width:100%; font:12px/1.5 var(--mono); }}
  th, td {{ border-bottom:1px solid var(--line); padding:6px 4px; text-align:left; }}
  th {{ color:var(--muted); font-weight:500; }}
  .scroll {{ overflow-x:auto; }}
  .stats {{ display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin-bottom:10px; }}
  .stat {{ border:1px solid var(--line); border-radius:4px; padding:10px; background:#fbf8ee; }}
  .stat strong {{ display:block; font:600 22px/1.1 var(--serif); }}
  .stat span {{ font:10px/1.4 var(--mono); color:var(--muted); }}
  .legend {{ font:10px var(--mono); color:var(--muted); display:flex; align-items:center; gap:6px; }}
  .dot {{ width:8px; height:8px; border-radius:50%; display:inline-block; margin-left:8px; }}
  .dot.exact {{ background:#cfc3a8; }}
  .dot.practical {{ background:#8c6a21; }}
  .dot.candidate {{ background:#2e2413; border:1px solid #b04a3a; }}
  .back {{ font:12px var(--mono); margin-bottom:16px; }}
  a {{ color:var(--gold); }}
  @media (max-width:620px) {{
    main {{ padding:22px 14px 60px; }}
    .cells, .stats {{ grid-template-columns:1fr; }}
    table {{ font-size:10px; }} th,td {{ padding:4px 2px; }}
  }}
</style>
</head>
<body>
<main>
  <p class="back"><a href="sandbox.html">← sandbox</a> ·
    <a href="practical-curve.html">the practical curve</a></p>
  <h1>Where to branch</h1>
  <p class="lead">The practical curve is {practical_cubics} cubics instead of {exact_cubics}.
    A branch is exact only at a pin.</p>

  <div class="stats">
    <div class="stat"><strong>{practical_cubics}</strong><span>cubics, practical, with mirror</span></div>
    <div class="stat"><strong>{exact_cubics}</strong><span>cubics, exact chain</span></div>
    <div class="stat"><strong>{sum(1 for c in candidates if c["open"])}/{len(candidates)}</strong><span>probe branches clear of the study</span></div>
  </div>

  <h2>The candidates</h2>
  <div class="panel">
    <p class="legend"><span class="dot exact"></span> exact chain knots
      <span class="dot practical"></span> practical cubic ends
      <span class="dot candidate"></span> candidate pin (dark open, red blocked)</p>
    <p>Six knots along the right half, chosen evenly by arc length. The colour is
    the verdict: gold is open, red is blocked. The number is the table row.
    <strong>Pale dots</strong> are the exact chain knots (0.5° step);
    <strong>gold dots</strong> are the practical cubic ends.</p>
    <div class="art">{map_svg}</div>
  </div>

  <h2>The numbers</h2>
  <div class="panel">
    <p>Each probe leaves the pin at 90° to the chain, on whichever side has more
    room, and runs {PROBE:.0f} units. “Clearance” is the distance from the probe
    (after the first {START:.0f} units, so the pin itself does not count) to the
    nearest ink in the half, its mirror or the band. Open means at least
    {CLEARANCE:.0f} units.</p>
    <div class="scroll"><table>
      <tr><th>#</th><th>along</th><th>pin</th><th>chain heading</th>
          <th>side</th><th>clearance</th><th>verdict</th></tr>
      {rows}
    </table></div>
  </div>

  <h2>Three branches, drawn</h2>
  <div class="panel">
    <div class="cells">{panel_html}</div>
    <p style="margin-top:10px">Each is the practical curve re-fitted with that one
    pin. Pinning costs one or two cubics; the pin is the gold dot, and the branch
    leaves on the chain's exact heading. A red candidate can still be used with a
    different branch angle or a shorter reach — the probe is a conservative test,
    not a prohibition.</p>
  </div>

  <h2>How to use it</h2>
  <div class="panel">
    <p>Choose the point on the <a href="spine-study-01.html">exact curve</a>, pin it,
    then generate the practical curve and attach the branch. The pin is a hard split
    with the chain's heading (pin error about 2e-7 units), so the junction is exact
    even though the rest of the curve is a 34-cubic approximation. If a probe is
    blocked, move along the chain until the dot turns gold; the table is the quick
    way to see whether the blockage is the mirror, the band, or another winding.</p>
  </div>
</main>
</body>
</html>
"""
    path = ROOT / "docs" / "branch-points.html"
    path.write_text(page, encoding="utf-8")
    print(path)
    print(f"exact {exact_cubics}, practical {practical_cubics}, "
          f"open {sum(1 for c in candidates if c['open'])}/{len(candidates)}")
    for c in candidates:
        print(f"  {c['number']} {c['fraction']:.0%} {c['side']} "
              f"clearance {c['clearance']:.1f} {'open' if c['open'] else 'blocked'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
