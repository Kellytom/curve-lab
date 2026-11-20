// The mirrored chain: each step is a p-triple turn, and the step after it is the
// same triple with its last two numbers swapped. For (3,4,5) the chain is
//
//     (3,4,5),  (3,5,4),  (3,4,5),  (3,5,4), ...
//
// The first is a turn on the unit circle. The mirror is a similarity: it turns
// by a slightly different angle *and* grows, so the chain breathes — out on the
// mirror step, back on the unit step (or the reverse, once a damper is on).
// Everything else — the lagged second mover, the sum, the zoom, the save — is
// the same machine as the plain prime mover, on its own ids.
import * as d3 from "d3";

const frac = (text) => {
  const [p, q] = String(text).split("/").map(Number);
  return q ? p / q : 0;
};
const TRIPLES = {
  "3,4,5": [3, 4, 5],
  "7,24,25": [7, 24, 25],
  "5,12,13": [5, 12, 13],
  "8,15,17": [8, 15, 17],
  "20,21,29": [20, 21, 29],
};
let showLabels = true;
const SIZE = 640;

const mirrorOf = (triple) => [triple[0], triple[2], triple[1]];

// even step: the triple itself, on the unit circle.
// odd step: the mirror, a similarity that turns and grows.
function stepFactor(triple, step) {
  const [x, y, z] = triple;
  if (step % 2 === 0) return [x / z, y / z];
  return [x / y, z / y];
}

function walk(triple, steps, netPercent = 100, fromDegrees = 0, limit = 4000) {
  const points = [];
  let z = [1, 0];
  let turned = 0;
  for (let step = 0; step < steps; step += 1) {
    points.push({ x: z[0], y: z[1], step, turned });
    const [a, b] = stepFactor(triple, step);
    const growth = Math.hypot(a, b) || 1;
    const dampAfter = (netPercent / 100) / growth;
    const now = turned >= fromDegrees ? dampAfter : 1;
    z = [(z[0] * a - z[1] * b) * now, (z[0] * b + z[1] * a) * now];
    turned += Math.abs((Math.atan2(b, a) * 180) / Math.PI);
    if (Math.hypot(z[0], z[1]) > limit) break;
  }
  return points;
}

function makePanel(host) {
  const svg = d3.select(host).append("svg")
    .attr("viewBox", `0 0 ${SIZE} ${SIZE}`)
    .attr("width", "100%")
    .attr("role", "img");
  svg.append("rect").attr("width", SIZE).attr("height", SIZE).attr("fill", "#fffdf7");
  const layer = svg.append("g");
  return { svg, layer };
}

