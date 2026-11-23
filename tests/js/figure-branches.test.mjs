import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { figureFor } from "../../app/src/lib/bordered.js";

// The figures page draws each record inside its border. c-0416's four arms were read as
// "spine + two rails" (four paths look like an offset group) and the figure filled the jump
// between the arms as one blob. The figure now asks `branchesOf` and draws each arm whole.

const registry = JSON.parse(readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url)));
const byUid = new Map(registry.curves.map((row) => [row.uid, row]));

const longestStep = (points) => {
  let worst = 0;
  for (let i = 1; i < points.length; i += 1) {
    worst = Math.max(worst, Math.hypot(points[i][0] - points[i - 1][0], points[i][1] - points[i - 1][1]));
  }
  return worst;
};

test("c-0416's figure draws four arms and no chord between them", () => {
  const figure = figureFor(byUid.get("c-0416"));
  assert.equal(figure.failed, false, figure.reason);
  assert.equal(figure.centralCount, 4, "one central path per arm");
  const central = figure.paths.slice(0, figure.centralCount);
  const xs = central.flat().map((p) => p[0]), ys = central.flat().map((p) => p[1]);
  const size = Math.hypot(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys)) || 1;
  for (const arm of central) {
    assert.ok(longestStep(arm) < 0.25 * size,
      `an arm carries a step of ${(longestStep(arm) / size).toFixed(2)} of the figure`);
  }
});

test("the four arms sit apart, not piled on one point", () => {
  const figure = figureFor(byUid.get("c-0416"));
  const centres = figure.paths.slice(0, figure.centralCount).map((arm) => {
    const xs = arm.map((p) => p[0]), ys = arm.map((p) => p[1]);
    return `${((Math.min(...xs) + Math.max(...xs)) / 2).toFixed(3)},` +
      `${((Math.min(...ys) + Math.max(...ys)) / 2).toFixed(3)}`;
  });
  assert.equal(new Set(centres).size, 4, `centres: ${centres.join(" ")}`);
});

test("the astroid keeps its two halves as two paths", () => {
  const figure = figureFor(byUid.get("c-0402"));
  assert.equal(figure.centralCount, 2);
});

test("a single-path record still gets the leaf figure, as before", () => {
  // no branches, not an offset group: the leaf (one half mirrored) is unchanged
  const figure = figureFor(byUid.get("c-0418"));
  assert.equal(figure.centralCount, 2, "the leaf is its half and its mirror");
  assert.ok(figure.fills.length >= 1, "the leaf still fills");
});
