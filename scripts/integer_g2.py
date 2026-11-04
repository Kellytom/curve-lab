"""Build the integer G2 mirror-join probe page.

    .venv/bin/python scripts/integer_g2.py

The construction and its checks live in `curve_lab/pyth_g2.py`; this script
only renders the result and the ten-triple table.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab import pyth_cubic, pyth_g2  # noqa: E402

COLOURS = ("#3f7d4e", "#c9a441", "#1f5fa8")


def cubic(points, t):
    u = 1.0 - t
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = points
    return (u*u*u*x0 + 3*u*u*t*x1 + 3*u*t*t*x2 + t*t*t*x3,
            u*u*u*y0 + 3*u*u*t*y1 + 3*u*t*t*y2 + t*t*t*y3)


def g2_svg(chain_data, w=1000, h=560):
    pieces = chain_data["pieces"]
    coords = []
    for piece in pieces:
        coords.extend(piece)
    for piece in pieces:
        coords.extend(cubic(piece, i / 60) for i in range(61))
    x0, y0 = min(p[0] for p in coords), min(p[1] for p in coords)
    x1, y1 = max(p[0] for p in coords), max(p[1] for p in coords)
    dx, dy = x1 - x0 or 1, y1 - y0 or 1
    pad = .12
    xa, xb = x0 - pad*dx, x1 + pad*dx
    ya, yb = y0 - pad*dy, y1 + pad*dy
    k = min((w - 70)/(xb - xa), (h - 105)/(yb - ya))
    ox = (w - (xb - xa)*k)/2
    oy = 42 + (h - 82 - (yb - ya)*k)/2

    def put(p):
        return ox + (p[0] - xa)*k, h - (oy + (p[1] - ya)*k)

    body = []
    # integer grid, decimated for legibility
    step = 10
    for gx in range(int(xa)//step*step, int(xb)+step, step):
        a, b = put((gx, ya)), put((gx, yb))
        body.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#e4dcc6"/>')
    for gy in range(int(ya)//step*step, int(yb)+step, step):
        a, b = put((xa, gy)), put((xb, gy))
        body.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#e4dcc6"/>')
    for idx, (piece, colour) in enumerate(zip(pieces, COLOURS)):
        d = " ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}" for p in (cubic(piece, i/120) for i in range(121)))
        body.append(f'<path d="M {d}" fill="none" stroke="{colour}" stroke-width="2.6" stroke-linejoin="round"/>')
        d = " ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}" for p in piece)
        body.append(f'<path d="M {d}" fill="none" stroke="{colour}" stroke-width="1" stroke-dasharray="4 4" opacity=".8"/>')
        mid = cubic(piece, .5)
        q = put(mid)
        body.append(f'<text x="{q[0]:.1f}" y="{q[1]-9:.1f}" text-anchor="middle" font-family="Georgia,serif" font-size="14" font-weight="600" fill="{colour}">{"CAB"[idx]}</text>')
    for piece in pieces:
        for p in piece:
            q = put(p)
            body.append(f'<rect x="{q[0]-2.5:.1f}" y="{q[1]-2.5:.1f}" width="5" height="5" fill="#fbf7ec" stroke="#7b6c4e" stroke-width=".8"/>')
    for point in (pieces[0][3], pieces[1][3]):
        q = put(point)
        body.append(f'<circle cx="{q[0]:.1f}" cy="{q[1]:.1f}" r="4.5" fill="#2e2413" stroke="#fbf7ec" stroke-width="1"/>')
        body.append(f'<text x="{q[0]+8:.1f}" y="{q[1]-8:.1f}" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="#2e2413">G2 ({point[0]}, {point[1]})</text>')
    body.append(f'<text x="12" y="19" font-family="Georgia,serif" font-size="14" font-weight="600" fill="#2e2413">Fig. G1 · 3-4-5 G2 chain · scale 5</text>')
    body.append(f'<text x="12" y="34" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="#7b6c4e">C → A → B · joint tangents (15,−20) · curvature ±16/375 · both joins exact</text>')
    body.append(f'<text x="12" y="{h-36}" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="#7b6c4e">— C   — A   — B   ■ control   • G2 join</text>')
    body.append(f'<text x="12" y="{h-8}" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="#7b6c4e">x →</text>')
    body.append(f'<text x="{w-38}" y="{h-8}" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="#7b6c4e">y ↑</text>')
    return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">'
            f'<rect width="{w}" height="{h}" fill="#fbf7ec" stroke="#d8ccae"/>'
            + "".join(body) + "</svg>")



def pair_svg(pair, w=1000, h=470):
    """The asymmetric A→B pair, with the reflected B."""
    pieces = [pair["a_points"], pair["b_points"]]
    colours = ("#c9a441", "#1f5fa8")
    coords = []
    for piece in pieces:
        coords.extend(piece)
        coords.extend(cubic(piece, i / 80) for i in range(81))
    x0, y0 = min(p[0] for p in coords), min(p[1] for p in coords)
    x1, y1 = max(p[0] for p in coords), max(p[1] for p in coords)
    dx, dy = x1 - x0 or 1, y1 - y0 or 1
    pad = .12
    xa, xb = x0 - pad*dx, x1 + pad*dx
    ya, yb = y0 - pad*dy, y1 + pad*dy
    k = min((w - 70)/(xb - xa), (h - 105)/(yb - ya))
    ox = (w - (xb - xa)*k)/2
    oy = 42 + (h - 82 - (yb - ya)*k)/2

    def put(p):
        return ox + (p[0] - xa)*k, h - (oy + (p[1] - ya)*k)

    body = []
    for gx in range(int(xa)//10*10, int(xb)+10, 10):
        a, b = put((gx, ya)), put((gx, yb))
        body.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#e4dcc6"/>')
    for gy in range(int(ya)//10*10, int(yb)+10, 10):
        a, b = put((xa, gy)), put((xb, gy))
        body.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#e4dcc6"/>')
    for idx, (piece, colour) in enumerate(zip(pieces, colours)):
        d = " ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}" for p in (cubic(piece, i/120) for i in range(121)))
        body.append(f'<path d="M {d}" fill="none" stroke="{colour}" stroke-width="2.6" stroke-linejoin="round"/>')
        d = " ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}" for p in piece)
        body.append(f'<path d="M {d}" fill="none" stroke="{colour}" stroke-width="1" stroke-dasharray="4 4" opacity=".8"/>')
        q = put(cubic(piece, .5))
        body.append(f'<text x="{q[0]:.1f}" y="{q[1]-9:.1f}" text-anchor="middle" font-family="Georgia,serif" font-size="14" font-weight="600" fill="{colour}">{"AB"[idx]}</text>')
        for p in piece:
            q = put(p)
            body.append(f'<rect x="{q[0]-2.5:.1f}" y="{q[1]-2.5:.1f}" width="5" height="5" fill="#fbf7ec" stroke="#7b6c4e" stroke-width=".8"/>')
    q = put(pair["join"])
    body.append(f'<circle cx="{q[0]:.1f}" cy="{q[1]:.1f}" r="4.5" fill="#2e2413" stroke="#fbf7ec" stroke-width="1"/>')
    body.append(f'<text x="{q[0]+8:.1f}" y="{q[1]-8:.1f}" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="#2e2413">G2 (50, 0)</text>')
    body.append(f'<text x="12" y="19" font-family="Georgia,serif" font-size="14" font-weight="600" fill="#2e2413">Fig. G2 · asymmetric pair · scale 1</text>')
    body.append(f'<text x="12" y="34" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="#7b6c4e">arms 7-24-25 / 3-4-5 ↔ 3-4-5 / 7-24-25 · tangent (4,−3) · curvature −6/5</text>')
    body.append(f'<text x="12" y="{h-36}" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="#7b6c4e">— A   — reflected B   ■ control   • G2 join</text>')
    body.append(f'<text x="12" y="{h-8}" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="#7b6c4e">x →</text>')
    body.append(f'<text x="{w-38}" y="{h-8}" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="#7b6c4e">y ↑</text>')
    return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">'
            f'<rect width="{w}" height="{h}" fill="#fbf7ec" stroke="#d8ccae"/>'
            + "".join(body) + "</svg>")

def main():
    reports = pyth_g2.probe_all()
    base = pyth_g2.chain(pyth_cubic.case(3, 4, 5))
    asym = pyth_g2.asymmetric_pair()
    fallback = pyth_g2.g1_fallback()
    asym_svg = pair_svg(asym)
    rows = []
    for r in reports:
        j0, j1 = r["joins"]
        rows.append(
            f'<tr><td>{r["label"]}</td><td>{r["scale"]}</td>'
            f'<td>({j0["tangent"][0]}, {j0["tangent"][1]})</td>'
            f'<td>±{abs(j0["curvature_left"])}</td>'
            f'<td>{"yes" if r["g2"] else "no"}</td></tr>')
    page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Integer G2 probe</title>
<style>
:root{{--paper:#fbf7ec;--ink:#2e2413;--muted:#7b6c4e;--rule:#d8ccae;--gold:#c9a441}}
*{{box-sizing:border-box}}
body{{margin:0;background:#f3eddf;color:var(--ink);font:16px/1.55 Georgia,serif}}
main{{max-width:1280px;margin:0 auto;padding:34px 22px 70px}}
.eyebrow{{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}}
h1{{font-size:32px;line-height:1.1;margin:0 0 7px}}
h2{{font-size:21px;margin:0 0 9px}}
.lede{{max-width:900px;color:var(--muted);margin:0 0 20px}}
.panel{{background:var(--paper);border:1px solid var(--rule);padding:17px 19px;margin:0 0 18px}}
.formula{{font:12px/1.8 ui-monospace,Menlo,monospace;background:#f8f3e6;border-left:3px solid var(--gold);padding:10px 12px;margin:10px 0 12px;overflow-x:auto}}
table{{border-collapse:collapse;width:100%;font:10px/1.5 ui-monospace,Menlo,monospace;margin:10px 0}}
th,td{{border:1px solid var(--rule);padding:4px 6px;text-align:right}}
th{{color:var(--muted);font-weight:400}}
.small{{font:12px/1.55 ui-monospace,Menlo,monospace;color:var(--muted)}}
code{{font:12px ui-monospace,Menlo,monospace;background:#f4ecd7;padding:1px 4px}}
svg{{display:block;width:100%;height:auto}}
a{{color:#1f5fa8}}
</style>
</head>
<body>
<main>
<p class="eyebrow">curve-lab · exact G2 probe</p>
<h1>Integer G2 mirror chain</h1>
<p class="lede">The symmetric integer cubic has opposite endpoint curvatures. Reflecting it across an endpoint tangent gives a curve with the same tangent and curvature at the join. Scaling by the hypotenuse clears the reflection denominators. The result is an exact G2 chain with integer controls.</p>

<section class="panel">
  <h2>Fig. G1 · the 3-4-5 chain</h2>
  <p>The middle piece is the 3-4-5 base, scaled by 5. The pieces before and after are its mirrors at the start and end tangents. Both joins are C1 and G2; the outer ends are free.</p>
  <div class="figure">{g2_svg(base)}</div>
  <p class="small">Join data: tangent <code>(15,−20)</code>; curvature <code>+16/375</code> at the start join and <code>−16/375</code> at the end join. The signs differ because the chain has an inflection between the joins.</p>
</section>

<section class="panel">
  <h2>Fig. G2 · asymmetric pair · scale 1</h2>
  <p>This pair is genuinely asymmetric: A uses arms <code>7-24-25</code> then <code>3-4-5</code>; B uses the complementary arms. Reflect B across its start tangent, translate it to A's end, and the join has exactly matching tangent and curvature at <strong>scale 1</strong>.</p>
  <div class="figure">{asym_svg}</div>
  <p class="small">A ends at <code>(50,0)</code> with tangent <code>(4,−3)</code> and curvature <code>−6/5</code>. Reflected B starts there with the same tangent and curvature; all controls are integers.</p>
</section>

<section class="panel">
  <h2>Probe all ten triples</h2>
  <p>Result: <strong>{sum(r["g2"] for r in reports)}/{len(reports)}</strong> triples pass both joins. The construction works for every symmetric triple. The scale is the hypotenuse <code>c</code>; each pair of joins has exact tangent and curvature match.</p>
  <div class="table-wrap"><table>
    <tr><th>triple</th><th>scale</th><th>join tangent</th><th>curvature</th><th>G2 both joins?</th></tr>
    {''.join(rows)}
  </table></div>
</section>

<section class="panel">
  <h2>G1 fallback</h2>
  <p>If a curvature match is not available or not worth the scale, a G1 join is still useful glue. Take the 3-4-5 base and an unreflected copy of itself: the tangent at <code>(10,0)</code> is <code>(3,−4)</code> on both sides, but the curvatures are <code>−16/75</code> and <code>+16/75</code>. The join is G1, not G2. The shape is continuous; only the curvature jumps.</p>
</section>

<section class="panel">
  <h2>What this proves, and what it does not</h2>
  <p><strong>Proved:</strong> a three-piece integer-control chain with G2 at both interior joins exists for every symmetric triple in the catalogue. The mirror scale is the hypotenuse <code>c</code>, and the checks are exact rational equalities.</p>
  <p><strong>Not proved:</strong> that an arbitrary pair of integer cubics can be joined G2; that the chain is visually clear or free of self-intersection; or that the outer ends match a following piece. This probe uses mirrored copies of one symmetric family, which is a much narrower construction than the asymmetric-arm search.</p>
  <p class="small">The next probe should search asymmetric arm pairs and report the smallest integer scale that matches two chosen endpoint curvatures.</p>
</section>

<section class="panel">
  <h2>Re-run</h2>
  <div class="formula">.venv/bin/python scripts/integer_g2.py<br>.venv/bin/python -m unittest tests.test_pyth_g2</div>
</section>
</main>
</body>
</html>
'''
    out = ROOT / "workbench" / "integer-g2.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    print(f"  {sum(r['g2'] for r in reports)}/{len(reports)} triples pass both joins")


if __name__ == "__main__":
    main()