function draw(panel, data, domain) {
  const { layer, svg } = panel;
  const pad = 24;
  const x = d3.scaleLinear().domain(domain.x).range([pad, SIZE - pad]);
  const y = d3.scaleLinear().domain(domain.y).range([SIZE - pad, pad]);

  layer.selectAll("*").remove();

  const stepFor = (scale) => {
    const pixels = Math.abs(scale(1) - scale(0));
    const target = 26;
    const magnitudes = [0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1,
      0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000];
    for (const size of magnitudes) {
      if (size * pixels >= target) return size;
    }
    return 1000;
  };
  const stepX = stepFor(x);
  const stepY = stepFor(y);
  const xs = d3.range(Math.floor(domain.x[0] / stepX) * stepX, domain.x[1], stepX);
  const ys = d3.range(Math.floor(domain.y[0] / stepY) * stepY, domain.y[1], stepY);
  layer.append("g").selectAll("line")
    .data(xs).join("line")
    .attr("x1", (v) => x(v)).attr("x2", (v) => x(v))
    .attr("y1", pad).attr("y2", SIZE - pad)
    .attr("stroke", (v) => (Math.abs(v) < 1e-9 ? "#b9a98a" : "#e6dcc6"))
    .attr("stroke-width", (v) => (Math.abs(v) < 1e-9 ? 1.2 : 0.7));
  layer.append("g").selectAll("line")
    .data(ys).join("line")
    .attr("y1", (v) => y(v)).attr("y2", (v) => y(v))
    .attr("x1", pad).attr("x2", SIZE - pad)
    .attr("stroke", (v) => (Math.abs(v) < 1e-9 ? "#b9a98a" : "#e6dcc6"))
    .attr("stroke-width", (v) => (Math.abs(v) < 1e-9 ? 1.2 : 0.7));

  const line = d3.line().x((d) => x(d.x)).y((d) => y(d.y)).curve(d3.curveCatmullRom.alpha(0.5));
  for (const [points, colour, width] of [
    [data.positive, "#e8b98a", 1.4],
    [data.negative, "#9ec3df", 1.4],
    [data.sums, "#6f4a2a", 2.2],
  ]) {
    if (points.length > 2) {
      layer.append("path").datum(points).attr("d", line)
        .attr("fill", "none").attr("stroke", colour).attr("stroke-width", width)
        .attr("stroke-linejoin", "round");
    }
  }

  const all = [...data.positive.map((p) => ({ ...p, hue: "#c9761f" })),
               ...data.negative.map((p) => ({ ...p, hue: "#2f6fa8" })),
               ...data.sums.map((p) => ({ ...p, hue: "#6f4a2a" }))];
  const px = all.map((p) => [x(p.x), y(p.y)]);
  const radius = all.map((_, i) => {
    let nearest = Infinity;
    for (let j = 0; j < px.length; j += 1) {
      if (j === i) continue;
      nearest = Math.min(nearest, Math.hypot(px[i][0] - px[j][0], px[i][1] - px[j][1]));
    }
    return Math.max(1.6, Math.min(5.5, nearest / 3.2));
  });
  layer.append("g").selectAll("circle")
    .data(all).join("circle")
    .attr("cx", (d) => x(d.x)).attr("cy", (d) => y(d.y))
    .attr("r", (_, i) => radius[i])
    .attr("fill", (d) => d.hue);

  const spacing = Math.abs(x(domain.total / 20) - x(0));
  if (showLabels && spacing > 22) {
    const every = Math.max(1, Math.ceil(data.positive.length / 14));
    layer.append("g").selectAll("text")
      .data(all.filter((d, i) => d.hue !== "#6f4a2a" && i % every === 0))
      .join("text")
      .attr("x", (d) => x(d.x) + 7).attr("y", (d) => y(d.y) - 7)
      .attr("font-family", "ui-monospace, Menlo, monospace").attr("font-size", 10)
      .attr("fill", (d) => (d.hue === "#c9761f" ? "#8c5a1a" : "#245480"))
      .text((d) => `${d.x.toFixed(2)}, ${d.y.toFixed(2)}`);
  }

  svg.selectAll("text.caption").remove();
  svg.append("text").attr("class", "caption")
    .attr("x", 10).attr("y", 18)
    .attr("font-family", "ui-monospace, Menlo, monospace").attr("font-size", 10)
    .attr("fill", "#8c6a21")
    .text(data.caption);
}

const tripleName = () => document.getElementById("mm-triple").value;
const readTriple = () => TRIPLES[tripleName()] || TRIPLES["3,4,5"];

function turnsOf(triple) {
  const unit = stepFactor(triple, 0);
  const mirror = stepFactor(triple, 1);
  const degrees = (pair) => (Math.atan2(pair[1], pair[0]) * 180) / Math.PI;
  return {
    unit: degrees(unit),
    mirror: degrees(mirror),
    unitGrowth: Math.hypot(unit[0], unit[1]),
    mirrorGrowth: Math.hypot(mirror[0], mirror[1]),
  };
}

