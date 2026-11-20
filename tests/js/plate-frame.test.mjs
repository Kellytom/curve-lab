import test from "node:test";
import assert from "node:assert/strict";
import { turn, frame } from "../../scripts/lib/plate-frame.mjs";

test("the plate puts +y up", () => {
  const { project } = frame(-1, 1, -1, 1, 3000);
  const low = project([0, -1])[1];
  const high = project([0, 1])[1];
  assert.ok(high < low, `a larger y must be higher in the image (${high} < ${low})`);
});

test("a 45° turn is clockwise on screen, like the desk", () => {
  const [[x, y]] = turn([[1, 0]], 45);
  assert.ok(x > 0 && y < 0, `(1,0) turned 45° lands down-right, got (${x}, ${y})`);
  const [[bx, by]] = turn([[1, 0]], -45);
  assert.ok(bx > 0 && by > 0, `(1,0) turned −45° lands up-right, got (${bx}, ${by})`);
});

test("the canvas long side is the requested size", () => {
  const { pxW, pxH } = frame(-2, 2, -1, 1, 3000);
  assert.equal(Math.max(pxW, pxH), 3000);
});
