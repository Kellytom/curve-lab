// The curve finder's first results, read from workbench/finder.json.
//
// The page displays; the Python script computes. No maths happens here.

import { existsSync, readFileSync } from "node:fs";
import { fileHash, readFinderStars } from "./finder-stars.js";
import path from "node:path";
import { repoRoot } from "./gallery.js";

export function finderData(root) {
  const base = repoRoot(root);
  const file = path.join(base, "workbench", "finder.json");
  const { curves: starred, source } = readFinderStars(base);
  const starsFile = path.join(base, "workbench", "finder-stars.json");
  const baseHash = existsSync(starsFile) ? fileHash(readFileSync(starsFile, "utf8")) : "";
  if (!existsSync(file)) return { format: null, curves: [], starred, starSource: source, baseHash, missing: file };
  const data = JSON.parse(readFileSync(file, "utf8"));
  return { ...data, curves: Array.isArray(data.curves) ? data.curves : [], starred, starSource: source, baseHash };
}

// A polyline in pixel space, from the sampled points, with a small margin.
export function svgPath(points, size = 160, margin = 8) {
  if (!points || !points.length) return { d: "", viewBox: `0 0 ${size} ${size}` };
  const xs = points.map((p) => p[0]);
  const ys = points.map((p) => p[1]);
  const [x0, x1, y0, y1] = [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)];
  const w = x1 - x0 || 1, h = y1 - y0 || 1;
  const k = (size - 2 * margin) / Math.max(w, h);
  const ox = (size - w * k) / 2, oy = (size - h * k) / 2;
  const d = points.map(([x, y], i) =>
    `${i ? "L" : "M"}${(ox + (x - x0) * k).toFixed(2)},${(size - (oy + (y - y0) * k)).toFixed(2)}`
  ).join("");
  return { d, viewBox: `0 0 ${size} ${size}` };
}
