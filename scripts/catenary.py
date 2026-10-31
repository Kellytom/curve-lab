"""Two catenary projects in one sandbox.

    .venv/bin/python scripts/catenary.py
    open docs/catenary.html

A. A catenary chained from pythagorean triples: every chord's direction is a
   triple's slope, the chord length is the arc step the catenary asks for, so
   the chain is a stair of real triangles that tracks cosh.

B. Weil's catenary drapery in 2.5D: each row of the sheet is the catenary of
   its own rest width, so the cloth gathers and sags as it hangs.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from curve_families import path_d  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
INK = "#2e2413"
GOLD = "#c9a441"
GRID = "#e8dfc8"
LINE = "#d8ccae"
MUTED = "#7b6c4e"


# -- A: the pythagorean catenary -------------------------------------------

def ladder(max_h: int = 500, max_deg: float = 62.0):
    """Pythagorean slopes as angles, sorted: the rungs the chain may use."""
    seen, rungs = set(), []
    for u in range(1, max_h):
        for v in range(u + 1, max_h):
            h = math.isqrt(u * u + v * v)
            if h * h != u * u + v * v or h > max_h:
                continue
            for legs in ((u, v), (v, u)):
                ang = math.degrees(math.atan2(legs[0], legs[1]))
                if ang > max_deg:
                    continue
                key = round(ang, 2)
                if key in seen:
                    continue
                seen.add(key)
                rungs.append({"deg": ang, "triple": (legs[0], legs[1], h)})
    rungs.sort(key=lambda r: r["deg"])
    return rungs


RUNGS = ladder()
DEGREES = [r["deg"] for r in RUNGS]


def snap(theta_deg: float) -> float:
    """The nearest rung: the chain only turns to angles a triple can make."""
    return min(DEGREES, key=lambda d: abs(d - theta_deg))


def cat(a: float, s: float):
    """The point at arc length s from the vertex, in catenary coordinates."""
    u = s / a
    return (a * math.asinh(u), a * (math.sqrt(1 + u * u) - 1))


def branch(a: float, length: float, steps: int):
    """Chain chords of equal arc, each aimed along the nearest triple."""
    pts = [(0.0, 0.0)]
    step = length / steps
    for i in range(1, steps + 1):
        s = i * step
        theta = snap(math.degrees(math.atan(s / a)))
        x, y = pts[-1]
        pts.append((x + step * math.cos(math.radians(theta)),
                    y + step * math.sin(math.radians(theta))))
    return pts


def branch_error(a: float, length: float, steps: int):
    """Worst distance from a chain node to the true catenary at the same arc."""
    pts = branch(a, length, steps)
    worst = 0.0
    for i, p in enumerate(pts):
        q = cat(a, i * length / steps)
        worst = max(worst, math.dist(p, q))
    return worst


def fig_catenary(a=100.0, high=0.62, steps=26, gold=True) -> str:
    """Both branches on one catenary: down to the vertex, then up from it."""
    total = 2.2 * a
    up = branch(a, high * total, steps)                    # to the higher anchor
    down = [(-x, y) for x, y in branch(a, (1 - high) * total, steps)]
    down.reverse()                                          # left anchor -> vertex
    chain = down + up[1:]

    if gold:
        true = [(-cat(a, (1 - high) * total * i / 200)[0],
                 cat(a, (1 - high) * total * i / 200)[1]) for i in range(200, -1, -1)]
        true += [cat(a, high * total * i / 200) for i in range(1, 201)]
    else:
        true = []

    pts = chain + true
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    w, h = 860.0, 380.0
    margin = 40.0
    scale = min((w - 2 * margin) / (x1 - x0), (h - 2 * margin) / (y1 - y0))
    dx = (w - (x1 - x0) * scale) / 2
    dy = (h - (y1 - y0) * scale) / 2

    def at(p):
        return (dx + (p[0] - x0) * scale, h - (dy + (p[1] - y0) * scale))

    # the triangles, on the first few chords of each branch
    tris = []
    for i in range(1, min(5, len(up))):
        (px, py), (qx, qy) = at(up[i - 1]), at(up[i])
        tris.append(f'<path d="M {px:.2f} {py:.2f} L {qx:.2f} {py:.2f} '
                    f'L {qx:.2f} {qy:.2f} Z" fill="none" stroke="{GOLD}" '
                    f'stroke-width="0.8" opacity="0.75"/>')
    for i in range(len(down) - 1, max(len(down) - 5, 0), -1):
        (px, py), (qx, qy) = at(down[i - 1]), at(down[i])
        tris.append(f'<path d="M {px:.2f} {py:.2f} L {px:.2f} {qy:.2f} '
                    f'L {qx:.2f} {qy:.2f} Z" fill="none" stroke="{GOLD}" '
                    f'stroke-width="0.8" opacity="0.75"/>')

    gold_line = ""
    if true:
        gold_line = (f'<path d="{path_d([at(p) for p in true])}" fill="none" '
                     f'stroke="{GOLD}" stroke-width="1.2" stroke-dasharray="6 5"/>')

    dots = ""
    for p, label in ((chain[0], "high anchor"), (chain[-1], "low anchor")):
        x, y = at(p)
        dots += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{INK}"/>'
    vx, vy = at((0.0, 0.0))
    dots += (f'<circle cx="{vx:.1f}" cy="{vy:.1f}" r="4" fill="#fff" '
             f'stroke="{INK}" stroke-width="1.6"/>')

    return f"""<svg viewBox="0 0 {w:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="#fff"
          stroke="{LINE}" stroke-width="1"/>
    {gold_line}
    {''.join(tris)}
    <path d="{path_d([at(p) for p in chain])}" fill="none" stroke="{INK}"
          stroke-width="2.2" stroke-linejoin="round"/>
    {dots}
  </svg>"""


# -- B: catenary drapery ----------------------------------------------------

def row_catenary(span: float, arc: float, n: int = 40):
    """A catenary of fixed arc hanging on a span shorter than that arc."""
    lo, hi = 1e-6 * span, 1e6 * span
    for _ in range(90):
        a = (lo + hi) / 2
        if 2 * a * math.sinh(span / (2 * a)) > arc:
            lo = a
        else:
            hi = a
    a = (lo + hi) / 2
    return [(x, a * (math.cosh(x / a) - 1))
            for x in (-span / 2 + span * i / n for i in range(n + 1))], a


def drape_svg(gather=0.35, rows=9, cols=44, w=860.0, h=430.0) -> str:
    """The sheet in 2.5D: rows are catenaries, each seen from above and ahead."""
    rest = 700.0
    margin = 30.0
    parts, ys, xs_all = [], [], []
    rows_pts = []
    for j in range(rows + 1):
        span = rest * (1 - gather * j / rows)
        depth = 120.0 * j / rows
        pts, _ = row_catenary(span, rest, cols)
        # project: x across, the sag lifts the row up the page, rows recede
        row = [(p[0], -p[1] * 0.55 - depth) for p in pts]
        rows_pts.append(row)
        ys += [q[1] for q in row]
        xs = [q[0] for q in row]
        xs_all += xs

    x0, x1 = min(xs_all), max(xs_all)
    y0, y1 = min(ys), max(ys)
    scale = min((w - 2 * margin) / (x1 - x0), (h - 2 * margin) / (y1 - y0))
    dx = (w - (x1 - x0) * scale) / 2
    dy = (h - (y1 - y0) * scale) / 2

    def at(p):
        return (dx + (p[0] - x0) * scale, h - (dy + (p[1] - y0) * scale))

    for j, row in enumerate(rows_pts):
        shade = f"rgba(46,36,19,{0.9 - 0.5 * j / rows:.2f})"
        parts.append(f'<path d="{path_d([at(p) for p in row])}" fill="none" '
                     f'stroke="{shade}" stroke-width="1.5"/>')

    return f"""<svg viewBox="0 0 {w:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="#fff"
          stroke="{LINE}" stroke-width="1"/>
    {''.join(parts)}
  </svg>"""


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
    color:var(--muted); margin:30px 0 8px; }
  h2 span { color: var(--gold); }
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
  .two { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
  .three { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; }
  .three figure { margin:0; }
  .three figcaption { font:10px/1.3 var(--mono); color:var(--muted); margin-top:4px; }
  #view { width:100%; height:440px; background:#fff; border:1px solid var(--line);
    border-radius:3px; display:block; cursor:grab; }
  #view:active { cursor:grabbing; }
  .controls { display:flex; gap:16px; align-items:center; flex-wrap:wrap;
    font:11px var(--mono); color:var(--muted); margin:8px 0 0; }
  .controls input[type=range] { width:130px; accent-color:#8c6a21; }
  .controls label { display:flex; gap:6px; align-items:center; }
  .next { border-left:3px solid var(--gold); padding-left:10px; color:var(--muted); }
  @media (max-width:620px) {
    main { padding:22px 14px 60px; }
    table { font-size:10px; } th,td { padding:4px 2px; }
    .two, .three { grid-template-columns:1fr; }
  }
"""

