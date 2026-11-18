// The illuminations: every picked curve, bordered by the same curve three times
// a side. One number per curve, assigned here so the page and the file names
// cannot disagree.
//
// The maths is the lab's (workbench/plate_math.js), required rather than copied.

import { readFileSync } from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const P = require("../../../workbench/plate_math.js");

const SIZE = 900;
const PER_SIDE = 3;
const PAD = 0.04;

function readJson(file) {
  return JSON.parse(readFileSync(file, "utf8"));
}

function mapPaths(paths, size = SIZE) {
  const all = paths.flat();
  if (!all.length) return [];
  const xs = all.map((p) => p[0]);
  const ys = all.map((p) => p[1]);
  const x0 = Math.min(...xs), x1 = Math.max(...xs);
  const y0 = Math.min(...ys), y1 = Math.max(...ys);
  const w = x1 - x0 || 1, h = y1 - y0 || 1;
  const inner = size * (1 - 2 * PAD);
  const k = inner / Math.max(w, h);
  const ox = (size - w * k) / 2 - x0 * k;
  const oy = (size + h * k) / 2 + y0 * k;
  return paths.map((points) => points.map(([x, y]) => [x * k + ox, oy - y * k]));
}

function svgFrom(paths) {
  const lines = mapPaths(paths).map((points) => {
    const step = Math.max(1, Math.floor(points.length / 150));
    const kept = points.filter((_, i) => i % step === 0 || i === points.length - 1);
    return `<polyline points="${kept.map((p) => p.map((v) => Math.round(v)).join(",")).join(" ")}"` +
      ' fill="none" stroke="#111" stroke-width="1.1" stroke-linejoin="round"/>';
  });
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${SIZE} ${SIZE}" width="${SIZE}" height="${SIZE}">` +
    `<rect width="${SIZE}" height="${SIZE}" fill="#fff"/>${lines.join("")}</svg>`;
}

// The frame rule for a drawing: the motif is the whole drawing, and n copies
// fill each edge of a square whose side is n x the motif's long side.
function frameSet(paths, perSide = PER_SIDE) {
  const all = paths.flat();
  const xs = all.map((p) => p[0]);
  const ys = all.map((p) => p[1]);
  const w = Math.max(...xs) - Math.min(...xs) || 1;
  const h = Math.max(...ys) - Math.min(...ys) || 1;
  const unit = Math.max(w, h);
  const side = perSide * unit;
  const turn = (pts, deg) => {
    const a = deg * Math.PI / 180;
    return pts.map(([x, y]) => [x * Math.cos(a) - y * Math.sin(a), x * Math.sin(a) + y * Math.cos(a)]);
  };
  const out = [];
  [[0, 0, 0], [side, 0, 90], [side, side, 180], [0, side, 270]].forEach(([ox, oy, deg]) => {
    for (let copy = 0; copy < perSide; copy += 1) {
      paths.forEach((points) => {
        const moved = points.map(([x, y]) => [x + copy * unit, y]);
        out.push(turn(moved, deg).map(([x, y]) => [x + ox, y + oy]));
      });
    }
  });
  const bx = out.flat().map((p) => p[0]);
  const by = out.flat().map((p) => p[1]);
  const cx = (Math.min(...bx) + Math.max(...bx)) / 2;
  const cy = (Math.min(...by) + Math.max(...by)) / 2;
  paths.forEach((points) => out.push(points.map(([x, y]) => [x + cx, y + cy])));
  return out;
}

function pathsFor(curve, rows) {
  if (curve.paths) return frameSet(curve.paths);
  if (curve.path) return frameSet([curve.path]);
  rows[curve.name] = rows[curve.name] || curve;
  return P.design({
    curve: curve.name,
    form: "arch",
    leg: 45,
    pattern: "a",
    frame: { perWidth: PER_SIDE, perHeight: PER_SIDE },
  }, rows).paths;
}

let cache = null;

export function buildIlluminations(root) {
  if (cache) return cache;
  const base = root || path.resolve(process.cwd(), "..");
  const lab = readJson(path.join(base, "workbench", "real-curves.json"));
  const rows = Object.fromEntries(lab.curves.map((curve) => [curve.name, curve]));
  const finder = readJson(path.join(base, "workbench", "finder.json")).curves;
  const saved = readJson(path.join(base, "workbench", "operator-list.json")).saved;
  const roses = finder.filter((curve) => curve.family === "roses-rational" && curve.name !== "rose k=4, a=1 b=1");

  const sections = [
    { title: "Fig. 1–50 · found", items: lab.curves.filter((c) => c.source === "found").slice(0, 50) },
    { title: "Fig. 51–59 · finder", items: finder.slice(0, 9) },
    { title: "Roses", items: roses },
    { title: "B | solve, save, take away", items: saved },
  ];

  let n = 0;
  const built = sections.map((section) => ({
    title: section.title,
    items: section.items.map((curve) => {
      n += 1;
      const slug = String(curve.name || `curve-${n}`).toLowerCase()
        .replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
      return { n, name: curve.name, slug, id: `fig-${n}`, svg: svgFrom(pathsFor(curve, rows)) };
    }),
  }));
  cache = { total: n, sections: built };
  return cache;
}
