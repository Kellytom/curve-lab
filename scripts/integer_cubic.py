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


def main():
    cases = pyth_cubic.cases()
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
                .replace("__DATA__", data))
    out = ROOT / "workbench" / "integer-cubic.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    print(f"  {len(cases)} Pythagorean cases")


if __name__ == "__main__":
    main()