SCRIPT = r"""
import * as THREE from 'three';

const host = document.getElementById('view');
let renderer;
try {
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false,
    preserveDrawingBuffer: true });
} catch (err) {
  host.innerHTML = '<p style="font:12px/1.5 ui-monospace,monospace;color:#7b6c4e;' +
    'padding:18px">This browser has no WebGL, so the 2.5D view cannot run here.' +
    ' The 2D figure above is the same drape.</p>';
  throw err;
}
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
host.appendChild(renderer.domElement);
renderer.domElement.style.width = '100%';
renderer.domElement.style.height = '100%';
renderer.domElement.style.display = 'block';

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xffffff);

const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100);
let yaw = -0.62, pitch = 0.34, dist = 7.4;
function place() {
  camera.position.set(
    dist * Math.cos(pitch) * Math.sin(yaw),
    dist * Math.sin(pitch),
    dist * Math.cos(pitch) * Math.cos(yaw));
  camera.lookAt(0, -0.15, 0);
}

const hemi = new THREE.HemisphereLight(0xfffdf6, 0x6d6248, 0.55);
const key = new THREE.DirectionalLight(0xffffff, 0.85);
key.position.set(3, 5, 4);
scene.add(hemi, key);

const material = new THREE.MeshStandardMaterial({
  color: 0xdfd2b4, roughness: 0.9, metalness: 0.0,
  side: THREE.DoubleSide, flatShading: false,
  wireframe: false
});

// a catenary of fixed arc on a span shorter than the arc
function rowCatenary(span, arc, n) {
  let lo = 1e-6 * span, hi = 1e6 * span, a = 0;
  for (let k = 0; k < 90; k++) {
    a = (lo + hi) / 2;
    if (2 * a * Math.sinh(span / (2 * a)) > arc) lo = a; else hi = a;
  }
  a = (lo + hi) / 2;
  const out = [];
  for (let i = 0; i <= n; i++) {
    const x = -span / 2 + span * i / n;
    out.push([x, a * (Math.cosh(x / a) - 1)]);
  }
  return out;
}

let mesh = null, pinGroup = null;
const state = { gather: 0.42, rows: 26, cols: 46, wire: false };

function build() {
  if (mesh) { scene.remove(mesh); mesh.geometry.dispose(); }
  if (pinGroup) { scene.remove(pinGroup); pinGroup = null; }

  const rows = state.rows, cols = state.cols;
  const rest = 4.6;               // rest width of the sheet, in scene units
  const height = 3.0;
  const pos = [];

  for (let j = 0; j <= rows; j++) {
    const t = j / rows;
    const span = rest * (1 - state.gather * t);
    const row = rowCatenary(span, rest, cols);
    for (let i = 0; i <= cols; i++) {
      pos.push(row[i][0], -t * height, row[i][1] * 1.0);
    }
  }

  const index = [];
  for (let j = 0; j < rows; j++) {
    for (let i = 0; i < cols; i++) {
      const a = j * (cols + 1) + i, b = a + 1, c = a + cols + 1, d = c + 1;
      index.push(a, c, b, b, c, d);
    }
  }

  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  geo.setIndex(index);
  geo.computeVertexNormals();

  material.wireframe = state.wire;
  mesh = new THREE.Mesh(geo, material);
  scene.add(mesh);

  // the two pins: the top corners
  pinGroup = new THREE.Group();
  const pinMat = new THREE.MeshStandardMaterial({ color: 0x8c6a21, roughness: 0.5 });
  for (const x of [-rest / 2, rest / 2]) {
    const s = new THREE.Mesh(new THREE.SphereGeometry(0.07, 16, 12), pinMat);
    s.position.set(x, 0, 0);
    pinGroup.add(s);
  }
  scene.add(pinGroup);
}

function render() { renderer.render(scene, camera); }

function resize() {
  const w = host.clientWidth, h = host.clientHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  place();
  render();
}

// a small orbit, so no second vendor file is needed
let dragging = false, lastX = 0, lastY = 0;
host.addEventListener('pointerdown', e => { dragging = true; lastX = e.clientX; lastY = e.clientY; host.setPointerCapture(e.pointerId); });
host.addEventListener('pointerup', e => { dragging = false; });
host.addEventListener('pointermove', e => {
  if (!dragging) return;
  yaw -= (e.clientX - lastX) * 0.008;
  pitch = Math.max(-0.15, Math.min(0.95, pitch + (e.clientY - lastY) * 0.006));
  lastX = e.clientX; lastY = e.clientY;
});
host.addEventListener('wheel', e => {
  e.preventDefault();
  dist = Math.max(3.5, Math.min(14, dist + e.deltaY * 0.004));
}, { passive: false });

window.addEventListener('resize', resize);

const gatherEl = document.getElementById('gather');
const gatherOut = document.getElementById('gatherOut');
const wireEl = document.getElementById('wire');
gatherEl.value = state.gather;
gatherOut.textContent = state.gather.toFixed(2);
gatherEl.addEventListener('input', () => {
  state.gather = parseFloat(gatherEl.value);
  gatherOut.textContent = state.gather.toFixed(2);
  build();
  render();
});
wireEl.addEventListener('change', () => { state.wire = wireEl.checked; build(); render(); });

build();
resize();          // sizes, places the camera, and draws the first frame
render();
renderer.setAnimationLoop(() => { place(); render(); });
window.__dbgObj = () => ({ scene, camera, renderer, mesh });
window.__dbg = () => ({ cam: camera.position.toArray().map(v => +v.toFixed(2)),
  verts: mesh ? mesh.geometry.attributes.position.count : 0,
  children: scene.children.length });
"""