function render() {
  const host = document.getElementById("mm-plot");
  if (!host) return;
  const triple = readTriple();
  const steps = Number(document.getElementById("mm-steps").value);
  const lagText = document.getElementById("mm-lag-frac").value;
  const onsetText = document.getElementById("mm-damp-at-frac").value;
  const dropText = document.getElementById("mm-damp-frac").value;
  const dblueText = document.getElementById("mm-damp-blue-frac").value;
  const lagDegrees = 360 * frac(lagText);
  const fromDegrees = 360 * frac(onsetText);
  const dampPositive = Math.round(100 * frac(dropText));
  const dampNegative = Math.round(100 * frac(dblueText));

  const turns = turnsOf(triple);
  const mirror = mirrorOf(triple);

  (document.getElementById("mm-mirror-out") || {}).textContent = mirror.join(",");
  (document.getElementById("mm-steps-out") || {}).textContent = String(steps);
  (document.getElementById("mm-lag-out") || {}).textContent = `${lagText} = ${lagDegrees.toFixed(1)}°`;
  (document.getElementById("mm-damp-out") || {}).textContent = dropText;
  (document.getElementById("mm-damp-blue-out") || {}).textContent = dblueText;
  (document.getElementById("mm-damp-at-out") || {}).textContent = `${onsetText} = ${fromDegrees.toFixed(1)}°`;
  (document.getElementById("mm-turns-out") || {}).textContent =
    `${turns.unit.toFixed(1)}° then ${turns.mirror.toFixed(1)}° · growth ${turns.mirrorGrowth.toFixed(3)} on the mirror step`;

  const positive = walk(triple, steps, dampPositive, fromDegrees);
  const negative = walk([triple[0], -triple[1], triple[2]], steps, dampNegative, fromDegrees);
  const rad = (lagDegrees * Math.PI) / 180;
  const delayed = positive.map((p) => ({
    x: p.x * Math.cos(rad) - p.y * Math.sin(rad),
    y: p.x * Math.sin(rad) + p.y * Math.cos(rad),
  }));
  const sums = positive.map((p, i) => ({ x: p.x + delayed[i].x, y: p.y + delayed[i].y }));

  const reach = Math.max(1, d3.max([...positive, ...negative, ...sums],
    (d) => Math.max(Math.abs(d.x), Math.abs(d.y))));
  const caption = `${tripleName()} then ${mirror.join(",")} · ${steps} steps · lag ${lagText} · radius ${dropText}/${dblueText} from ${onsetText}`;
  const data = { positive, negative, sums, caption };

  host.innerHTML = "";
  const panel = makePanel(host);

  const sepHost = document.getElementById("mm-sep");
  if (sepHost) {
    sepHost.innerHTML = "";
    const sepPanel = makePanel(sepHost);
    const sepData = {
      positive: positive.map((p) => ({ ...p, y: Math.abs(p.y) })),
      negative: negative.map((p) => ({ ...p, y: -Math.abs(p.y) })),
      sums: [],
      caption: "separated · positive above, negative below",
    };
    draw(sepPanel, sepData, { x: [-reach, reach], y: [-reach, reach], total: reach * 2 });
  }

  const cropInput = document.getElementById("mm-crop");
  const cropOut = document.getElementById("mm-crop-out");
  const hud = document.getElementById("mm-hud");
  const fullHalf = reach * 1.05;
  const cropHalf = () => {
    const value = cropInput ? Number(cropInput.value) : 1000;
    return value >= 1000 ? fullHalf : Math.max(0.01, fullHalf * (value / 1000));
  };
  const view = { cx: 0, cy: 0, half: cropHalf() };
  const redraw = () => {
    draw(panel, data, {
      x: [view.cx - view.half, view.cx + view.half],
      y: [view.cy - view.half, view.cy + view.half],
      total: view.half * 2,
    });
    if (hud) {
      const zoom = (fullHalf / view.half).toFixed(2);
      hud.textContent = `view · x ${(view.cx - view.half).toFixed(2)} … ${(view.cx + view.half).toFixed(2)}`
        + ` · y +${(view.cy + view.half).toFixed(2)} … ${(view.cy - view.half).toFixed(2)}`
        + ` · zoom ${zoom}× · ${data.caption}`;
    }
    if (cropOut) cropOut.textContent = cropInput && Number(cropInput.value) >= 1000
      ? "all" : `±${view.half.toFixed(2)}`;
  };
  if (cropInput) cropInput.oninput = () => { view.half = cropHalf(); redraw(); };
  redraw();

  const toData = (event) => {
    const box = panel.svg.node().getBoundingClientRect();
    const fx = (event.clientX - box.left) / box.width;
    const fy = (event.clientY - box.top) / box.height;
    return {
      x: view.cx - view.half + fx * 2 * view.half,
      y: view.cy + view.half - fy * 2 * view.half,
    };
  };

  panel.svg.node().addEventListener("wheel", (event) => {
    event.preventDefault();
    const at = toData(event);
    const factor = Math.exp(event.deltaY * 0.0015);
    const nextHalf = Math.min(reach * 1.2, Math.max(reach / 500, view.half * factor));
    view.cx = at.x + (view.cx - at.x) * (nextHalf / view.half);
    view.cy = at.y + (view.cy - at.y) * (nextHalf / view.half);
    view.half = nextHalf;
    redraw();
  }, { passive: false });

  let dragging = null;
  panel.svg.node().addEventListener("pointerdown", (event) => {
    dragging = { ...toData(event), cx: view.cx, cy: view.cy };
    panel.svg.node().setPointerCapture(event.pointerId);
  });
  panel.svg.node().addEventListener("pointermove", (event) => {
    if (!dragging) return;
    const at = toData(event);
    view.cx = dragging.cx + (dragging.x - at.x);
    view.cy = dragging.cy + (dragging.y - at.y);
    redraw();
  });
  panel.svg.node().addEventListener("pointerup", () => { dragging = null; });
}

