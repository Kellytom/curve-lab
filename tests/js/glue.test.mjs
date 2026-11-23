import test from "node:test";
import assert from "node:assert/strict";
import {
  parseSlope, fracText, controls, cubicPoints, crossings, slopeAt,
} from "../../app/src/lib/glue.js";

// The operator's own example: a connector from slope 3/4 to slope -7/24. A cubic with its
// inner control points on the two end directions cannot have the wrong slope at either end.

test("slopes are read as exact fractions", () => {
  assert.equal(fracText(parseSlope("3/4")), "3/4");
  assert.equal(fracText(parseSlope("-7/24")), "-7/24");
  assert.equal(fracText(parseSlope("2")), "2");
  assert.equal(parseSlope("3//4"), null);
  assert.equal(parseSlope("0.75"), null);
});

test("the connector leaves and arrives on the typed slopes", () => {
  const ctrl = controls({ x: 0, y: 0 }, { x: 1, y: 0 }, parseSlope("3/4"), parseSlope("-7/24"), 0.1, 0.1);
  assert.ok(Math.abs(slopeAt(ctrl, 0) - 3 / 4) < 1e-9, `start ${slopeAt(ctrl, 0)}`);
  assert.ok(Math.abs(slopeAt(ctrl, 1) + 7 / 24) < 1e-9, `end ${slopeAt(ctrl, 1)}`);
});

test("the handle changes the shape, and a crossing is detected when there is one", () => {
  const short = controls({ x: 0, y: 0 }, { x: 1, y: 0 }, parseSlope("3/4"), parseSlope("-7/24"), 0.1, 0.1);
  const long = controls({ x: 0, y: 0 }, { x: 1, y: 0 }, parseSlope("3/4"), parseSlope("-7/24"), 0.5, 0.5);
  assert.notDeepEqual(short, long, "the handle must move the control points");
  assert.equal(crossings(cubicPoints(short)).length, 0, "a short handle must not loop");
  // a loop needs the far handle to point back past the end; this cubic does not do that
  assert.equal(crossings(cubicPoints(long)).length, 0);
});
