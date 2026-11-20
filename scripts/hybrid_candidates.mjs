// Candidates for the hybrid family, on the prime mover's exact walk.
//
//   node scripts/hybrid_candidates.mjs [triple] [stations]
//
// x = C^p, y = S^q with (C, S) the engine's exact unit-circle points. The middle-term
// polynomial P is used in 2D only: as a colour value, or as a radial scale.
//
// Writes workbench/hybrid-candidates.json for scripts/hybrid_rank.py to score.
// Powers are precomputed once per station; the arithmetic is the driver's own, all
// BigInt, so a raise to the 5th costs a few multiplications and no float.

import { writeFileSync } from "node:fs";
import path from "node:path";
import {
  unitWalk, walkFor, rational, multiply, add, rationalFloat,
} from "../app/src/scripts/prime-mover-driver.js";

const ROOT = path.resolve(import.meta.dirname, "..");
const OUT = path.join(ROOT, "workbench", "hybrid-candidates.json");

const tripleName = process.argv[2] || "7,24,25";
const COUNT = Number(process.argv[3] || 48);
const MAX_POWER = 4;

// middle-term blocks of (x+y)^n, as [coefficient, xPower, yPower]
const BLOCKS = {
  "quadratic, all": [[2, 1, 1]],
  "cubic, all": [[3, 2, 1], [3, 1, 2]],
  "quintic, central pair": [[10, 3, 2], [10, 2, 3]],
  "quintic, all four": [[5, 4, 1], [10, 3, 2], [10, 2, 3], [5, 1, 4]],
  "cubic + quintic, all": [[3, 2, 1], [3, 1, 2], [5, 4, 1], [10, 3, 2], [10, 2, 3], [5, 1, 4]],
  "every middle term": [[2, 1, 1], [3, 2, 1], [3, 1, 2], [5, 4, 1], [10, 3, 2], [10, 2, 3], [5, 1, 4]],
};

const rows = unitWalk(COUNT);
const walk = walkFor(tripleName);
const candidates = [];

// one table of powers per station: xP[i], yP[i] for i = 1..MAX_POWER
const table = rows.map((row) => {
  const C = rational(row.x, row.d);
  const S = rational(row.y, row.d);
  const xP = [rational(1n)];
  const yP = [rational(1n)];
  for (let i = 1; i <= MAX_POWER; i += 1) {
    xP.push(multiply(xP[i - 1], C));
    yP.push(multiply(yP[i - 1], S));
  }
  return { xP, yP };
});

for (let p = 1; p <= MAX_POWER; p += 1) {
  for (let q = 1; q <= MAX_POWER; q += 1) {
    // x = C^p, y = S^q, and their powers 2..4, built one multiply at a time
    const base = table.map(({ xP, yP }) => {
      const x = xP[p];
      const y = yP[q];
      const x2 = multiply(x, x);
      const y2 = multiply(y, y);
      return {
        x, y, x2, y2,
        x3: multiply(x2, x), x4: multiply(x2, x2),
        y3: multiply(y2, y), y4: multiply(y2, y2),
        base: add(x2, y2),
      };
    });

    for (const [blockName, block] of Object.entries(BLOCKS)) {
      const powerOf = (station, i, axis) => {
        const key = axis === "x" ? `x${i}` : `y${i}`;
        return station[key] || (axis === "x" ? station.x : station.y);
      };
      const P = base.map((station) => {
        let out = station.base;
        for (const [coefficient, i, j] of block) {
          out = add(out, multiply(rational(BigInt(coefficient)),
            multiply(powerOf(station, i, "x"), powerOf(station, j, "y"))));
        }
        return out;
      });

      candidates.push({
        id: `${p}-${q}|${blockName}|colour`,
        p, q, block: blockName, use: "colour",
        points: base.map(({ x, y }) => [rationalFloat(x), rationalFloat(y)]),
      });
      candidates.push({
        id: `${p}-${q}|${blockName}|radius`,
        p, q, block: blockName, use: "radius",
        points: base.map(({ x, y }, index) => {
          const f = P[index];
          return [rationalFloat(multiply(x, f)), rationalFloat(multiply(y, f))];
        }),
      });
    }
  }
}

writeFileSync(OUT, JSON.stringify({
  format: "curve-lab.hybrid-candidates/1",
  triple: tripleName,
  turn: walk.turn,
  count: COUNT,
  candidates,
}, null, 0) + "\n");
console.log(`wrote ${path.relative(ROOT, OUT)}: ${candidates.length} candidates, ` +
  `${COUNT} stations, turn ${walk.turn.toFixed(4)}°`);
