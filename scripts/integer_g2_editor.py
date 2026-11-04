"""Interactive integer G2 pair editor.

    .venv/bin/python scripts/integer_g2_editor.py

Writes `workbench/integer-g2-editor.html`. The starting state is the exact
scale-1 asymmetric pair from `curve_lab.pyth_g2`; dragging a point shows how
quickly G1/G2 is lost away from that exact configuration.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab import pyth_cubic, pyth_g2  # noqa: E402


def main():
    pair = pyth_g2.asymmetric_pair()
    page = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Integer G2 pair · drag probe</title>
<style>
:root{--paper:#fbf7ec;--ink:#2e2413;--muted:#7b6c4e;--rule:#d8ccae;--gold:#c9a441;--blue:#1f5fa8}
*{box-sizing:border-box}
body{margin:0;background:#f3eddf;color:var(--ink);font:16px/1.55 Georgia,serif}
main{max-width:1180px;margin:0 auto;padding:34px 22px 70px}
.eyebrow{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}
h1{font-size:32px;line-height:1.1;margin:0 0 7px}
h2{font-size:21px;margin:0 0 9px}
.lede{max-width:900px;color:var(--muted);margin:0 0 18px}
.panel{background:var(--paper);border:1px solid var(--rule);padding:15px 18px;margin:0 0 18px}
.controls{display:flex;flex-wrap:wrap;gap:9px 16px;align-items:center;margin:0 0 9px;font:11px/1.4 ui-monospace,Menlo,monospace;color:var(--muted)}
.controls button{border:1px solid var(--rule);background:var(--paper);color:var(--ink);padding:5px 9px;font:inherit;cursor:pointer}
.controls button:hover{background:#f4ecd7}
.controls label{display:flex;gap:5px;align-items:center}
canvas{display:block;width:100%;height:auto;border:1px solid var(--rule);background:var(--paper);touch-action:none}
.readout{font:12px/1.65 ui-monospace,Menlo,monospace;color:var(--muted);margin:9px 0 0;white-space:pre-wrap}
.good{color:#3f7d4e;font-weight:600}
.bad{color:#a23b2a;font-weight:600}
.small{font:12px/1.55 ui-monospace,Menlo,monospace;color:var(--muted)}
code{font:12px ui-monospace,Menlo,monospace;background:#f4ecd7;padding:1px 4px}
</style>
</head>
<body>
<main>
<p class="eyebrow">curve-lab · interactive G2 probe</p>
<h1>Integer G2 pair · drag probe</h1>
<p class="lede">The starting pair is exact: A ends where reflected B begins, with matching tangent and curvature. Drag an anchor or handle. Integer snapping keeps every point on the lattice, but G2 survives only when the tangent direction and curvature both still agree.</p>

<section class="panel">
  <h2>Drag the points</h2>
  <div class="controls">
    <button id="reset" type="button">reset exact pair</button>
    <label><input type="checkbox" id="snap" checked> snap to integers</label>
    <label><input type="checkbox" id="tangents" checked> show join tangents</label>
    <span>○ anchors · ■ handles · black = G2 join</span>
  </div>
  <canvas id="editor" width="1000" height="560" aria-label="Interactive two-piece integer cubic with G2 diagnostics"></canvas>
  <p class="readout" id="readout" aria-live="polite"></p>
</section>

<section class="panel">
  <h2>What the check means</h2>
  <p class="small"><strong>G1</strong> = the two endpoint tangent directions agree. <strong>G2</strong> = G1 plus the signed curvatures agree. Integer snapping is a separate property: a point can be integer and still miss either condition. The exact pair is the only guaranteed G2 state here; free dragging is a probe, not a solver.</p>
</section>
</main>

<script>
(() => {
  const A0 = [[0,0],[7,-24],[46,3],[50,0]];
  const B0 = [[50,0],[54,-3],[39,-48],[64,-48]];
  let A = A0.map(p => [...p]), B = B0.map(p => [...p]);

  const canvas = document.getElementById('editor');
  const ctx = canvas.getContext('2d');
  const readout = document.getElementById('readout');
  const snapBox = document.getElementById('snap');
  const tangentBox = document.getElementById('tangents');
  const W = 1000, H = 560, PAD = 46;
  const DOM = {x0:-10, x1:70, y0:-60, y1:32};
  const scale = Math.min((W-2*PAD)/(DOM.x1-DOM.x0), (H-2*PAD)/(DOM.y1-DOM.y0));
  const ox = (W-(DOM.x1-DOM.x0)*scale)/2, oy=(H-(DOM.y1-DOM.y0)*scale)/2;
  const SX = x => ox + (x-DOM.x0)*scale;
  const SY = y => H - oy - (y-DOM.y0)*scale;
  const UX = x => DOM.x0 + (x-ox)/scale;
  const UY = y => DOM.y0 + (H-oy-y)/scale;
  let drag = null;

  const targets = () => [
    {id:'A0', p:A[0], set:p=>{A[0]=p;}},
    {id:'A1', p:A[1], set:p=>{A[1]=p;}},
    {id:'A2', p:A[2], set:p=>{A[2]=p;}},
    {id:'join', p:A[3], set:p=>{A[3]=p; B[0]=p;}},
    {id:'B1', p:B[1], set:p=>{B[1]=p;}},
    {id:'B2', p:B[2], set:p=>{B[2]=p;}},
    {id:'B3', p:B[3], set:p=>{B[3]=p;}},
  ];

  function cubic(P, t){
    const u=1-t;
    return [u*u*u*P[0][0]+3*u*u*t*P[1][0]+3*u*t*t*P[2][0]+t*t*t*P[3][0],
            u*u*u*P[0][1]+3*u*u*t*P[1][1]+3*u*t*t*P[2][1]+t*t*t*P[3][1]];
  }
  function cross(a,b){return a[0]*b[1]-a[1]*b[0];}
  function sub(a,b){return [a[0]-b[0],a[1]-b[1]];}
  function add(a,b){return [a[0]+b[0],a[1]+b[1]];}
  function mul(a,k){return [a[0]*k,a[1]*k];}
  function len(a){return Math.hypot(a[0],a[1]);}
  function endTangent(P){return mul(sub(P[3],P[2]),3);}
  function startTangent(P){return mul(sub(P[1],P[0]),3);}
  function endCurvature(P){
    const v=sub(P[3],P[2]);
    const w=[P[3][0]-2*P[2][0]+P[1][0], P[3][1]-2*P[2][1]+P[1][1]];
    return (2/3)*cross(v,w)/Math.pow(len(v),3);
  }
  function startCurvature(P){
    const v=sub(P[1],P[0]);
    const w=[P[2][0]-2*P[1][0]+P[0][0], P[2][1]-2*P[1][1]+P[0][1]];
    return (2/3)*cross(v,w)/Math.pow(len(v),3);
  }
  function diagnostics(){
    const ta=endTangent(A), tb=startTangent(B);
    const ka=endCurvature(A), kb=startCurvature(B);
    const g1=Math.abs(cross(ta,tb))<1e-9 && ta[0]*tb[0]+ta[1]*tb[1]>0;
    const g2=g1 && Math.abs(ka-kb)<1e-9;
    const integer=[...A,...B].every(p=>Number.isInteger(p[0])&&Number.isInteger(p[1]));
    return {ta,tb,ka,kb,g1,g2,integer};
  }
  function drawPath(P, colour){
    ctx.beginPath();
    for(let i=0;i<=100;i++){
      const p=cubic(P,i/100), x=SX(p[0]), y=SY(p[1]);
      i?ctx.lineTo(x,y):ctx.moveTo(x,y);
    }
    ctx.strokeStyle=colour; ctx.lineWidth=2.6; ctx.stroke();
  }
  function drawPolygon(P, colour){
    ctx.beginPath();
    P.forEach((p,i)=>{const x=SX(p[0]),y=SY(p[1]); i?ctx.lineTo(x,y):ctx.moveTo(x,y);});
    ctx.strokeStyle=colour; ctx.lineWidth=1; ctx.setLineDash([4,4]); ctx.stroke(); ctx.setLineDash([]);
  }
  function draw(){
    ctx.clearRect(0,0,W,H); ctx.fillStyle='#fbf7ec'; ctx.fillRect(0,0,W,H);
    ctx.strokeStyle='#e4dcc6'; ctx.lineWidth=1;
    for(let x=DOM.x0;x<=DOM.x1;x+=10){
      ctx.beginPath(); ctx.moveTo(SX(x),SY(DOM.y0)); ctx.lineTo(SX(x),SY(DOM.y1)); ctx.stroke();
    }
    for(let y=DOM.y0;y<=DOM.y1;y+=10){
      ctx.beginPath(); ctx.moveTo(SX(DOM.x0),SY(y)); ctx.lineTo(SX(DOM.x1),SY(y)); ctx.stroke();
    }
    drawPolygon(A,'#c9a441'); drawPolygon(B,'#1f5fa8');
    drawPath(A,'#c9a441'); drawPath(B,'#1f5fa8');

    const d=diagnostics();
    if(tangentBox.checked){
      const q=A[3];
      for(const [v,c] of [[d.ta,'#c9a441'],[d.tb,'#1f5fa8']]){
        const L=24/ (len(v)||1);
        ctx.beginPath(); ctx.moveTo(SX(q[0]),SY(q[1])); ctx.lineTo(SX(q[0]+v[0]*L),SY(q[1]+v[1]*L));
        ctx.strokeStyle=c; ctx.lineWidth=1.3; ctx.setLineDash([5,3]); ctx.stroke(); ctx.setLineDash([]);
      }
    }

    for(const t of targets()){
      const x=SX(t.p[0]), y=SY(t.p[1]);
      ctx.strokeStyle='#2e2413'; ctx.lineWidth=1.1;
      ctx.fillStyle=t.id==='join'?'#2e2413':(t.id.startsWith('A')?'#c9a441':'#1f5fa8');
      if(t.id==='join'){ctx.beginPath();ctx.arc(x,y,5,0,7);ctx.fill();}
      else {ctx.beginPath();ctx.arc(x,y,4,0,7);ctx.fill();}
      ctx.fillStyle='#2e2413'; ctx.font='10px ui-monospace,Menlo,monospace';
      ctx.fillText(t.id,x+7,y-7);
    }

    const status = d.g2 ? 'G2 exact' : (d.g1 ? 'G1 only' : 'not G1');
    readout.innerHTML =
      `<strong class="${d.g2?'good':'bad'}">${status}</strong>`+
      ` · G1 ${d.g1?'yes':'no'} · G2 ${d.g2?'yes':'no'} · integer ${d.integer?'yes':'no'}\n`+
      `A end tangent (${d.ta[0].toFixed(3)}, ${d.ta[1].toFixed(3)}) · `+
      `B start tangent (${d.tb[0].toFixed(3)}, ${d.tb[1].toFixed(3)})\n`+
      `A end κ ${d.ka.toFixed(6)} · B start κ ${d.kb.toFixed(6)} · Δκ ${Math.abs(d.ka-d.kb).toFixed(6)}\n`+
      `join (${A[3][0]}, ${A[3][1]})`;
  }

  function nearest(w){
    let best=null, bestD=18;
    for(const t of targets()){
      const d=Math.hypot(SX(t.p[0])-w.x, SY(t.p[1])-w.y);
      if(d<bestD){bestD=d;best=t;}
    }
    return best;
  }
  canvas.addEventListener('pointerdown',ev=>{
    const r=canvas.getBoundingClientRect();
    const w={x:(ev.clientX-r.left)*W/r.width, y:(ev.clientY-r.top)*H/r.height};
    const t=nearest(w);
    if(!t)return;
    drag={target:t, pointerId:ev.pointerId};
    canvas.setPointerCapture(ev.pointerId);
  });
  canvas.addEventListener('pointermove',ev=>{
    if(!drag)return;
    const r=canvas.getBoundingClientRect();
    const w={x:(ev.clientX-r.left)*W/r.width, y:(ev.clientY-r.top)*H/r.height};
    let x=UX(w.x), y=UY(w.y);
    if(snapBox.checked){x=Math.round(x); y=Math.round(y);}
    x=Math.max(DOM.x0,Math.min(DOM.x1,x)); y=Math.max(DOM.y0,Math.min(DOM.y1,y));
    drag.target.set([x,y]); draw();
  });
  canvas.addEventListener('pointerup',ev=>{drag=null;try{canvas.releasePointerCapture(ev.pointerId);}catch(_){}});
  canvas.addEventListener('pointercancel',()=>{drag=null;});
  document.getElementById('reset').addEventListener('click',()=>{
    A=A0.map(p=>[...p]); B=B0.map(p=>[...p]); draw();
  });
  snapBox.addEventListener('change',draw);
  tangentBox.addEventListener('change',draw);
  window.__g2Targets = () => targets().map(t => ({
    id: t.id, x: SX(t.p[0]), y: SY(t.p[1])
  }));
  draw();
})();
</script>
</body>
</html>
'''
    out = ROOT / "workbench" / "integer-g2-editor.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    print(f"  exact pair: join {pair['join']} · tangent {pair['tangent']} · curvature {pair['curvature']}")


if __name__ == "__main__":
    main()
