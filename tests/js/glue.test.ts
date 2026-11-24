import test from "node:test";
import assert from "node:assert/strict";
import {
  parseSlope, fracText, controls, cubicPoints, crossings, slopeAt,
  quinticControls, endConditions,
} from "../../app/src/lib/glue.ts";

// The operator's own example: a connector from slope 3/4 to slope -7/24. A cubic with its
// inner control points on the two end directions cannot have the wrong slope at either end.

test("slopes are read as exact fractions", () => {
  assert.equal(fracText(parseSlope("3/4")), "3/4");
  assert.equal(fracText(parseSlope("-7/24")), "-7/24");
  assert.equal(fracText(parseSlope("2")), "2");
  assert.equal(parseSlope("3//4"), null);
  assert.equal(parseSlope("0.75"), null);
});

test("the cubic connector leaves and arrives on the typed slopes", () => {
  const ctrl = controls({ x: 0, y: 0 }, { x: 1, y: 0 }, parseSlope("3/4"), parseSlope("-7/24"), 0.1, 0.1);
  assert.ok(ctrl);
  assert.ok(Math.abs(slopeAt(ctrl, 0) - 3 / 4) < 1e-9, `start ${slopeAt(ctrl, 0)}`);
  assert.ok(Math.abs(slopeAt(ctrl, 1) + 7 / 24) < 1e-9, `end ${slopeAt(ctrl, 1)}`);
});

test("the handle changes the shape, and a crossing is detected when there is one", () => {
  const short = controls({ x: 0, y: 0 }, { x: 1, y: 0 }, parseSlope("3/4"), parseSlope("-7/24"), 0.1, 0.1);
  const long = controls({ x: 0, y: 0 }, { x: 1, y: 0 }, parseSlope("3/4"), parseSlope("-7/24"), 0.5, 0.5);
  assert.ok(short && long);
  assert.notDeepEqual(short, long, "the handle must move the control points");
  assert.equal(crossings(cubicPoints(short)).length, 0, "a short handle must not loop");
  assert.equal(crossings(cubicPoints(long)).length, 0);
});

test("the quintic connector is G3: all six end conditions at 1e-9", () => {
  // A stated case: the operator's two slopes, a nonzero curvature and rate at each end.
  const targets = { slope0: 3 / 4, slope1: -7 / 24, kappa0: 0.5, kappa1: -0.25, rate0: 0.1, rate1: -0.2 };
  const ctrl = quinticControls({ x: 0, y: 0 }, { x: 1, y: 0.1 },
    parseSlope("3/4"), parseSlope("-7/24"),
    { h0: 0.4, h1: 0.4, kappa0: 0.5, kappa1: -0.25, dkappa0: 0.1, dkappa1: -0.2 });
  assert.ok(ctrl && ctrl.length === 6);
  const c = endConditions(ctrl);
  const close = (actual: number, target: number, name: string) =>
    assert.ok(Math.abs(actual - target) < 1e-9, `${name}: ${actual} vs ${target}`);
  close(c.start.slope, targets.slope0, "start slope");
  close(c.end.slope, targets.slope1, "end slope");
  close(c.start.kappa, targets.kappa0, "start curvature");
  close(c.end.kappa, targets.kappa1, "end curvature");
  close(c.start.rate, targets.rate0, "start curvature rate");
  close(c.end.rate, targets.rate1, "end curvature rate");
});

test("the quintic with zero targets leaves both ends straight", () => {
  const ctrl = quinticControls({ x: 0, y: 0 }, { x: 1, y: 0 }, parseSlope("0"), parseSlope("0"),
    { h0: 0.3, h1: 0.3 });
  assert.ok(ctrl);
  const c = endConditions(ctrl);
  assert.ok(Math.abs(c.start.kappa) < 1e-12);
  assert.ok(Math.abs(c.end.kappa) < 1e-12);
  assert.ok(Math.abs(c.start.rate) < 1e-12);
  assert.ok(Math.abs(c.end.rate) < 1e-12);
});
