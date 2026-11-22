// Turn a range so the blue start dot sits on a named bearing.
//
//   node scripts/set_bearings.mjs c-0273:c-0328=N c-0091:c-0093=NE
//
// The bearing is the direction from the drawing's centre (the bounding-box centre after the
// turn) to the start point, measured from north (+y) toward east (+x): N 0, NE 45, E 90,
// SE 135, S 180, SW 225, W 270, NW 315. That definition always has a solution; "the start is
// the topmost point" does not, because a concave start can never be the extreme point.
import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import P from "../workbench/plate_math.js";

const ROOT = path.resolve(import.meta.dirname, "..");
const REGISTRY = path.join(ROOT, "workbench", "curve-registry.json");
const BEARING = { N: 0, NE: 45, E: 90, SE: 135, S: 180, SW: 225, W: 270, NW: 315 };

const spineOf = (record) => {
  if (Array.isArray(record.path) && record.path.length > 2) return record.path;
  if (Array.isArray(record.speedX) && record.speedX.length) {
    return P.spine(record.speedX, record.speedY, 400).map((s) => [s.x, s.y]);
  }
  return [];
};

const rotate = (points, degrees) => {
  const a = (-degrees * Math.PI) / 180;
  const c = Math.cos(a), s = Math.sin(a);
  return points.map(([x, y]) => [x * c - y * s, x * s + y * c]);
};

const wrap = (degrees) => {
  let d = ((degrees + 180) % 360 + 360) % 360 - 180;
  if (d === -180) d = 180;
  return d;
};

// The bearing from the curve's own centre of mass to its start. The centroid rotates with
// the curve, so the bearing moves with the turn by a known amount: bearing + degrees.
const bearingAt = (points) => {
  const n = points.length;
  const centre = [points.reduce((s, p) => s + p[0], 0) / n, points.reduce((s, p) => s + p[1], 0) / n];
  const v = [points[0][0] - centre[0], points[0][1] - centre[1]];
  if (Math.hypot(...v) < 1e-9) return null;
  return (Math.atan2(v[0], v[1]) * 180) / Math.PI;
};

const solve = (points, fromDegrees, target) => {
  const current = bearingAt(points);
  if (current === null) return null;
  return Number(wrap(target - current).toFixed(2));
};

const plans = process.argv.slice(2).map((spec) => {
  const [range, name] = spec.split("=");
  const [start, end] = range.split(":");
  if (!(name in BEARING)) throw new Error(`no bearing named ${name}`);
  return { start, end, target: BEARING[name], name };
});

const registry = JSON.parse(readFileSync(REGISTRY, "utf8"));
const changed = [];
for (const record of registry.curves) {
  const plan = plans.find((p) => p.start <= record.uid && record.uid <= p.end);
  if (!plan) continue;
  const points = spineOf(record);
  if (points.length < 3) continue;
  const before = Number(record.transform?.degrees || 0);
  const after = solve(points, before, plan.target);
  if (after === null) {
    console.log(`${record.uid}  skipped: the start point sits on the centre`);
    continue;
  }
  if (Math.abs(after - before) < 0.02) continue;
  const radians = (after * Math.PI) / 180;
  record.transform = {
    degrees: after,
    matrix: [
      [Number(Math.cos(radians).toFixed(6)), Number((-Math.sin(radians)).toFixed(6))],
      [Number(Math.sin(radians).toFixed(6)), Number(Math.cos(radians).toFixed(6))],
    ],
    exact: Math.abs((((after % 90) + 90) % 90)) < 1e-6,
  };
  changed.push({ uid: record.uid, before, after, target: plan.name });
}
if (!changed.length) {
  console.log("nothing to change");
} else {
  writeFileSync(REGISTRY, `${JSON.stringify(registry, null, 2)}\n`);
  for (const row of changed) {
    console.log(`${row.uid}  ${String(row.before).padStart(8)}° -> ${String(row.after).padStart(8)}°  (dot at ${row.target})`);
  }
  console.log(`${changed.length} curve(s) turned`);
}
