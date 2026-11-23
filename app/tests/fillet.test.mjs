// The fillet's and the contact's laws, pinned to the Python core's arithmetic.
import assert from "node:assert/strict";
import test from "node:test";
import { Contact } from "../src/lib/contact.ts";
import { arcSegment, cornerFillet, FilletError } from "../src/lib/fillet.ts";

test("a right-angle fillet: the ruler numbers", () => {
  // corner at the origin, edges along +x and +y, radius 2
  const fillet = cornerFillet([10, 0], [0, 0], [0, 10], 2);
  assert.ok(Math.abs(fillet.angle - Math.PI / 2) < 1e-12);
  assert.ok(Math.abs(fillet.tangent - 2) < 1e-12); // r / tan(45°)
  assert.ok(Math.abs(fillet.start[0] - 2) < 1e-12 && Math.abs(fillet.start[1]) < 1e-12);
  assert.ok(Math.abs(fillet.end[0]) < 1e-12 && Math.abs(fillet.end[1] - 2) < 1e-12);
  assert.ok(Math.abs(fillet.centre[0] - 2) < 1e-12 && Math.abs(fillet.centre[1] - 2) < 1e-12);
  assert.ok(Math.abs(fillet.length - Math.PI) < 1e-12); // r·(π − θ)
  // the arc's spans ride the circle exactly at their ends
  const first = fillet.spans[0];
  const last = fillet.spans[fillet.spans.length - 1];
  assert.deepEqual(first.p0, fillet.start);
  assert.deepEqual(last.p3, fillet.end);
  const radial = (p) =>
    Math.hypot(p[0] - fillet.centre[0], p[1] - fillet.centre[1]);
  for (const span of fillet.spans) {
    assert.ok(Math.abs(radial(span.p0) - 2) < 1e-9);
    assert.ok(Math.abs(radial(span.p3) - 2) < 1e-9);
  }
});

test("the fillet refuses what it cannot do", () => {
  assert.throws(() => cornerFillet([10, 0], [0, 0], [0, 10], 0), FilletError);
  // a radius whose tangent exceeds the shorter edge
  assert.throws(() => cornerFillet([1, 0], [0, 0], [0, 10], 5), FilletError);
  // collinear edges
  assert.throws(() => cornerFillet([10, 0], [0, 0], [-10, 0], 1), /double/);
  // doubled back
  assert.throws(() => cornerFillet([10, 0], [0, 0], [0.001, 0], 1), /collinear|double/);
});

test("the arc segment is a clothoid with kd = 0 and curvature ±1/r", () => {
  const fillet = cornerFillet([10, 0], [0, 0], [0, 10], 2);
  const { anchor, segment } = arcSegment(fillet);
  assert.equal(segment.kd, 0);
  assert.ok(Math.abs(Math.abs(segment.kappa0) - 0.5) < 1e-12);
  assert.ok(Math.abs(segment.length - Math.PI) < 1e-12);
  // the anchor is the arc's start with its motion tangent
  assert.ok(Math.abs(anchor.x - fillet.start[0]) < 1e-12);
  const heading = (anchor.angle * 180) / Math.PI;
  assert.ok(Math.abs(Math.abs(heading) - 180) < 1e-6); // clockwise from the circle's bottom
});

test("a contact licenses only its own pair, inside its radius", () => {
  const contact = new Contact([0, 0], 5, "ink/branch", "ink/trunk");
  assert.equal(contact.allows([1, 1], "ink/branch", "ink/trunk"), true);
  assert.equal(contact.allows([1, 1], "ink/trunk", "ink/branch"), true); // order-blind
  assert.equal(contact.allows([6, 0], "ink/branch", "ink/trunk"), false); // outside
  assert.equal(contact.allows([1, 1], "ink/branch", "other"), false); // wrong pair
  assert.throws(() => new Contact([0, 0], 0), /radius must be positive/);
});

test("a one-sided contact trusts any second name at its point", () => {
  const contact = new Contact([0, 0], 2, "ink/branch");
  assert.equal(contact.allows([0, 0], "ink/branch", "ink/trunk"), true);
  assert.equal(contact.allows([0, 0], "ink/other", "ink/trunk"), false);
});
