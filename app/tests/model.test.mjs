// The design model's TypeScript port, pinned to the Python core.
//
// curve_lab/model.py is the reference. The laws under test:
//   - a design needs a segment, a positive length, a finite corner;
//   - the JSON a Python design writes loads here unchanged, and back;
//   - an empty segments list is refused before anything is drawn;
//   - a G1 design keeps its flag (curvature jumps are the fit, not a fault).
import assert from "node:assert/strict";
import test from "node:test";
import { Design, Segment } from "../src/lib/model.ts";

test("a design needs at least one segment", () => {
  assert.throws(() => new Design({ segments: [] }), /at least one segment/);
});

test("segment validation follows the Python refusals", () => {
  assert.throws(() => new Segment(1, 0), /length must be positive/);
  assert.throws(() => new Segment(1, -2), /length must be positive/);
  assert.throws(() => new Segment(1, 2, Number.POSITIVE_INFINITY), /kappa0/);
  assert.throws(() => new Segment(1, 2, 0, Number.NaN), /corner/);
  const segment = new Segment(2, 3, null, 0.5);
  assert.equal(segment.kappaEnd(1), 7);
  assert.deepEqual(segment.toDict(), { kd: 2, length: 3, kappa0: null, corner: 0.5 });
});

test("a Python-written design loads unchanged and round-trips", () => {
  // the dict shape curve_lab/model.py writes (to_dict)
  const pythonDesign = {
    name: "swan-line",
    anchor: { x: 1, y: -2, angle: 0.25 },
    segments: [
      { kd: 0.5, length: 2, kappa0: 0 },
      { kd: -0.25, length: 1.5, kappa0: null },
    ],
    offsets: [1, -1],
    stroke: 0.75,
  };
  const design = Design.fromDict(pythonDesign);
  assert.equal(design.name, "swan-line");
  assert.equal(design.segments[1].kappa0, null);
  assert.deepEqual(design.toDict(), pythonDesign);
  // through the JSON text too
  const again = Design.fromJson(design.toJson());
  assert.deepEqual(again.toDict(), pythonDesign);
});

test("the g1 flag survives only when set", () => {
  const plain = new Design({ segments: [new Segment(1, 1)] });
  assert.equal(Object.hasOwn(plain.toDict(), "g1"), false);
  const g1 = new Design({ segments: [new Segment(1, 1)], g1: true });
  assert.equal(g1.toDict().g1, true);
});

test("fromPieces reads the backend's keys", () => {
  const design = Design.fromPieces([
    { x0: 0, y0: 0, theta0: 0, kd: 1, length: 2, k0: 0 },
    { x0: 2, y0: 0, theta0: 1, kd: 0.5, length: 1, kappa0: null, corner: 0.1 },
  ]);
  assert.equal(design.segments.length, 2);
  assert.equal(design.segments[0].kappa0, 0);
  assert.equal(design.segments[1].kappa0, null);
  assert.deepEqual(design.anchor, { x: 0, y: 0, angle: 0 });
});

test("stroke must be positive", () => {
  assert.throws(
    () => new Design({ segments: [new Segment(1, 1)], stroke: 0 }),
    /stroke width must be positive/,
  );
});
