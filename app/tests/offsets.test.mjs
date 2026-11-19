// The character offsets: the rail band closes, and the -B variant differs from
// A for a curve whose stored offsets are off.

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { figureFor, svgForFigure } from "../src/lib/bordered.js";

const registry = JSON.parse(
  readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url), "utf8"),
);
const record = registry.curves.find((curve) => curve.speedX && curve.speedY);

test("the rail band closes", () => {
  const figure = figureFor({ ...record, offsets: 1 }, {}, null);
  assert.equal(figure.centralCount, 2);
  assert.ok(figure.fills.length >= 2);
  for (const band of figure.fills) {
    const first = band[0];
    const last = band[band.length - 1];
    assert.ok(Math.hypot(first[0] - last[0], first[1] - last[1]) < 1e-6);
  }
});

test("the -B variant differs from A when offsets are off", () => {
  const a = figureFor({ ...record, offsets: 0 }, {}, null);
  const b = figureFor({ ...record, offsets: 1 }, {}, null);
  assert.notEqual(svgForFigure(a, "A"), svgForFigure(b, "B"));
});
