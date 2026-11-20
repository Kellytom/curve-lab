// The prime mover, with D3 and a semantic zoom: zooming re-renders the curve at
// a new domain, so dots, lines and grid stay at readable pixel sizes instead of
// being scaled into blobs. The lattice is redrawn with the spacing that fits.
import * as d3 from "d3";

const frac = (text) => {
  const [p, q] = String(text).split("/").map(Number);
  return q ? p / q : 0;
};
// Only p-triples: (x, y, z) with x² + y² = z². The step is (x/z, y/z), whose
// length is exactly 1, so a walk stays on the circle and every position is a
// ratio of whole numbers. A step like 2 + i is refused, because its length is
// not a ratio and that length would ride along in every position afterwards.
const TRIPLES = {
  "3,4,5": [3, 4, 5],
  "7,24,25": [7, 24, 25],
  "5,12,13": [5, 12, 13],
  "8,15,17": [8, 15, 17],
};
// The labels are a reading aid, not part of the data: one button toggles them.
let showLabels = true;
const SIZE = 640;

function walk(triple, steps, netPercent = 100, fromDegrees = 0, limit = 4000) {
  const points = [];
  let z = [1, 0];
  const [legX, legY, hypotenuse] = triple;
  const factor = [legX / hypotenuse, legY / hypotenuse];
  const stepDegrees = (Math.atan2(factor[1], factor[0]) * 180) / Math.PI;
  // every step keeps the length, so the damper is simply the net radius a step
  const dampAfter = netPercent / 100;
  let turned = 0;
  for (let step = 0; step < steps; step += 1) {
    points.push({ x: z[0], y: z[1], step, turned });
    const now = turned >= fromDegrees ? dampAfter : 1;
    z = [(z[0] * factor[0] - z[1] * factor[1]) * now,
         (z[0] * factor[1] + z[1] * factor[0]) * now];
    turned += Math.abs(stepDegrees);
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

  // Grid: chosen so a cell is at least ~26 px on screen, subdivided as you zoom.
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

  // Dots: a fixed screen radius, smaller only where two dots would touch.
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

  // Labels only when there is room: a station every ~34 px, rounded.
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

function render() {
  const host = document.getElementById("pm-plot");
  if (!host) return;
  const triple = TRIPLES[document.getElementById("pm-factor").value] || TRIPLES["3,4,5"];
  const steps = Number(document.getElementById("pm-steps").value);
  // The inputs are fractions of a turn — the lattice's own language. Degrees are
  // a readout, never an entry.
  const lagText = document.getElementById("pm-lag-frac").value;
  const onsetText = document.getElementById("pm-damp-at-frac").value;
  const dropText = document.getElementById("pm-damp-frac").value;
  const dblueText = document.getElementById("pm-damp-blue-frac").value;
  const lagDegrees = 360 * frac(lagText);
  const fromDegrees = 360 * frac(onsetText);
  const dampPositive = Math.round(100 * frac(dropText));
  const dampNegative = Math.round(100 * frac(dblueText));

  (document.getElementById("pm-steps-out") || {}).textContent = String(steps);
  (document.getElementById("pm-lag-out") || {}).textContent = `${lagText} = ${lagDegrees.toFixed(1)}°`;
  (document.getElementById("pm-damp-out") || {}).textContent = dropText;
  (document.getElementById("pm-damp-blue-out") || {}).textContent = dblueText;
  (document.getElementById("pm-damp-at-out") || {}).textContent = `${onsetText} = ${fromDegrees.toFixed(1)}°`;

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
  const caption = `${document.getElementById("pm-factor").value} · ${steps} steps · lag ${lagDegrees}° · radius ${dampPositive}/${dampNegative}% from ${fromDegrees}°`;
  const data = { positive, negative, sums, caption };

  host.innerHTML = "";
  const panel = makePanel(host);

  // The separated panel: positive above the axis, negative mirrored below, the
  // sum left out so the two walks can be read on their own.
  const sepHost = document.getElementById("pm-sep");
  let sepPanel = null;
  if (sepHost) {
    sepHost.innerHTML = "";
    sepPanel = makePanel(sepHost);
    const sepData = {
      positive: positive.map((p) => ({ ...p, y: Math.abs(p.y) })),
      negative: negative.map((p) => ({ ...p, y: -Math.abs(p.y) })),
      sums: [],
      caption: "separated · positive above, negative below",
    };
    draw(sepPanel, sepData, { x: [-reach, reach], y: [-reach, reach], total: reach * 2 });
  }

  // The zoom is a window in data units: centre and half-width. Nothing is
  // transformed; the drawing is redrawn for the new window, so dots stay ~4 px,
  // lines stay ~2 px and the grid re-chooses its own spacing.
  const cropInput = document.getElementById("pm-crop");
  const cropOut = document.getElementById("pm-crop-out");
  const hud = document.getElementById("pm-hud");
  const fullHalf = reach * 1.05;
  const cropHalf = () => {
    const value = cropInput ? Number(cropInput.value) : 1000;
    // the slider runs 0..1000: 1000 is the full view, 0.5 at the bottom
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
  if (cropInput) cropInput.addEventListener("input", () => { view.half = cropHalf(); redraw(); });
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
    // keep the point under the pointer still
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

for (const id of ["pm-lag-frac", "pm-damp-frac", "pm-damp-blue-frac", "pm-damp-at-frac"]) {
  const control = document.getElementById(id);
  if (control) control.addEventListener("change", render);
}
// the lag slider walks the ruler's stops, one per fraction
const lagSelect = document.getElementById("pm-lag-frac");
const lagRange = document.getElementById("pm-lag-range");
if (lagSelect && lagRange) {
  lagRange.value = String(lagSelect.selectedIndex < 0 ? 0 : lagSelect.selectedIndex);
  lagRange.addEventListener("input", () => {
    lagSelect.selectedIndex = Number(lagRange.value);
    render();
  });
  lagSelect.addEventListener("change", () => { lagRange.value = String(lagSelect.selectedIndex); });
}
for (const id of ["pm-factor", "pm-steps"]) {
  const control = document.getElementById(id);
  if (control) control.addEventListener("input", render);
}
const labelButton = document.getElementById("pm-labels");
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
// The record is the builder's own settings, stored through the sandbox-curves
// endpoint (SQLite through Prisma). Rename writes the new name and deletes the
// old one, so a curve has one row, not two.
(() => {
  const name = document.getElementById("pm-name");
  const saved = document.getElementById("pm-saved");
  const status = document.getElementById("pm-status");
  if (!name || !saved) return;

  const settings = () => ({
    factor: document.getElementById("pm-factor").value,
    steps: Number(document.getElementById("pm-steps").value),
    lag: Number(document.getElementById("pm-lag").value),
    dampOrange: Number(document.getElementById("pm-damp").value),
    dampBlue: Number(document.getElementById("pm-damp-blue").value),
    onset: Number(document.getElementById("pm-damp-at").value),
  });

  const apply = (record) => {
    const s = record.settings || record;
    document.getElementById("pm-factor").value = TRIPLES[s.factor] ? s.factor : "3,4,5";
    document.getElementById("pm-steps").value = s.steps || 12;
    document.getElementById("pm-lag").value = s.lag ?? 27;
    document.getElementById("pm-lag-range").value = s.lag ?? 27;
    document.getElementById("pm-damp").value = s.dampOrange ?? 80;
    document.getElementById("pm-damp-range").value = s.dampOrange ?? 80;
    document.getElementById("pm-damp-blue").value = s.dampBlue ?? 80;
    document.getElementById("pm-damp-blue-range").value = s.dampBlue ?? 80;
    document.getElementById("pm-damp-at").value = s.onset ?? 45;
    document.getElementById("pm-damp-at-range").value = s.onset ?? 45;
    render();
  };

  const refresh = async () => {
    try {
      const response = await fetch("/api/sandbox-curves");
      const out = await response.json();
      const mine = (out.curves || []).filter((curve) => curve.family === "prime-mover");
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

  document.getElementById("pm-save")?.addEventListener("click", async () => {
    const label = name.value.trim();
    if (!label) { status.textContent = "name it first"; return; }
    const ok = await post({ name: label, family: "prime-mover", settings: settings(), kind: "prime-mover" });
    status.textContent = ok ? `saved ${label}` : "save failed";
    if (ok) { await refresh(); saved.value = label; }
  });

  document.getElementById("pm-rename")?.addEventListener("click", async () => {
    const label = name.value.trim();
    const old = saved.value;
    if (!label || !old) { status.textContent = "pick a saved curve and type the new name"; return; }
    const ok = await post({ name: label, family: "prime-mover", settings: settings(), kind: "prime-mover" });
    if (!ok) { status.textContent = "rename failed"; return; }
    await fetch("/api/sandbox-curves", {
      method: "DELETE", headers: { "content-type": "application/json" },
      body: JSON.stringify({ name: old }),
    });
    status.textContent = `renamed ${old} → ${label}`;
    await refresh();
    saved.value = label;
  });

  document.getElementById("pm-load")?.addEventListener("click", async () => {
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