for (const id of ["mm-lag-frac", "mm-damp-frac", "mm-damp-blue-frac", "mm-damp-at-frac"]) {
  const control = document.getElementById(id);
  if (control) control.addEventListener("change", render);
}
const lagSelect = document.getElementById("mm-lag-frac");
const lagRange = document.getElementById("mm-lag-range");
if (lagSelect && lagRange) {
  lagRange.value = String(lagSelect.selectedIndex < 0 ? 0 : lagSelect.selectedIndex);
  lagRange.addEventListener("input", () => {
    lagSelect.selectedIndex = Number(lagRange.value);
    render();
  });
  lagSelect.addEventListener("change", () => { lagRange.value = String(lagSelect.selectedIndex); });
}
for (const id of ["mm-triple", "mm-steps"]) {
  const control = document.getElementById(id);
  if (control) control.addEventListener("input", render);
}
const labelButton = document.getElementById("mm-labels");
if (labelButton) {
  labelButton.setAttribute("aria-pressed", String(showLabels));
  labelButton.addEventListener("click", () => {
    showLabels = !showLabels;
    labelButton.setAttribute("aria-pressed", String(showLabels));
    labelButton.textContent = showLabels ? "labels on" : "labels off";
    render();
  });
}
render();

// --- save, rename, load ----------------------------------------------------
(() => {
  const name = document.getElementById("mm-name");
  const saved = document.getElementById("mm-saved");
  const status = document.getElementById("mm-status");
  if (!name || !saved) return;

  const settings = () => ({
    triple: tripleName(),
    mirror: mirrorOf(readTriple()).join(","),
    steps: Number(document.getElementById("mm-steps").value),
    lag: document.getElementById("mm-lag-frac").value,
    dampOrange: document.getElementById("mm-damp-frac").value,
    dampBlue: document.getElementById("mm-damp-blue-frac").value,
    onset: document.getElementById("mm-damp-at-frac").value,
  });

  const apply = (record) => {
    const s = record.settings || record;
    if (s.triple && TRIPLES[s.triple]) document.getElementById("mm-triple").value = s.triple;
    document.getElementById("mm-steps").value = s.steps || 12;
    const setSelect = (id, value) => {
      const control = document.getElementById(id);
      if (control && value != null) control.value = String(value);
    };
    setSelect("mm-lag-frac", s.lag ?? "1/12");
    setSelect("mm-damp-frac", s.dampOrange ?? "4/5");
    setSelect("mm-damp-blue-frac", s.dampBlue ?? "4/5");
    setSelect("mm-damp-at-frac", s.onset ?? "1/8");
    const range = document.getElementById("mm-lag-range");
    if (range) range.value = String(lagSelect.selectedIndex);
    render();
  };

  const refresh = async () => {
    try {
      const response = await fetch("/api/sandbox-curves");
      const out = await response.json();
      const mine = (out.curves || []).filter((curve) => curve.family === "mirrored-euler");
      saved.innerHTML = '<option value="">—</option>' +
        mine.map((curve) => `<option value="${curve.name}">${curve.name}</option>`).join("");
    } catch { /* the list is a convenience; a failed read changes nothing */ }
  };

  const post = async (record) => {
    const response = await fetch("/api/sandbox-curves", {
      method: "POST", headers: { "content-type": "application/json" },
      body: JSON.stringify({ curves: [record] }),
    });
    return response.ok;
  };

  document.getElementById("mm-save")?.addEventListener("click", async () => {
    const label = name.value.trim();
    if (!label) { status.textContent = "name it first"; return; }
    const ok = await post({ name: label, family: "mirrored-euler", settings: settings(), kind: "mirrored-euler" });
    status.textContent = ok ? `saved ${label}` : "save failed";
    if (ok) { await refresh(); saved.value = label; }
  });

  document.getElementById("mm-rename")?.addEventListener("click", async () => {
    const label = name.value.trim();
    const old = saved.value;
    if (!label || !old) { status.textContent = "pick a saved curve and type the new name"; return; }
    const ok = await post({ name: label, family: "mirrored-euler", settings: settings(), kind: "mirrored-euler" });
    if (!ok) { status.textContent = "rename failed"; return; }
    await fetch("/api/sandbox-curves", {
      method: "DELETE", headers: { "content-type": "application/json" },
      body: JSON.stringify({ name: old }),
    });
    status.textContent = `renamed ${old} → ${label}`;
    await refresh();
    saved.value = label;
  });

  document.getElementById("mm-load")?.addEventListener("click", async () => {
    const label = saved.value;
    if (!label) { status.textContent = "nothing selected"; return; }
    const response = await fetch("/api/sandbox-curves");
    const out = await response.json();
    const record = (out.curves || []).find((curve) => curve.name === label);
    if (!record) { status.textContent = "not found"; return; }
    apply(record);
    name.value = label;
    status.textContent = `loaded ${label}`;
  });

  refresh();
})();
