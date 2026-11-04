"""The integer cubic Bézier family from Pythagorean triples.

    .venv/bin/python scripts/integer_cubic.py

Writes `workbench/integer-cubic.html`. The construction is exact: no fitting
and no approximation.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab import pyth_cubic  # noqa: E402

PYTH_3125 = (0.0, 4.34948822922, 16.260204708312, 20.609692937532,
             32.520409416624, 36.869897645844, 53.130102354156,
             57.479590583376, 69.390307062468, 73.739795291688,
             85.65051177078, 90.0)



def grid_svg(w: int = 1000, h: int = 430):
    """The quarter-turn integer cubic with its 61 points at t=k/60."""
    P = ((0.0, 0.0), (4.0, -3.0), (7.0, -4.0), (10.0, 0.0))
    Q = 60

    def at(t):
        u = 1.0 - t
        return (u*u*u*P[0][0] + 3*u*u*t*P[1][0] + 3*u*t*t*P[2][0] + t*t*t*P[3][0],
                u*u*u*P[0][1] + 3*u*u*t*P[1][1] + 3*u*t*t*P[2][1] + t*t*t*P[3][1])

    curve = [at(i / 240) for i in range(241)]
    dots = [at(k / Q) for k in range(Q + 1)]
    pts = curve + list(P)
    x0, y0 = min(p[0] for p in pts), min(p[1] for p in pts)
    x1, y1 = max(p[0] for p in pts), max(p[1] for p in pts)
    dx, dy = (x1 - x0) or 1, (y1 - y0) or 1
    pad = .10
    xa, xb = x0 - pad*dx, x1 + pad*dx
    ya, yb = y0 - pad*dy, y1 + pad*dy
    k = min((w - 54)/(xb - xa), (h - 90)/(yb - ya))
    ox = (w - (xb - xa)*k)/2
    oy = 34 + (h - 64 - (yb - ya)*k)/2

    def put(p):
        return ox + (p[0] - xa)*k, h - (oy + (p[1] - ya)*k)

    body = []
    for gx in range(0, 11):
        a, b = put((gx, ya)), put((gx, yb))
        body.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#e4dcc6"/>')
    for gy in range(-4, 1):
        a, b = put((xa, gy)), put((xb, gy))
        body.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#e4dcc6"/>')
    d = " ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}" for p in curve)
    body.append(f'<path d="M {d}" fill="none" stroke="#2e2413" stroke-width="2.4" stroke-linejoin="round"/>')
    d = " ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}" for p in P)
    body.append(f'<path d="M {d}" fill="none" stroke="#7b6c4e" stroke-width="1" stroke-dasharray="4 4"/>')
    for p in dots:
        q = put(p)
        body.append(f'<circle cx="{q[0]:.1f}" cy="{q[1]:.1f}" r="2.2" fill="#c9a441" stroke="#fbf7ec" stroke-width=".5"/>')
    for name, p in zip(("P0", "P1", "P2", "P3"), P):
        q = put(p)
        body.append(f'<rect x="{q[0]-3:.1f}" y="{q[1]-3:.1f}" width="6" height="6" fill="#fbf7ec" stroke="#2e2413" stroke-width="1"/>')
        body.append(f'<text x="{q[0]+6:.1f}" y="{q[1]-6:.1f}" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="#2e2413">{name} ({p[0]:.0f}, {p[1]:.0f})</text>')
    body.append(f'<text x="12" y="19" font-family="Georgia,serif" font-size="14" font-weight="600" fill="#2e2413">Fig. P2 · quarter-turn · 61 points at t=k/60</text>')
    body.append(f'<text x="12" y="34" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="#7b6c4e">slopes −3/4 → 4/3 · scale by 60³ = 216000</text>')
    body.append(f'<text x="12" y="{h-24}" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="#7b6c4e">— cubic   • t=k/60, integer after ×60³</text>')
    body.append(f'<text x="12" y="{h-8}" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="#7b6c4e">x →</text>')
    body.append(f'<text x="{w-38}" y="{h-8}" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="#7b6c4e">y ↑</text>')
    return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">'
            f'<rect width="{w}" height="{h}" fill="#fbf7ec" stroke="#d8ccae"/>'
            + "".join(body) + "</svg>")

def main():
    cases = pyth_cubic.cases()
    grid_svg_markup = grid_svg()
    data = json.dumps(cases, separators=(",", ":"))
    buttons = "".join(
        f'<button type="button" data-index="{i}">{c["label"]}</button>'
        for i, c in enumerate(cases))
    rows = "".join(
        f'<tr><td>{c["label"]}</td><td>{c["angle"]:.2f}°</td>'
        f'<td>{c["chord"]}</td><td>{c["arm"]}</td>'
        f'<td>({c["p1"][0]}, {c["p1"][1]})</td>'
        f'<td>({c["p2"][0]}, {c["p2"][1]})</td></tr>'
        for c in cases)
    angles = ", ".join(f"{a:.2f}°" for a in PYTH_3125)

    page = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Integer cubic Béziers</title>
<style>
:root{--paper:#fbf7ec;--ink:#2e2413;--muted:#7b6c4e;--rule:#d8ccae;--gold:#c9a441}
*{box-sizing:border-box}
body{margin:0;background:#f3eddf;color:var(--ink);font:16px/1.55 Georgia,serif}
main{max-width:1280px;margin:0 auto;padding:34px 22px 70px}
.eyebrow{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}
h1{font-size:32px;line-height:1.1;margin:0 0 7px}
h2{font-size:21px;margin:0 0 9px}
.lede{max-width:900px;color:var(--muted);margin:0 0 20px}
.panel{background:var(--paper);border:1px solid var(--rule);padding:17px 19px;margin:0 0 18px}
.formula{font:12px/1.8 ui-monospace,Menlo,monospace;background:#f8f3e6;border-left:3px solid var(--gold);padding:10px 12px;margin:10px 0 12px;overflow-x:auto}
.buttons{display:flex;flex-wrap:wrap;gap:6px;margin:9px 0 11px}
.buttons button{font:10px ui-monospace,Menlo,monospace;border:1px solid var(--rule);background:var(--paper);color:var(--ink);padding:4px 8px;cursor:pointer}
.buttons button:hover{background:#f4ecd7}
canvas{display:block;width:100%;height:auto;background:var(--paper);border:1px solid var(--rule)}
table{border-collapse:collapse;width:100%;font:10px/1.5 ui-monospace,Menlo,monospace;margin:10px 0}
th,td{border:1px solid var(--rule);padding:4px 6px;text-align:right}
th{color:var(--muted);font-weight:400}
.meta{font:11px/1.6 ui-monospace,Menlo,monospace;color:var(--muted);margin:9px 0 0}
.small{font:11px/1.55 ui-monospace,Menlo,monospace;color:var(--muted)}
code{font:12px ui-monospace,Menlo,monospace;background:#f4ecd7;padding:1px 4px}
</style>
</head>
<body>
<main>
<p class="eyebrow">curve-lab · exact integer construction</p>
<h1>Integer cubic Béziers</h1>
<p class="lede">A Pythagorean triple gives a cubic Bézier with every control point an integer, a rational tangent, and a chord twice its hypotenuse. The 3-4-5 case is the base; every other triple is the same construction.</p>

<section class="panel">
  <h2>Fig. P1 · the family</h2>
  <p>For any positive integer triple <code>a² + b² = c²</code>:</p>
  <div class="formula">P0 = (0, 0)<br>P1 = (a, −b)<br>P2 = (2c − a, b)<br>P3 = (2c, 0)</div>
  <p>The chord is <code>2c</code>. Both handle arms have length <code>c</code>. Both endpoints have tangent angle <code>−atan2(b,a)</code>. The construction is exact; nothing is fitted.</p>
  <div class="buttons" id="tri-buttons">__BUTTONS__</div>
  <canvas id="tri-canvas" width="1000" height="420" aria-label="Integer cubic Bézier selected from a Pythagorean triple"></canvas>
  <p class="meta" id="tri-meta"></p>
  <table><tr><th>triple</th><th>tangent</th><th>chord</th><th>arm</th><th>P1</th><th>P2</th></tr>__ROWS__</table>
</section>

<section class="panel">
  <h2>The 3-4-5 base</h2>
  <p><code>(a,b,c)=(3,4,5)</code> gives</p>
  <div class="formula">P0=(0,0), P1=(3,−4), P2=(7,4), P3=(10,0)</div>
  <p>chord 10, both arms 5, both tangents −53.13°. The control polygon is two congruent 3-4-5 triangles against the chord.</p>
</section>

<section class="panel">
  <h2>Rotations stay integer when the angle is Pythagorean</h2>
  <p>Rotate the 3-4-5 base by 53.13° (cos=3/5, sin=4/5) and scale by 5:</p>
  <div class="formula">P0=(0,0), P1=(25,0), P2=(5,40), P3=(30,40)</div>
  <p>Rotate by 36.87° (cos=4/5, sin=3/5) and scale by 5:</p>
  <div class="formula">P0=(0,0), P1=(24,−7), P2=(16,37), P3=(40,30)</div>
  <p>The angle between each arm and its chord remains 53.13°. An arbitrary rotation usually makes the coordinates irrational; a Pythagorean rotation makes them rational, and the denominator scale clears them.</p>
</section>


<section class="panel">
  <h2>What this means for the curve system</h2>
  <p>This is an exact integer-control spine, not a promise that every later operation stays integer. The useful question is which operations follow from the construction and which need their own test.</p>
  <div class="table-wrap"><table>
    <tr><th>operation</th><th>status</th><th>why</th></tr>
    <tr><td>integer controls</td><td>yes</td><td>the four points are built from integers</td></tr>
    <tr><td>point at rational <code>t=p/q</code></td><td>rational, then integer after scaling</td><td>de Casteljau denominators divide q³</td></tr>
    <tr><td>split at rational <code>t</code></td><td>rational, then integer after scaling</td><td>the sub-curve has the same denominator</td></tr>
    <tr><td>exact offset</td><td>no, not automatically</td><td>the normal needs a square root; the base curve is not PH</td></tr>
    <tr><td>G2 join</td><td>possible, needs solving</td><td>tangent and curvature are rational; asymmetric arms give more freedom</td></tr>
    <tr><td>arc length</td><td>no</td><td>a cubic arc length is generally not rational</td></tr>
  </table></div>

  <h3>Points along the curve</h3>
  <p>Choose a rational parameter <code>t=p/q</code>. The de Casteljau construction gives rational control points with denominators dividing <code>q³</code>. Multiply the whole cubic by <code>q³</code> and every control point, the split point, and both sub-curves become integer. For a finite set of fractions, use a common denominator <code>Q</code> and scale by <code>Q³</code>.</p>
  <p>For the 3-4-5 base at <code>t=1/3</code>, scale by 27. The first sub-curve is</p>
  <div class="formula">P0=(0,0), P1=(27,−36), P2=(57,−36), P3=(88,−24)</div>
  <p>and the split point is <code>(88,−24)</code>. The shape is unchanged; the lattice is simply finer. The parameter is a fraction of the curve’s parameter, not a distance along it, and the required scale can grow quickly.</p>

  <h3>Offsets are a separate promise</h3>
  <p>Integer controls do not make an offset curve integer. An offset point needs the unit normal, which involves a square root. The normal is rational at special points such as endpoints with Pythagorean tangents, but not at a generic point. The offset of a general cubic is not another cubic, and the 3-4-5 base is not a Pythagorean-hodograph cubic, so its exact offset is not rational in general.</p>
  <p>Treat offsets as a fitted or numeric layer. Exact rails remain lines, arcs and PH curves; this family gives a clean spine to offset from, not an exact offset family.</p>

  <h3>G2 joins, symmetric and asymmetric</h3>
  <p>G2 needs both the tangent direction and the curvature to match. For an integer cubic, endpoint curvature is rational, so this becomes a rational algebra problem rather than a numerical fitting problem.</p>
  <p>The symmetric family is a single shape parameter per triple: both arms have the same length, and the two endpoint curvatures have the same magnitude and opposite signs. That is elegant, but it is rigid at a join: matching one end fixes the curvature scale for the other.</p>
  <p>An asymmetric version removes that constraint. Take</p>
  <div class="formula">P0=(0,0), P1=(a0,−b0), P2=(L−a1,b1), P3=(L,0)</div>
  <p>with integer chord <code>L</code> and two Pythagorean arms <code>(a0,b0)</code> and <code>(a1,b1)</code>. The arm lengths can differ, and the two endpoint curvatures can be tuned independently. That is the natural way to give a piece a G2 match on both sides: rotate at a Pythagorean angle, translate on integers, choose or scale the arms for the two curvatures, then clear the common denominator.</p>
  <p>This is a direction, not yet a proved recipe. A zero-curvature endpoint cannot be scaled into a nonzero one, the sign of curvature must match, and the required integer scale may be large. The asymmetric shape also moves the inflection, so it needs a shape and clearance check, not only a curvature check.</p>

  <h3>What to add next</h3>
  <ul>
    <li>a split-and-scale helper with exact rational arithmetic and tests at <code>t=1/2</code> and <code>t=1/3</code>;</li>
    <li>a G2 join probe that reports tangent mismatch, curvature mismatch, and the final integer scale;</li>
    <li>an asymmetric-arm search: which pairs of Pythagorean arms can match two chosen endpoint curvatures;</li>
    <li>one offset comparison on this curve, labelled fitted rather than exact;</li>
    <li>a small lattice census: which integer points appear at chosen scales, and how large the scales get;</li>
    <li>a two-parabola S probe: elevate two quadratics, solve the G2 join, and compare with the cubic.</li>
  </ul>
</section>


<section class="panel">
  <h2>The 60³ grid</h2>
  <p>A natural asymmetric example is the quarter-turn cubic</p>
  <div class="formula">P0=(0,0), P1=(4,−3), P2=(7,−4), P3=(10,0)</div>
  <p>It starts at slope <code>−3/4</code>, ends at slope <code>4/3</code>, and has integer controls. Take <code>Q=3·4·5=60</code>. Every point at <code>t=k/60</code> has a denominator dividing <code>60³</code>, so scaling by <code>60³ = 216000</code> puts all 61 sampled points on one integer grid.</p>
  <div class="figure">__GRID_SVG__</div>
  <p class="small">The 61 points are parameter samples, not arc-length points. The grid is a consequence of the integer controls and the chosen denominator; it does not make offsets or arbitrary curve points integer.</p>
</section>


<section class="panel">
  <h2>Another route: elevate a quadratic</h2>
  <p>A quadratic Bézier is a parabola. Degree elevation turns it into a cubic without changing the curve:</p>
  <div class="formula">R0=Q0, R1=(Q0+2Q1)/3, R2=(2Q1+Q2)/3, R3=Q2</div>
  <p>That is exact, not a fit. If the quadratic controls are integers, the elevated controls may acquire a factor of 3; scale by 3 to clear it. Points at a rational <code>t=p/q</code> have denominators dividing <code>q²</code> for the quadratic, which is cheaper than the cubic’s <code>q³</code>.</p>
  <p>A single parabola cannot make an S: its curvature has one sign. An S needs two pieces, one on each side of the inflection. If you start with two quadratics and elevate them, the piecewise-parabolic S is exact for that design. If you start with the existing integer cubic S and split it at <code>1/2</code>, each half is still a cubic; replacing each half by a quadratic is an approximation, not an exact elevation.</p>
  <p>The trade is fewer shape controls. Two parabolas give a clean S and easy G1 joins, but G2 still requires a curvature match, and the family has fewer degrees of freedom than the asymmetric cubic. Parabola offsets are also not rational in general.</p>
  <div class="table-wrap"><table>
    <tr><th>representation</th><th>exact for</th><th>point denominator</th><th>shape freedom</th></tr>
    <tr><td>single cubic</td><td>a cubic</td><td>q³</td><td>high; asymmetric arms</td></tr>
    <tr><td>elevated quadratic</td><td>one parabola</td><td>q², then ×3 for integer controls</td><td>one bend</td></tr>
    <tr><td>two elevated quadratics</td><td>a piecewise-parabolic S</td><td>q² per piece</td><td>two bends; join conditions</td></tr>
  </table></div>
</section>

<section class="panel">
  <h2>The 3125 circle</h2>
  <p>The integer points on <code>x²+y²=3125</code> have these slopes:</p>
  <p class="small">__ANGLES__</p>
  <p>Each is a rational-lattice rotation. Scale by 3125 to clear the denominator and return to integer control points.</p>
</section>

<section class="panel">
  <h2>Verification</h2>
  <p><code>curve_lab/pyth_cubic.py</code> builds the family; <code>tests/test_pyth_cubic.py</code> checks every case, the 3-4-5 coordinates, the 53.13° angle, and both rotated/scaled examples. Re-run with:</p>
  <div class="formula">.venv/bin/python -m unittest tests.test_pyth_cubic</div>
</section>
</main>

<script>
(() => {
  const CASES = __DATA__;
  const W=1000,H=420,PAD=44;
  const canvas=document.getElementById('tri-canvas');
  const ctx=canvas.getContext('2d');
  const dpr=window.devicePixelRatio||1;
  canvas.width=W*dpr; canvas.height=H*dpr;
  ctx.setTransform(dpr,0,0,dpr,0,0);

  function draw(index){
    const c=CASES[index];
    const pts=[c.p0,c.p1,c.p2,c.p3];
    const xs=pts.map(p=>p[0]), ys=pts.map(p=>p[1]);
    const x0=Math.min(...xs), x1=Math.max(...xs);
    const y0=Math.min(...ys), y1=Math.max(...ys);
    const dx=x1-x0||1, dy=y1-y0||1, pad=.12;
    const xa=x0-pad*dx, xb=x1+pad*dx, ya=y0-pad*dy, yb=y1+pad*dy;
    const k=Math.min((W-2*PAD)/(xb-xa),(H-2*PAD)/(yb-ya));
    const ox=(W-(xb-xa)*k)/2, oy=(H-(yb-ya)*k)/2;
    const px=x=>ox+(x-xa)*k, py=y=>H-oy-(y-ya)*k;
    ctx.clearRect(0,0,W,H); ctx.fillStyle='#fbf7ec'; ctx.fillRect(0,0,W,H);
    const step=Math.max(1,Math.ceil(Math.max(dx,dy)/26));
    ctx.strokeStyle='#e4dcc6'; ctx.lineWidth=1;
    for(let gx=Math.ceil(xa/step)*step;gx<=xb;gx+=step){
      ctx.beginPath(); ctx.moveTo(px(gx),py(ya)); ctx.lineTo(px(gx),py(yb)); ctx.stroke();
    }
    for(let gy=Math.ceil(ya/step)*step;gy<=yb;gy+=step){
      ctx.beginPath(); ctx.moveTo(px(xa),py(gy)); ctx.lineTo(px(xb),py(gy)); ctx.stroke();
    }
    ctx.strokeStyle='#b9aa88'; ctx.strokeRect(px(xa),py(yb),px(xb)-px(xa),py(ya)-py(yb));
    ctx.beginPath(); pts.forEach((p,i)=>i?ctx.lineTo(px(p[0]),py(p[1])):ctx.moveTo(px(p[0]),py(p[1])));
    ctx.strokeStyle='#7b6c4e'; ctx.lineWidth=1; ctx.setLineDash([4,4]); ctx.stroke(); ctx.setLineDash([]);
    ctx.beginPath();
    for(let i=0;i<=160;i++){
      const t=i/160,u=1-t;
      const x=u*u*u*c.p0[0]+3*u*u*t*c.p1[0]+3*u*t*t*c.p2[0]+t*t*t*c.p3[0];
      const y=u*u*u*c.p0[1]+3*u*u*t*c.p1[1]+3*u*t*t*c.p2[1]+t*t*t*c.p3[1];
      i?ctx.lineTo(px(x),py(y)):ctx.moveTo(px(x),py(y));
    }
    ctx.strokeStyle='#2e2413'; ctx.lineWidth=2.6; ctx.stroke();
    for(const [name,p] of [['P0',c.p0],['P1',c.p1],['P2',c.p2],['P3',c.p3]]){
      const x=px(p[0]),y=py(p[1]);
      ctx.fillStyle=name==='P1'||name==='P2'?'#c9a441':'#fbf7ec';
      ctx.strokeStyle='#2e2413'; ctx.lineWidth=1.3;
      if(name==='P1'||name==='P2'){ctx.fillRect(x-4.5,y-4.5,9,9);ctx.strokeRect(x-4.5,y-4.5,9,9);}
      else{ctx.beginPath();ctx.arc(x,y,5,0,7);ctx.fill();ctx.stroke();}
      ctx.fillStyle='#2e2413'; ctx.font='11px ui-monospace,Menlo,monospace';
      ctx.fillText(`${name} (${p[0]}, ${p[1]})`,x+7,y-7);
    }
    ctx.fillStyle='#2e2413'; ctx.font='600 15px Georgia,serif';
    ctx.fillText(`Fig. P1 · ${c.label} · integer cubic`,14,23);
    ctx.font='10px ui-monospace,Menlo,monospace'; ctx.fillStyle='#7b6c4e';
    ctx.fillText(`chord ${c.chord} · arm ${c.arm} · tangent ${c.angle.toFixed(3)}°`,14,39);
    ctx.fillText('— cubic   -- control polygon   ■ integer handles   ○ ends',14,55);
    document.getElementById('tri-meta').textContent =
      `${c.label} · P1=(${c.p1[0]}, ${c.p1[1]}) · P2=(${c.p2[0]}, ${c.p2[1]}) · chord ${c.chord} · arm ${c.arm} · tangent ${c.angle.toFixed(3)}°`;
  }
  document.querySelectorAll('#tri-buttons button').forEach(b => {
    b.addEventListener('click', () => draw(Number(b.dataset.index)));
  });
  draw(0);
})();
</script>
</body>
</html>
"""
    page = (page.replace("__BUTTONS__", buttons)
                .replace("__ROWS__", rows)
                .replace("__ANGLES__", angles)
                .replace("__DATA__", data)
                .replace("__GRID_SVG__", grid_svg_markup))
    out = ROOT / "workbench" / "integer-cubic.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    print(f"  {len(cases)} Pythagorean cases")


if __name__ == "__main__":
    main()
