// Draws the two hearts sandbox. The maths is in app/src/lib/hearts-emblems.js.
import {
  heartPoints, flamePoints, crossPaths, rayPaths, swordPaths, rosePaths,
  letterC, letterM,
} from "../lib/hearts-emblems.js";

const el = (id) => document.getElementById(id);

function draw() {
  const host = el("h-preview");
  const readout = el("h-readout");
  const kind = el("h-kind").value;
  const scale = Number(el("h-size").value);
  const flameSize = Number(el("h-flame").value);
  const crossHeight = Number(el("h-cross").value);
  const raysCount = Number(el("h-rays").value);
  const swordLength = Number(el("h-sword").value);
  const swordAngle = Number(el("h-angle").value);
  const rosesCount = Number(el("h-roses").value);
  el("h-size-out").textContent = scale.toFixed(2);
  el("h-flame-out").textContent = flameSize.toFixed(2);
  el("h-cross-out").textContent = crossHeight.toFixed(2);
  el("h-rays-out").textContent = String(raysCount);
  el("h-sword-out").textContent = swordLength.toFixed(2);
  el("h-angle-out").textContent = `${swordAngle}°`;
  el("h-roses-out").textContent = String(rosesCount);

  const heart = heartPoints(400).map((p) => ({ x: p.x * scale, y: p.y * scale }));
  // the heart's own top notch is at y ≈ 0.7; the flame and cross rise from there
  const topY = Math.max(...heart.map((p) => p.y));
  const sacred = kind === "sacred";
  const flame = sacred && flameSize > 0.01
    ? flamePoints(flameSize * scale).map((p) => ({ x: p.x * scale, y: p.y * scale + topY * 0.92 }))
    : [];
  const flameTop = flame.length ? Math.max(...flame.map((p) => p.y)) : topY * 0.92;
  const cross = sacred && crossHeight > 0.01
    ? crossPaths(crossHeight * scale, 0.18 * scale).map((line) =>
      line.map((p) => ({ x: p.x * scale, y: p.y * scale + flameTop })))
    : [];
  const rays = raysCount > 0
    ? rayPaths(raysCount, 0.95 * scale, 1.35 * scale, { x: 0, y: 0.05 * scale })
    : [];
  const sword = kind === "immaculate" && swordLength > 0.01
    ? swordPaths(swordAngle, swordLength * scale).map((line) =>
      line.map((p) => ({ x: p.x * scale, y: p.y * scale })))
    : [];
  const roses = kind === "immaculate" ? Array.from({ length: rosesCount }, (_, i) => {
    const a = (Math.PI * (i + 0.5)) / Math.max(1, rosesCount) + Math.PI * 0.55;
    const c = { x: 0.62 * scale * Math.cos(a), y: -0.75 * scale + 0.12 * scale * Math.sin(a) };
    return rosePaths(0.065 * scale, c);
  }) : [];

  // the letter under the heart: C for the Sacred Heart, M for the Immaculate Heart
  const bottomY = Math.min(...heart.map((p) => p.y));
  const letterSize = 0.5 * scale;
  const letter = kind === "sacred"
    ? letterC(letterSize, { x: 0, y: bottomY - letterSize * 0.75 })
    : letterM(letterSize, { x: 0, y: bottomY - letterSize * 0.75 });

  const all = [heart, flame, ...cross, ...rays.flat(), ...sword.flat(),
    ...roses.flatMap((r) => [r.ring, ...r.petals]), ...letter];
  const pts = all.flat();
  const xs = pts.map((p) => p.x), ys = pts.map((p) => p.y);
  const x0 = Math.min(...xs), x1 = Math.max(...xs);
  const y0 = Math.min(...ys), y1 = Math.max(...ys);
  const w = 640, h = 560, margin = 28;
  const k = Math.min((w - 2 * margin) / (x1 - x0 || 1), (h - 2 * margin) / (y1 - y0 || 1));
  const ox = (w - (x1 - x0) * k) / 2, oy = (h - (y1 - y0) * k) / 2;
  const put = (p) => [ox + (p.x - x0) * k, h - (oy + (p.y - y0) * k)];
  const line = (ptsIn, colour, width) => ptsIn.length < 2 ? "" : '<path d="M ' +
    ptsIn.map((p) => put(p).map((v) => v.toFixed(1)).join(" ")).join(" L ") +
    `" fill="none" stroke="${colour}" stroke-width="${width}" stroke-linecap="round" stroke-linejoin="round"/>`;

  host.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}">
    <rect width="${w}" height="${h}" fill="#fff"/>
    ${rays.map((r) => line(r, "#d8b45a", 1.6)).join("")}
    ${line([...heart, heart[0]], "#2b2b2b", 2.6)}
    ${flame.length ? line([...flame, flame[0]], "#b06a1f", 2.0) : ""}
    ${cross.map((c) => line(c, "#2b2b2b", 1.8)).join("")}
    ${sword.map((s) => line(s, "#4a4a4a", 1.8)).join("")}
    ${roses.map((r) => line([...r.ring, r.ring[0]], "#a06a2c", 1.2)).join("")}
    ${roses.map((r) => r.petals.map((pt) => line(pt, "#a06a2c", 1.0)).join("")).join("")}
    ${letter.map((l) => line(l, "#2b2b2b", 2.2)).join("")}
    <text x="12" y="20" font-family="ui-monospace, Menlo, monospace" font-size="12" fill="#8a7a62">
      ${kind === "sacred" ? "Sacred Heart" : "Immaculate Heart"} · heart ×${scale.toFixed(2)} · flame ${flameSize.toFixed(2)} · cross ${crossHeight.toFixed(2)} · rays ${raysCount}</text>
    <text x="12" y="${h - 10}" font-family="ui-monospace, Menlo, monospace" font-size="12" fill="#5a4a36">
      heart sampled (not rational) · emblems built from curves</text>
  </svg>`;

  readout.innerHTML = kind === "sacred"
    ? "Sacred Heart: the flame rises from the notch, the cross stands on the flame, and the " +
      "rays alternate long and short. 16 rays is the traditional count."
    : "Immaculate Heart: one sword pierces the heart, the roses sit at the foot, and the rays " +
      "are the same. The traditional sword is vertical; move the angle for the tilt you want.";
}

function mount() {
  for (const id of ["h-kind", "h-size", "h-flame", "h-cross", "h-rays", "h-sword", "h-angle", "h-roses"]) {
    el(id)?.addEventListener("input", draw);
    el(id)?.addEventListener("change", draw);
  }
  draw();
}

if (typeof document !== "undefined") {
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mount);
  else mount();
}
