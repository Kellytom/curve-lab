"""Build the practical-curve page: exact study vs the small-SVG profile.

    .venv/bin/python scripts/practical_curve.py
    open docs/practical-curve.html

Both drawings are the same study. The exact one keeps one cubic per chain
chord; the practical one fits one clothoid per structural run and emits about
32 cubics. The page prints what each costs and measures the practical curve
against the exact one.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clothoid_lab import practical, spine_study  # noqa: E402
from clothoid_lab.grammar import STUDY_01, fleur_right  # noqa: E402
from clothoid_lab.piece import build_piece, render_piece  # noqa: E402

PAGE = (200.0, 250.0)

FONTS = [
    ("Times New Roman", 21, 55, 45, 14),
    ("Baskerville", 19, 46, 42, 12),
    ("Didot", 38, 82, 70, 24),
    ("Bodoni 72", 34, 51, 47, 10),
    ("Big Caslon", 42, 68, 94, 12),
    ("Charter", 18, 56, 32, 16),
    ("Hoefler Text", 23, 49, 48, 14),
    ("Iowan Old Style", 20, 56, 48, 16),
    ("New York", 28, 71, 47, 18),
    ("PT Serif", 32, 69, 64, 16),
]


def count_cubics(piece, tol):
    groups, info = build_piece(piece, tol=tol)
    return sum(len(g.spans) for g in groups if g.role == "spine"), info["fit_ok"]


def main() -> int:
    exact = spine_study.study_01_from_chains(0.5)
    exact_segments = sum(len(t.design.segments) for t in exact.traces)
    practical_piece, report = practical.practical_study_01()

    # A branch point is chosen on the exact chain, then pinned. Take a knot in
    # the middle of the long petal run.
    right = fleur_right(STUDY_01)
    points, ends, _ = spine_study.composite(
        right["spans"], 0.5, start=right["start"], heading=right["angle"])
    knot = (ends[1] + ends[2]) // 2
    pin = (float(points[knot][0]), float(points[knot][1]))
    pinned_piece, pinned = practical.practical_study_01(0.5, pins=[pin])

    exact_cubics, exact_ok = count_cubics(exact, 0.02)
    practical_cubics, practical_ok = count_cubics(pinned_piece, 0.1)
    if not (exact_ok and practical_ok):
        raise SystemExit("a trace did not fit")

    annotations = [{"kind": "circle", "x": pin[0], "y": pin[1], "r": 2.2,
                    "fill": "#8c6a21"}]
    svg, info = render_piece(pinned_piece, tol=0.1, frame=PAGE, margin=12,
                             annotations=annotations)
    exact_svg, _ = render_piece(exact, tol=0.02, frame=PAGE, margin=12)

    def row(label, tol, segments, cubics, error, text, piece=None):
        if piece is not None:
            rendered, _ = render_piece(piece, tol=0.1, frame=PAGE, margin=12)
            text = f"{len(rendered) // 1024} KB"
        return (f"<tr><td>{label}</td><td>{tol:g}</td><td>{segments}</td>"
                f"<td>{cubics}</td><td>{text}</td><td>{error}</td></tr>")

    profile_rows = row("exact", 0.02, exact_segments, exact_cubics,
                       "reference", f"{len(exact_svg) // 1024} KB")
    profile_rows += row("practical (no pin)", 0.5, report["segments"],
                        count_cubics(practical_piece, 0.1)[0],
                        f"{report['deviation']:.2f} mm", "", practical_piece)
    profile_rows += row("practical (one pin)", 0.5, pinned["segments"],
                        practical_cubics, f"{pinned['deviation']:.2f} mm", "",
                        pinned_piece)
    for tol in (0.25, 1.0):
        piece, variant = practical.practical_study_01(tol)
        cubics, _ = count_cubics(piece, 0.1)
        profile_rows += row("practical", tol, variant["segments"], cubics,
                            f"{variant['deviation']:.2f} mm", "", piece)

    font_rows = "\n".join(
        f"<tr><td>{name}</td><td>{c}</td><td>{at}</td><td>{amp}</td><td>{tilde}</td></tr>"
        for name, c, at, amp, tilde in FONTS)

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The practical curve — same study, a smaller SVG</title>
<style>
  :root {{ color-scheme: light; --paper:#f6f1e4; --card:#fffdf7; --ink:#2e2413;
    --muted:#7b6c4e; --gold:#8c6a21; --line:#d8ccae;
    --mono: ui-monospace,"SF Mono",Menlo,Consolas,monospace;
    --serif:"EB Garamond",Georgia,"Palatino Linotype",Palatino,serif; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; color:var(--ink); font:16px/1.55 var(--serif);
    background: radial-gradient(900px 440px at 12% -8%, #fcf9ef 0, transparent 60%), var(--paper); }}
  main {{ max-width: 900px; margin: 0 auto; padding: 34px 22px 70px; }}
  h1 {{ font-size: 28px; margin: 0 0 4px; }}
  .lead {{ color: var(--gold); margin: 0 0 18px; }}
  h2 {{ font: 600 11px/1.2 var(--mono); letter-spacing: .12em; text-transform: uppercase;
    color: var(--muted); margin: 26px 0 8px; }}
  .panel {{ background: var(--card); border: 1px solid var(--line); border-radius: 6px; padding: 14px; }}
  .art svg {{ display: block; width: 100%; height: auto; background: #fff; }}
  table {{ border-collapse: collapse; width: 100%; font: 12px/1.5 var(--mono); }}
  th, td {{ border-bottom: 1px solid var(--line); padding: 6px 4px; text-align: left; }}
  th {{ color: var(--muted); font-weight: 500; }}
  code {{ font: 12px/1 var(--mono); background: #fbf8ee; border: 1px solid var(--line);
    border-radius: 3px; padding: 2px 4px; }}
  .scroll {{ overflow-x: auto; }}
  .back {{ font: 12px var(--mono); margin-bottom: 16px; }}
  a {{ color: var(--gold); }}
  @media (max-width: 620px) {{
    main {{ padding: 22px 14px 60px; }}
    table {{ font-size: 10px; }}
    th, td {{ padding: 4px 2px; }}
  }}
</style>
</head>
<body>
<main>
  <p class="back"><a href="sandbox.html">← sandbox</a> · <a href="ornament-board.html">the ornament board</a></p>
  <h1>The practical curve</h1>
  <p class="lead">The same study, fitted for a small SVG: {practical_cubics} cubics instead of {exact_cubics}.</p>

  <h2>The drawing</h2>
  <div class="panel art">
    {svg}
  </div>

  <h2>What each profile costs</h2>
  <div class="panel">
    <div class="scroll"><table>
      <tr><th>profile</th><th>tolerance</th><th>design segments</th>
          <th>cubics with mirror</th><th>SVG</th><th>worst deviation</th></tr>
      {profile_rows}
    </table></div>
    <p style="margin-top:10px">The exact profile is the chain itself: one straight
    design segment per chord, one cubic per segment. The practical profile fits
    one clothoid through each structural run (the parts between the study's
    corners) and subdivides a run only when the measured error exceeds the
    tolerance. The drawing above has one pin — the gold dot — chosen on the
    exact chain as a branch point; it is a hard split with the exact heading, and
    the rest of the curve is re-fitted around it. Measured deviation
    {pinned['deviation']:.2f} mm.</p>
  </div>

  <h2>How big is that in type terms</h2>
  <div class="panel">
    <p>A capital C in a serif face is not two or three cubics; that is a
    geometric ring, not a letter. These are the native segment counts from ten
    installed serif faces. TrueType stores quadratics, and one cubic reproduces
    a quadratic exactly by degree elevation, so the count is the cubic
    equivalent.</p>
    <div class="scroll"><table>
      <tr><th>serif face</th><th>C</th><th>@</th><th>&amp;</th><th>~</th></tr>
      {font_rows}
    </table></div>
    <p style="margin-top:10px">So one letter C is 18–42 cubics, and <code>@</code>
    is 46–82 and <code>&amp;</code> is 32–94. The practical half at 14 clothoids is in
    the range of one serif C. The exact half, at 221, is past a whole glyph —
    and the band, at 722, is past an <code>@</code> several times over.</p>
  </div>

  <h2>Why the exact count was even higher</h2>
  <div class="panel">
    <p>The first measurement at a 1 degree step gave 1,078 cubics with 351 in
    the half. Some of that was a real bug: at a segment boundary the backend reports the
    <em>next</em> segment's tangent, so a corner was corrupting the end of the
    previous cubic and the fitter kept splitting to hide it. Reading the tangent
    just inside the segment fixed it: one straight segment now takes one cubic,
    not nine. The exact profile still uses one segment per chord by design; the
    practical profile exists to avoid paying for that.</p>
  </div>
</main>
</body>
</html>
"""
    path = ROOT / "docs" / "practical-curve.html"
    path.write_text(page, encoding="utf-8")
    print(path)
    print(f"exact {exact_cubics} cubics, practical {practical_cubics} cubics, "
          f"deviation {report['deviation']:.2f} mm, {len(svg) // 1024} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
