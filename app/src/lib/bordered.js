// The illuminations: every curve in the registry, bordered by a curve.
//
// The inner curve has its own spec, stored by uid in workbench/curve-notes.json:
//
//   rotation    degrees, usually a multiple of 90; applied to the inner only
//   pieces      1, 2 or 4; 2 adds a vertical mirror, 4 adds the horizontal too
//   border_uid  the curve used for the border, when it is not the same one
//
// The frame rule is the lab's: the side is n x the motif, so n copies fill each
// edge. 9 by default, 5 for the curves whose loops make a wide border. The
// border's share of the figure is measured and printed, so a wide one is seen.

import { statSync } from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { loadRegistry } from "./registry.js";

const require = createRequire(import.meta.url);
const P = require("../../../workbench/plate_math.js");

const SIZE = 900;
const PAD = 0.04;
const PER_SIDE = 9;
const PER_SIDE_FIVE = new Set(["c-0007", "c-0002"]);
const TOO_WIDE = 30;

function pointsOf(record) {
  if (record.path) return record.path;
  return P.spine(record.speedX, record.speedY, 400).map((s) => [s.x, s.y]);
}

function rotatePoints(points, degrees) {
  const turn = (((Number(degrees) || 0) % 360) + 360) % 360;
  if (!turn) return points.map(([x, y]) => [x, y]);
  const exact = [90, 180, 270].includes(turn);
  const a = turn * Math.PI / 180;
  const c = exact ? Math.round(Math.cos(a)) : Math.cos(a);
  const s = exact ? Math.round(Math.sin(a)) : Math.sin(a);
  return points.map(([x, y]) => [x * c - y * s, x * s + y * c]);
}

function mirroredPieces(points, pieces) {
  const box = P.bbox(points);
  const cx = (box[0] + box[2]) / 2;
  const cy = (box[1] + box[3]) / 2;
  const out = [points];
  if (pieces >= 2) out.push(points.map(([x, y]) => [2 * cx - x, y]));
  if (pieces >= 4) {
    out.push(points.map(([x, y]) => [x, 2 * cy - y]));
    out.push(points.map(([x, y]) => [2 * cx - x, 2 * cy - y]));
  }
  return out;
}

function scaleAbout(points, factor) {
  return points.map(([x, y]) => [x * factor, y * factor]);
}

function moveToCentre(points, cx, cy) {
  const box = P.bbox(points);
  return points.map(([x, y]) => [x - (box[0] + box[2]) / 2 + cx, y - (box[1] + box[3]) / 2 + cy]);
}

function frameBorder(record, perSide) {
  if (record.path) {
    const xs = record.path.map((p) => p[0]);
    const ys = record.path.map((p) => p[1]);
    const unit = Math.max(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys)) || 1;
    const side = perSide * unit;
    const turn = (pts, deg) => {
      const a = deg * Math.PI / 180;
      return pts.map(([x, y]) => [x * Math.cos(a) - y * Math.sin(a), x * Math.sin(a) + y * Math.cos(a)]);
    };
    const border = [];
    [[0, 0, 0], [side, 0, 90], [side, side, 180], [0, side, 270]].forEach(([ox, oy, deg]) => {
      for (let copy = 0; copy < perSide; copy += 1) {
        const moved = record.path.map(([x, y]) => [x + copy * unit, y]);
        border.push(turn(moved, deg).map(([x, y]) => [x + ox, y + oy]));
      }
    });
    return border;
  }
  const a = P.group(record);
  return P.frame(a, null, perSide, perSide, 45, "a", false).flatMap((item) => item.paths);
}

function marginPercent(border, central) {
  const fbox = P.bbox(border.flat());
  const cbox = P.bbox(central.flat());
  const margin = Math.min(cbox[0] - fbox[0], fbox[2] - cbox[2],
                          cbox[1] - fbox[1], fbox[3] - cbox[3]);
  const size = Math.max(fbox[2] - fbox[0], fbox[3] - fbox[1]) || 1;
  return Math.max(0, Math.round((margin / size) * 100));
}

export function figureFor(record, all, borderRecord) {
  const perSide = PER_SIDE_FIVE.has(record.uid) ? 5 : PER_SIDE;
  const rotation = Number(record.rotation) || 0;
  const pieces = [1, 2, 4].includes(Number(record.pieces)) ? Number(record.pieces) : 1;
  try {
    const border = frameBorder(borderRecord || record, perSide);
    const fbox = P.bbox(border.flat());
    const unit = Math.max(fbox[2] - fbox[0], fbox[3] - fbox[1]) / perSide || 1;
    let inner = rotatePoints(pointsOf(record), rotation);
    const ibox = P.bbox(inner);
    const size = Math.max(ibox[2] - ibox[0], ibox[3] - ibox[1]) || 1;
    inner = scaleAbout(inner, unit / size);
    const central = mirroredPieces(inner, pieces)
      .map((line) => moveToCentre(line, (fbox[0] + fbox[2]) / 2, (fbox[1] + fbox[3]) / 2));
    const margin = marginPercent(border, central);
    return {
      paths: [...central, ...border],
      perSide,
      margin,
      rotation,
      pieces,
      failed: false,
      tooWide: margin >= TOO_WIDE,
    };
  } catch (error) {
    return {
      paths: [pointsOf(record)], perSide, margin: 0, rotation, pieces,
      failed: true, reason: String(error.message || error),
    };
  }
}