def main() -> int:
    a = 100.0
    total = 2.2 * a
    steps = 26

    fig_main = fig_catenary(a, 0.62, steps)
    err_hi = branch_error(a, 0.62 * total, steps)
    err_lo = branch_error(a, 0.38 * total, steps)

    # three splits of the same catenary
    small = []
    for p in (0.50, 0.62, 0.75):
        svg = fig_catenary(a, p, steps, gold=False)
        small.append(f'<figure>{svg}<figcaption>split {p:.2f} : '
                     f'{1 - p:.2f}</figcaption></figure>')

    rows = []
    for s in range(1, steps + 1):
        ang = math.degrees(math.atan(s * 0.62 * total / steps / a))
        rows.append((s, ang, snap(ang)))
    page_rows = []
    for i, ang, sn in rows:
        node = RUNGS[min(range(len(RUNGS)), key=lambda k: abs(RUNGS[k]["deg"] - sn))]
        page_rows.append(
            f"<tr><td>{i}</td><td>{ang:.1f}°</td><td>{node['deg']:.2f}°</td>"
            f"<td>{node['triple'][0]}-{node['triple'][1]}-{node['triple'][2]}</td>"
            f"<td>{sn - ang:+.1f}°</td></tr>")

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Catenary sandbox: triples and drapery</title>
<style>{CSS}</style>
<script type="importmap">{{ "imports": {{ "three": "./vendor/three.module.js" }} }}</script>
</head>
<body>
<main>
  <p class="back"><a href="sandbox.html">← sandbox</a> ·
  <a href="stage-two.html">the stage II page</a></p>
  <h1>Catenary sandbox</h1>
  <p class="lead">Two projects running side by side: one hangs a catenary on
  pythagorean triangles, the other drapes a cloth on catenaries.</p>

  <h2>A · <span>the catenary, chained from triples</span></h2>
  <div class="panel">
    <p>A catenary asks for a tangent angle that changes with arc length:
    <code>tan θ = s/a</code>. The chain here may only take directions that a
    pythagorean triple can make, so each step snaps θ to the nearest rung of a
    {len(RUNGS)}-rung ladder, then lays a chord of the arc length that step
    deserves. Every chord is the hypotenuse of a real triangle — two of them
    are drawn on each end.</p>
    <p>The two branches share one catenary. Down to the vertex is
    <em>toward the focus</em>; up from it is <em>away</em>. The split sets how
    much of the curve each side owns, and since height rises with arc, the side
    that owns more is also the higher anchor. At {0.62:.2f} : {0.38:.2f} the
    high anchor sits {0.71 * a:.0f} above the vertex and the low one
    {0.32 * a:.0f}.</p>
    <div class="strip">{fig_main}
      <p><strong>Fig. 1</strong> · the chain (ink) on the true catenary (gold) ·
      arc {total:.0f}, split 0.62 : 0.38 · worst node error
      {max(err_hi, err_lo):.1f} on the high branch
      ({100 * max(err_hi, err_lo) / total:.1f}% of arc)</p></div>
    <div class="three">{''.join(small)}</div>
    <p style="margin-top:10px" class="next">The split is the only dial a
    drapery needs: it says where the low point sits, and therefore which
    anchor the cloth is hanging from.</p>
    <div class="scroll"><table style="margin-top:10px">
      <tr><th>step</th><th>catenary wants</th><th>triple angle</th>
      <th>triple</th><th>error</th></tr>
      {''.join(page_rows[:10])}
    </table></div>
    <p style="margin-top:8px">First ten steps of the high branch, at
    a = {a:.0f}. The ladder is the whole catalogue of slopes below
    {max(DEGREES):.0f}° with hypotenuse ≤ 500; gaps between rungs are what the
    error column measures.</p>
  </div>

  <h2>B · <span>catenary drapery, in 2.5D</span></h2>
  <div class="panel">
    <p>Weil's method is geometric, not physical: cloth is a grid of points, and
    the shape is found by fitting catenaries between the restraint points,
    splitting each triangle by the <em>lower</em> of the two candidate
    catenaries, then relaxing so the points keep their spacing. It aims at the
    look of cloth, not its properties. (The page it comes from is
    <a href="https://davis.wpi.edu/~matt/courses/cloth/geometric.html">WPI's
    geometric techniques</a>, which also covers Agui's sleeve folds.)</p>
    <p>What is built here is the first half, the hanging: every row of the
    sheet is the catenary of its own rest width, so a row that has lost span
    sags more, and the cloth gathers toward the free edge. The relaxation pass
    is not in yet — the rows keep equal spacing down the sheet, which is why
    the folds read as neat rather than lived-in.</p>
    <div class="strip">{drape_svg()}
      <p><strong>Fig. 2</strong> · nine rows, each the catenary of the full
      rest width on a span that narrows with depth</p></div>
    <canvas id="view"></canvas>
    <div class="controls">
      <label>gather <input id="gather" type="range" min="0" max="0.7"
        step="0.01" value="0.42"><span id="gatherOut">0.42</span></label>
      <label><input id="wire" type="checkbox"> wireframe</label>
      <span>drag to orbit · wheel to zoom</span>
    </div>
    <p style="margin:5px 0 0; font:10px/1.3 var(--mono); color:var(--muted)">
      <strong>Fig. 3</strong> · the same drape in 2.5D (three.js) — 26 × 46
      grid, two pins at the top corners</p>
  </div>
</main>
<script type="module">{SCRIPT}</script>
</body>
</html>
"""
    path = ROOT / "docs" / "catenary.html"
    path.write_text(page, encoding="utf-8")
    print(path)
    print(f"rungs={len(RUNGS)} max_err={max(err_hi, err_lo):.2f} a={a}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
