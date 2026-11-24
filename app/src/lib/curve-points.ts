// The points of a stored curve, for a page that must draw or cut it.
//
// The operator, 2026-11-23: the records that say "rows only" are high-degree parametric
// polynomials, not stored lines — the equation is in the record as the speed polynomials
// `speedX` and `speedY`. The plates already draw them with `PLATE.spine`, so this module reads
// the same sampler: one law for a plate and a page, never a second integrator.
//
// A record with a stored `path` uses it as it stands. A rows record is sampled: the stations are
// the equation's own values, exact there and approximate between them, which is how every plate
// already states it.

import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

export type Point = [number, number];

export type CurveLike = {
  path?: unknown;
  speedX?: unknown;
  speedY?: unknown;
  [key: string]: unknown;
};

const require = createRequire(import.meta.url);
const plateFile = fileURLToPath(new URL("../../../workbench/plate_math.js", import.meta.url));
delete require.cache[require.resolve(plateFile)];
const PLATE = require(plateFile) as {
  spine: (u: number[], v: number[], stations: number) => Array<{ x: number; y: number }>;
};

export const STATIONS = 700;

export function pointsOf(record: CurveLike | null | undefined, stations = STATIONS): Point[] | null {
  if (!record) return null;
  const path = record.path;
  if (Array.isArray(path) && path.length >= 4) {
    return path.map((p) => [Number((p as number[])[0]), Number((p as number[])[1])] as Point);
  }
  const u = record.speedX;
  const v = record.speedY;
  if (Array.isArray(u) && u.length >= 1 && Array.isArray(v) && v.length >= 1) {
    return PLATE.spine(u as number[], v as number[], stations)
      .map((sample) => [sample.x, sample.y] as Point);
  }
  return null;
}