function svgFrom(paths, label) {
  const all = paths.flat();
  const xs = all.map((p) => p[0]);
  const ys = all.map((p) => p[1]);
  const x0 = Math.min(...xs), x1 = Math.max(...xs);
  const y0 = Math.min(...ys), y1 = Math.max(...ys);
  const w = x1 - x0 || 1, h = y1 - y0 || 1;
  const inner = SIZE * (1 - 2 * PAD);
  const k = inner / Math.max(w, h);
  const ox = (SIZE - w * k) / 2 - x0 * k;
  const oy = (SIZE + h * k) / 2 + y0 * k;
  const lines = paths.map((points) => {
    const step = Math.max(1, Math.floor(points.length / 300));
    const kept = points.filter((_, i) => i % step === 0 || i === points.length - 1);
    return `<polyline points="${kept.map(([x, y]) =>
      `${(x * k + ox).toFixed(1)},${(oy - y * k).toFixed(1)}`).join(" ")}"` +
      ' fill="none" stroke="#111" stroke-width="1.1" stroke-linejoin="round"/>';
  });
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${SIZE} ${SIZE}" width="${SIZE}" height="${SIZE}" role="img" aria-label="${label}">` +
    `<rect width="${SIZE}" height="${SIZE}" fill="#fff"/>${lines.join("")}</svg>`;
}

export function svgForFigure(figure, label) {
  return svgFrom(figure.paths, label);
}

export function svgForRecord(record, all = {}) {
  return svgForFigure(figureFor(record, all), `${record.uid}: ${record.name}`);
}

export function plainSvgForRecord(record) {
  return svgFrom([pointsOf(record)], `${record.uid}: ${record.name}`);
}

let cache = null;

export function clearIlluminateCache() {
  cache = null;
}

// The build is memoised: 238 figures is about a second of work, and the page
// and its figure route must not each pay it. The stamp is the two data files'
// mtimes, so an edit to the registry or the notes rebuilds on the next request
// instead of serving yesterday's borders.
function dataStamp(base) {
  return ["workbench/curve-registry.json", "workbench/curve-notes.json"]
    .map((file) => {
      try { return statSync(path.join(base, file)).mtimeMs; } catch { return 0; }
    })
    .join(":");
}

export async function buildIlluminations(root) {
  const base = root || path.resolve(process.cwd(), "..");
  const stamp = dataStamp(base);
  if (cache && cache.base === base && cache.stamp === stamp) return cache;
  const registry = (await loadRegistry(base)).curves;
  const rows = Object.fromEntries(registry.map((record) => [record.name, record]));
  const byUid = Object.fromEntries(registry.map((record) => [record.uid, record]));
  const byList = (name) => registry.filter((record) => record.lists.includes(name));
  const byWeight = (a, b) => (b.importance || 0) - (a.importance || 0);

  const sections = [
    { title: "Fig. 1–50 · found", records: byList("found").slice(0, 50) },
    // Only the finder curves that were actually picked: starred or rated.
    // Unstarred finder rows are the candidate pool, not the collection.
    { title: "Finder · picked", records: byList("finder").filter((r) => r.starred || (r.importance || 0) > 0) },
    { title: "Roses", records: registry.filter((r) => r.family_id === "rose" && !r.name.includes("k-4")) },
    { title: "B | solve, save, take away", records: byList("B") },
  ];

  let n = 0;
  const built = sections.map((section) => ({
    title: section.title,
    items: section.records.slice().sort(byWeight).map((record) => {
      n += 1;
      const border = record.border_uid ? byUid[record.border_uid] : null;
      const figure = figureFor(record, rows, border);
      return {
        n,
        uid: record.uid,
        name: record.name,
        id: `fig-${n}`,
        svg: svgFrom(figure.paths, `Fig. ${n}: ${record.name}`),
        perSide: figure.perSide,
        marginPercent: figure.margin,
        rotation: figure.rotation,
        pieces: figure.pieces,
        importance: record.importance || 0,
        tooWide: figure.tooWide,
        failed: figure.failed,
      };
    }),
  }));
  cache = {
    total: n,
    sections: built,
    base,
    stamp,
    byId: Object.fromEntries(built.flatMap((section) => section.items.map((item) => [item.id, item]))),
  };
  return cache;
}
